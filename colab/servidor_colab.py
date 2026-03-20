# =============================================================================
# NotebookLM + Claude Studio — Servidor Flask para Google Colab
# Desenvolvido por Bruno Ferreira — 2026
# =============================================================================
#
# INSTRUÇÕES DE USO:
#   1. No Colab, crie uma nova célula (+ Código) para cada bloco abaixo
#   2. Execute célula por célula, na ordem indicada
#
# CÉLULA 1 — Instalar dependências
# ---------------------------------
# !pip install notebooklm-py flask flask-cors pyngrok requests -q
# print("✅ Dependências instaladas!")
#
# CÉLULA 2 — Upload das credenciais
# -----------------------------------
# import os, json
# from google.colab import files
# print("Selecione o arquivo storage_state.json do seu computador:")
# uploaded = files.upload()
# filename = list(uploaded.keys())[0]
# with open('/content/storage_state.json', 'wb') as f:
#     f.write(uploaded[filename])
# print("✅ Credenciais carregadas em /content/storage_state.json")
#
# CÉLULA 3 — Servidor Flask (este arquivo)
# ------------------------------------------
# Cole todo o conteúdo abaixo em uma nova célula e execute.
# =============================================================================

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pyngrok import ngrok
import subprocess, requests, os, time, json, datetime

app = Flask(__name__)
CORS(app, origins="*")

AUTH_FILE   = '/content/storage_state.json'
CONTENT_DIR = '/content/'

# ── Opção alternativa: carregar credenciais do Google Drive ────────────────
# Útil para evitar reupload manual a cada sessão.
# Salve o storage_state.json no Drive e cole o ID do arquivo abaixo.
#
# import gdown
# DRIVE_FILE_ID = 'SEU_ID_DO_ARQUIVO_NO_DRIVE'
# gdown.download(id=DRIVE_FILE_ID, output=AUTH_FILE, quiet=True)
# print("✅ Credenciais carregadas do Google Drive")

# ── Verificação de credenciais ────────────────────────────────────────────
if not os.path.exists(AUTH_FILE):
    raise FileNotFoundError(
        f"\n\n❌ CREDENCIAIS NÃO ENCONTRADAS!\n"
        f"Arquivo esperado em: {AUTH_FILE}\n"
        f"Execute a Célula 2 para fazer o upload do storage_state.json."
    )

print("✅ Credenciais encontradas.")


# ── Função principal de execução com retry automático ────────────────────
# Timeouts diferenciados por tipo de comando
TIMEOUTS = {
    'generate': 600,   # até 10 min — geração de relatórios e podcasts
    'artifact': 600,   # artifact wait pode demorar
    'ask':      120,   # perguntas respondem rápido
    'default':  180,   # outros comandos
}

def get_timeout(cmd):
    for prefix, seconds in TIMEOUTS.items():
        if cmd.strip().startswith(prefix):
            return seconds
    return TIMEOUTS['default']


def run_notebooklm(cmd, retries=3, delay=30):
    """
    Executa um comando notebooklm-py com retry automático e timeout por tipo.
    Tenta até 3 vezes em caso de rate limit do Google (GENERATION_FAILED).
    """
    with open(AUTH_FILE, 'r') as f:
        auth_content = f.read().strip()

    env = os.environ.copy()
    env['NOTEBOOKLM_AUTH_JSON'] = auth_content
    timeout = get_timeout(cmd)

    for attempt in range(retries):
        result = subprocess.run(
            f'notebooklm {cmd}',
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env
        )
        # Retry em rate limit do Google
        if result.returncode != 0 and 'GENERATION_FAILED' in (result.stdout + result.stderr):
            if attempt < retries - 1:
                wait = delay * (attempt + 1)
                print(f"⚠ Rate limit detectado. Aguardando {wait}s antes de tentar novamente...")
                time.sleep(wait)
                continue
        return result

    return result


# ── Endpoints ────────────────────────────────────────────────────────────

LOG_FILE = '/content/server_log.jsonl'

def write_log(entry):
    """Salva entrada de log em JSONL — nunca interrompe a execução."""
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as lf:
            lf.write(json.dumps(entry, ensure_ascii=False) + '\n')
    except Exception:
        pass


@app.route('/execute', methods=['POST'])
def execute():
    """Executa um comando notebooklm-py e retorna stdout/stderr."""
    cmd = request.json.get('command', '')
    t0 = time.time()
    try:
        result = run_notebooklm(cmd)
        write_log({'ts': datetime.datetime.now().isoformat(), 'cmd': cmd,
                   'rc': result.returncode, 'duration': round(time.time()-t0, 2), 'error': None})
        return jsonify({'stdout': result.stdout, 'stderr': result.stderr,
                        'returncode': result.returncode})
    except Exception as e:
        write_log({'ts': datetime.datetime.now().isoformat(), 'cmd': cmd,
                   'rc': -1, 'duration': round(time.time()-t0, 2), 'error': str(e)})
        return jsonify({'error': str(e)}), 500


@app.route('/logs', methods=['GET'])
def get_logs():
    """Retorna as últimas N entradas do log (padrão: 50)."""
    n = int(request.args.get('n', 50))
    if not os.path.exists(LOG_FILE):
        return jsonify({'logs': []})
    with open(LOG_FILE, 'r', encoding='utf-8') as lf:
        lines = [l.strip() for l in lf if l.strip()]
    entries = []
    for line in lines[-n:]:
        try:
            entries.append(json.loads(line))
        except Exception:
            pass
    return jsonify({'logs': entries})


@app.route('/health', methods=['GET'])
def health():
    """Verificação de saúde — usado pelo keep-alive do Studio."""
    return jsonify({'status': 'ok'})


@app.route('/download/<path:filename>', methods=['GET'])
def download(filename):
    """Serve arquivos gerados pelo notebooklm-py (relatórios, podcasts)."""
    try:
        return send_from_directory(CONTENT_DIR, filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': f'Arquivo não encontrado: {filename}'}), 404


@app.route('/save-history', methods=['POST'])
def save_history():
    """Salva o histórico de comandos do Studio em /content/nlm_history.json."""
    data = request.json.get('history', [])
    path = '/content/nlm_history.json'
    with open(path, 'w') as f:
        json.dump({
            'version': '2.6',
            'synced': datetime.datetime.now().isoformat(),
            'commands': data
        }, f, indent=2)
    return jsonify({'ok': True, 'path': path, 'count': len(data)})


# ── Configuração do ngrok ─────────────────────────────────────────────────
#
# OPÇÃO A — Colab Secrets (recomendada, token não aparece no código):
#   1. Clique no ícone 🔑 na barra lateral esquerda do Colab
#   2. Clique em "Add new secret"
#   3. Name: NGROK_TOKEN   |   Value: seu token do dashboard.ngrok.com
#   4. Ative o toggle "Notebook access"
#
# OPÇÃO B — Direto no código (substitua SEU_TOKEN_AQUI pelo token real):
#   ngrok_token = 'SEU_TOKEN_AQUI'

try:
    from google.colab import userdata
    ngrok_token = userdata.get('NGROK_TOKEN')
    if not ngrok_token:
        raise ValueError("Token vazio nos Secrets")
except Exception:
    ngrok_token = 'SEU_TOKEN_AQUI'  # ← Opção B: cole seu token aqui

# Validação antes de tentar conectar
if ngrok_token == 'SEU_TOKEN_AQUI' or not ngrok_token:
    raise ValueError(
        "\n\n❌ TOKEN DO NGROK NÃO CONFIGURADO!\n"
        "Configure via Colab Secrets (Opção A) ou\n"
        "substitua SEU_TOKEN_AQUI pelo seu token real (Opção B).\n"
        "Obtenha seu token em: https://dashboard.ngrok.com/get-started/your-authtoken"
    )

ngrok.set_auth_token(ngrok_token)
print("✅ Token ngrok configurado.")

# ── Keep-alive: previne desconexão do Colab após 90 min ──────────────────
import threading

url = ngrok.connect(5000)
url_str = url.public_url  # URL limpa, sem o objeto NgrokTunnel

def keep_alive():
    while True:
        time.sleep(25 * 60)  # ping a cada 25 minutos
        try:
            requests.get(url_str + '/health', timeout=5)
        except Exception:
            pass

threading.Thread(target=keep_alive, daemon=True).start()

# ── Exibe a URL uma única vez ─────────────────────────────────────────────
print(f"\n{'━'*50}")
print(f"✅ Servidor ativo!")
print(f"📡 URL para colar no Studio: {url_str}")
print(f"🕑 Keep-alive ativo — ping a cada 25 min")
print(f"{'━'*50}\n")

app.run(port=5000)
