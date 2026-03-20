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
                    config[key.strip()] = val.strip()

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
        print(result.stderr)
        sys.exit(1)
    return result


def build_zip(version):
    """Monta o arquivo .zip mantendo a estrutura de subpastas do projeto."""
    zip_name = f"notebooklm_claude_v{version}.zip"

    # Estrutura: (caminho_local, caminho_dentro_do_zip)
    files = [
        (f"studio/notebooklm_studio_v{version}.html",    f"studio/notebooklm_studio_v{version}.html"),
        (f"guia/guia_notebooklm_claude_v{version}.html", f"guia/guia_notebooklm_claude_v{version}.html"),
        ("colab/servidor_colab.py",                       "colab/servidor_colab.py"),
        ("README.md",                                     "README.md"),
        ("CHANGELOG.md",                                  "CHANGELOG.md"),
        (".gitignore",                                    ".gitignore"),
        ("release.py",                                    "release.py"),
    ]

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

    size_kb = os.path.getsize(zip_name) // 1024
    print(f"   → {zip_name} ({size_kb} KB)")
    return zip_name


def git_commit_push(version, description):
    """Commita todos os arquivos modificados e faz push."""
    run("git add .")
    run(f'git commit -m "feat: v{version} — {description}"')
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


def read_changelog_entry(version):
    """Lê as notas da versão do CHANGELOG.md."""
    if not os.path.exists("CHANGELOG.md"):
        return f"Versão {version}"

    with open("CHANGELOG.md", "r", encoding="utf-8") as f:
        content = f.read()

    start = content.find(f"## v{version}")
    if start == -1:
        return f"Versão {version}"

    end = content.find("\n## ", start + 1)
    block = content[start:end].strip() if end != -1 else content[start:].strip()
    lines = block.split("\n")[1:]
    return "\n".join(lines).strip()


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
    notes = read_changelog_entry(version)
    release_body = f"## O que mudou\n\n{notes}\n\n---\n\nBaixe o arquivo zip abaixo para usar o Studio e o Guia."

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
