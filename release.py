#!/usr/bin/env python3
"""
release.py — Script de publicação automática
NotebookLM + Claude Studio

Uso:
    python release.py <versão> "<descrição>"
    python release.py 2.13 "Melhorias no sistema"

O que faz automaticamente:
    1. Monta o .zip com os arquivos da versão
    2. git add, commit e push
    3. Cria a release no GitHub via API
    4. Faz upload do .zip como anexo da release

──────────────────────────────────────────────────────────────
CONFIGURAÇÃO DO TOKEN (faça uma única vez, nunca edite aqui)
──────────────────────────────────────────────────────────────

O token do GitHub NUNCA deve ser escrito neste arquivo —
ele ficaria visível no git e seria bloqueado pelo GitHub.

Opção A — Arquivo .github_config (recomendado para uso local):

  Crie o arquivo .github_config na mesma pasta do release.py
  com o seguinte conteúdo (sem aspas):

      GITHUB_USER=seu-usuario
      GITHUB_REPO=notebooklm-studio
      GITHUB_TOKEN=ghp_xxxxxxxxxxxx

  Este arquivo está no .gitignore — nunca será commitado.

Opção B — Variáveis de ambiente:

  Windows (PowerShell, válido na sessão atual):
      $env:GITHUB_USER  = "seu-usuario"
      $env:GITHUB_REPO  = "notebooklm-studio"
      $env:GITHUB_TOKEN = "ghp_xxxxxxxxxxxx"

  Para tornar permanente no Windows:
      [Environment]::SetEnvironmentVariable("GITHUB_TOKEN","ghp_xxx","User")

  Mac/Linux:
      export GITHUB_USER="seu-usuario"
      export GITHUB_REPO="notebooklm-studio"
      export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"

Como criar o token:
    1. Acesse https://github.com/settings/tokens
    2. "Generate new token (classic)"
    3. Marque a permissão: repo (acesso completo)
    4. Clique em "Generate token" e salve o valor no .github_config
──────────────────────────────────────────────────────────────
"""

import os
import sys
import json
import zipfile
import subprocess
import urllib.request
import urllib.error


def load_config():
    """
    Carrega GITHUB_USER, GITHUB_REPO e GITHUB_TOKEN.
    Prioridade: variáveis de ambiente > arquivo .github_config
    Nunca lê valores hardcoded neste script.
    """
    config = {}

    # Tenta ler arquivo .github_config local (gitignored)
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".github_config")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key, _, val = line.partition("=")
                    val = val.strip().strip('"').strip("'")
                    config[key.strip()] = val

    # Variáveis de ambiente sobrescrevem o arquivo
    for key in ("GITHUB_USER", "GITHUB_REPO", "GITHUB_TOKEN"):
        if os.environ.get(key):
            config[key] = os.environ[key]

    return config


def validate_config(config):
    missing = [k for k in ("GITHUB_USER", "GITHUB_REPO", "GITHUB_TOKEN") if not config.get(k)]
    if missing:
        print("\n❌ Configuração incompleta. Faltam: " + ", ".join(missing))
        print("\nCrie o arquivo .github_config na pasta do projeto com:")
        print("   GITHUB_USER=seu-usuario")
        print("   GITHUB_REPO=notebooklm-studio")
        print("   GITHUB_TOKEN=ghp_xxxxxxxxxxxx")
        print("\nLeia as instruções completas no topo deste script.")
        sys.exit(1)


def log(msg, icon="→"):
    print(f"\n{icon} {msg}")


def run(cmd, check=True):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"\n❌ Erro ao executar: {cmd}")
        if result.stdout.strip():
            print(result.stdout)
        if result.stderr.strip():
            print(result.stderr)
        sys.exit(1)
    return result


def build_zip(version):
    """
    Monta o arquivo .zip com os arquivos que o usuário precisa para usar o projeto.
    Os HTMLs têm nomes fixos (sem versão no filename) — cada release substitui
    o arquivo anterior automaticamente, sem deixar versões antigas na pasta.
    release.py e .gitignore são ferramentas do repositório — não entram no zip.
    """
    zip_name = f"notebooklm_claude_v{version}.zip"

    # Nomes fixos: o arquivo sempre se chama o mesmo, independente da versão
    # A versão fica visível dentro do arquivo (título, badge, STUDIO_VERSION)
    files = [
        ("studio/notebooklm_studio.html",    "studio/notebooklm_studio.html"),
        ("guia/guia_notebooklm_claude.html",  "guia/guia_notebooklm_claude.html"),
        ("colab/servidor_colab.py",           "colab/servidor_colab.py"),
        ("README.md",                         "README.md"),
        ("CHANGELOG.md",                      "CHANGELOG.md"),
    ]

    # Allowlist: qualquer arquivo fora desta lista aborta o release
    ALLOWED_IN_ZIP = {
        "studio/notebooklm_studio.html",
        "guia/guia_notebooklm_claude.html",
        "colab/servidor_colab.py",
        "README.md",
        "CHANGELOG.md",
    }

    missing = [src for src, _ in files if not os.path.exists(src)]
    if missing:
        print(f"\n❌ Arquivos não encontrados:")
        for f in missing:
            print(f"   {f}")
        print(f"\nVerifique se os HTMLs estão nas pastas corretas com o número de versão correto.")
        sys.exit(1)

    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zf:
        for src, dest in files:
            zf.write(src, dest)
            print(f"   + {dest}")

    # Validação: inspeciona o zip gerado e aborta se houver arquivo fora da allowlist
    with zipfile.ZipFile(zip_name, "r") as zf:
        names = set(zf.namelist())
    unexpected = names - ALLOWED_IN_ZIP
    if unexpected:
        os.remove(zip_name)
        print(f"\n❌ ABORTADO — o zip contém arquivos não autorizados:")
        for f in sorted(unexpected):
            print(f"   {f}")
        print("\nRemova esses arquivos da lista 'files' em build_zip() e tente novamente.")
        sys.exit(1)

    size_kb = os.path.getsize(zip_name) // 1024
    print(f"   → {zip_name} ({size_kb} KB) — validado ✓")
    return zip_name


def git_commit_push(version, description):
    """
    Commita os arquivos do projeto incluindo deleções (arquivos renomeados/removidos).
    Usa git add -A nas pastas do projeto para capturar modificações E deleções.
    Inclui release.py no commit quando ele tiver mudanças (atualização de STUDIO_VERSION etc.).
    Nunca commita .github_config, github.txt ou secrets.txt.
    """

    # Arquivos que NUNCA devem entrar em um commit — verificação de segurança
    NEVER_COMMIT = [".github_config", "github.txt", "secrets.txt"]
    for f in NEVER_COMMIT:
        result = run(f"git ls-files {f}", check=False)
        if result.stdout.strip():
            print(f"\n❌ ABORTADO — '{f}' está sendo rastreado pelo git e contém credenciais.")
            print(f"   Execute: git rm --cached {f}")
            print(f"   Depois reescreva o histórico: git filter-branch --force --index-filter \"git rm --cached --ignore-unmatch {f}\" --prune-empty HEAD")
            print(f"   E force o push: git push origin main --force")
            print(f"   Por fim, revogue e renove o token em: https://github.com/settings/tokens")
            sys.exit(1)

    # git add -A nas pastas do projeto captura: novos arquivos, modificações E deleções
    # Isso resolve o caso de arquivos antigos com versão no nome que foram removidos
    for folder in ["studio", "guia", "colab"]:
        if os.path.isdir(folder):
            run(f'git add -A "{folder}"', check=False)

    # Arquivos individuais na raiz
    for f in ["README.md", "CHANGELOG.md"]:
        run(f'git add "{f}"', check=False)

    # release.py entra no commit quando tiver mudanças (ex: nova STUDIO_VERSION)
    # .gitignore também, quando modificado
    for f in ["release.py", ".gitignore"]:
        status_f = run(f"git status --porcelain {f}", check=False)
        if status_f.stdout.strip():
            run(f'git add "{f}"', check=False)

    # Verificar se há algo staged para commitar
    staged = run("git status --porcelain", check=False)
    if not staged.stdout.strip():
        print("   → Nada a commitar — repositório já está atualizado")
    else:
        run(f'git commit -m "release: v{version} — {description}"')

    # Sincronizar com o remoto antes de fazer push — evita rejeição por divergência
    print("   → Sincronizando com o repositório remoto...")
    pull = run("git pull --rebase origin main", check=False)
    if pull.returncode != 0:
        print("\n❌ Erro ao sincronizar com o remoto:")
        if pull.stdout.strip(): print(pull.stdout)
        if pull.stderr.strip(): print(pull.stderr)
        print("\nResolva os conflitos manualmente e execute: git rebase --continue")
        print("Depois rode o release novamente.")
        sys.exit(1)

    run("git push")


def github_api(method, path, data=None, token=None):
    """Chamada genérica à API do GitHub."""
    url = f"https://api.github.com{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"\n❌ Erro na API do GitHub ({e.code}): {e.read().decode()}")
        sys.exit(1)


def upload_asset(upload_url, zip_path, token):
    """Faz upload do .zip como anexo da release."""
    base_url = upload_url.split("{")[0]
    filename = os.path.basename(zip_path)
    url = f"{base_url}?name={filename}"

    with open(zip_path, "rb") as f:
        data = f.read()

    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/zip",
        "Accept": "application/vnd.github+json",
    }
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"\n❌ Erro ao fazer upload do zip ({e.code}): {e.read().decode()}")
        sys.exit(1)


def get_last_published_version(github_user, github_repo, token):
    """Consulta o GitHub para saber qual foi a última versão publicada."""
    try:
        url = f"https://api.github.com/repos/{github_user}/{github_repo}/releases/latest"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            return data.get("tag_name", "").lstrip("v")
    except Exception:
        return None


def compile_changelog(current_version, last_published_version):
    """
    Compila todas as entradas do CHANGELOG entre a última versão publicada
    e a versão atual — inclui todas as versões internas intermediárias.
    """
    if not os.path.exists("CHANGELOG.md"):
        return f"Versão {current_version}"

    with open("CHANGELOG.md", "r", encoding="utf-8") as f:
        content = f.read()

    # Extrair todos os blocos de versão presentes no CHANGELOG
    import re
    pattern = re.compile(r'^## v([\d.]+)', re.MULTILINE)
    matches = list(pattern.finditer(content))

    if not matches:
        return f"Versão {current_version}"

    def ver_tuple(v):
        try:
            return tuple(int(x) for x in v.split('.'))
        except Exception:
            return (0,)

    current_t = ver_tuple(current_version)
    last_t    = ver_tuple(last_published_version) if last_published_version else (0,)

    # Coletar blocos de versões que estão ENTRE last_published (exclusive) e current (inclusive)
    entries = []
    for i, m in enumerate(matches):
        v = m.group(1)
        v_t = ver_tuple(v)
        if last_t < v_t <= current_t:
            start = m.start()
            end   = matches[i+1].start() if i+1 < len(matches) else len(content)
            block = content[start:end].strip()
            # Remove o cabeçalho "## vX.X" da primeira linha
            lines = block.split('\n')[1:]
            entries.append(f"### v{v}\n" + "\n".join(lines).strip())

    if not entries:
        # Fallback: retornar só a versão atual
        start = content.find(f"## v{current_version}")
        if start == -1:
            return f"Versão {current_version}"
        end = content.find("\n## ", start + 1)
        block = content[start:end].strip() if end != -1 else content[start:].strip()
        lines = block.split("\n")[1:]
        return "\n".join(lines).strip()

    return "\n\n".join(entries)


def main():
    if len(sys.argv) < 3:
        print("Uso: python release.py <versão> \"<descrição>\"")
        print('Ex:  python release.py 2.13 "Melhorias no sistema"')
        sys.exit(1)

    config = load_config()
    validate_config(config)

    GITHUB_USER  = config["GITHUB_USER"]
    GITHUB_REPO  = config["GITHUB_REPO"]
    GITHUB_TOKEN = config["GITHUB_TOKEN"]

    version     = sys.argv[1].lstrip("v")
    description = sys.argv[2]
    tag         = f"v{version}"

    print(f"\n{'━'*50}")
    print(f"  Publicando NotebookLM Studio v{version}")
    print(f"  {description}")
    print(f"{'━'*50}")

    log("Montando o arquivo .zip...")
    zip_path = build_zip(version)

    log("Commitando e publicando no GitHub...")
    git_commit_push(version, description)
    print("   → Push concluído")

    log("Criando a release no GitHub...")
    last_version = get_last_published_version(GITHUB_USER, GITHUB_REPO, GITHUB_TOKEN)
    if last_version:
        print(f"   → Última versão publicada: v{last_version}")
    notes = compile_changelog(version, last_version)
    intro = f"Versões incluídas neste release: v{last_version} → v{version}" if last_version else f"v{version}"
    release_body = f"## {intro}\n\n{notes}\n\n---\n\nBaixe o arquivo zip abaixo para usar o Studio e o Guia."

    release = github_api(
        "POST",
        f"/repos/{GITHUB_USER}/{GITHUB_REPO}/releases",
        data={
            "tag_name":   tag,
            "name":       f"v{version} — {description}",
            "body":       release_body,
            "draft":      False,
            "prerelease": False,
        },
        token=GITHUB_TOKEN,
    )
    print(f"   → Release criada: {release['html_url']}")

    log("Fazendo upload do .zip...")
    asset = upload_asset(release["upload_url"], zip_path, GITHUB_TOKEN)
    print(f"   → Download disponível em: {asset['browser_download_url']}")

    os.remove(zip_path)
    print(f"   → Zip local removido")

    print(f"\n{'━'*50}")
    print(f"  ✅ v{version} publicada com sucesso!")
    print(f"  🔗 {release['html_url']}")
    print(f"{'━'*50}\n")


if __name__ == "__main__":
    main()
