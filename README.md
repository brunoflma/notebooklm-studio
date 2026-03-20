# 📓 NotebookLM + Claude Studio

Terminal visual para conectar o poder de análise do **Claude** com a capacidade do **NotebookLM** de processar centenas de documentos — via notebooklm-py, Google Colab e ngrok.

---

## O que é isso?

O NotebookLM consegue analisar centenas de documentos e responder com citações precisas. O Claude consegue interpretar, estruturar argumentos e redigir conteúdo complexo. Este projeto conecta os dois: você usa o **Studio** para consultar o NotebookLM e traz os resultados para o Claude elaborar.

```
Studio HTML → ngrok → Flask/Colab → notebooklm-py → NotebookLM Google
```

---

## Arquivos incluídos

```
notebooklm-studio/
├── studio/
│   └── notebooklm_studio_v2.14.html   ← Terminal visual (abrir no Chrome)
├── guia/
│   └── guia_notebooklm_claude_v2.14.html ← Guia completo passo a passo
├── colab/
│   └── servidor_colab.py              ← Servidor Flask para o Google Colab
├── README.md
├── CHANGELOG.md
└── .gitignore
```

---

## Como usar

### 1. Configuração local (uma vez)

```bash
pip install notebooklm-py playwright
playwright install chromium
notebooklm login
```

Isso gera o arquivo `~/.notebooklm/storage_state.json` com suas credenciais do Google.

### 2. Google Colab

1. Abra https://colab.research.google.com e crie um novo notebook
2. Crie células com **+ Código** e execute na ordem:
   - **Célula 1:** instalar dependências (ver comentário no topo de `servidor_colab.py`)
   - **Célula 2:** upload do `storage_state.json`
   - **Célula 3:** colar e executar o conteúdo de `colab/servidor_colab.py`
3. Configure o token do ngrok via **Colab Secrets** (ícone 🔑 na barra lateral)
4. Copie a URL gerada (formato `https://xxxx.ngrok-free.app`)

### 3. Studio

1. Abra `studio/notebooklm_studio_v2.14.html` no Chrome
2. Cole a URL do ngrok e clique em **Conectar**
3. Use a paleta lateral para executar comandos ou digite diretamente

### 4. Transferir contexto para o Claude

Quando quiser levar o estado do projeto para uma conversa no Claude:
1. Clique no botão **📋 copiar contexto** na barra superior do Studio
2. Copie o bloco gerado
3. Abra uma nova conversa no Claude, cole o contexto e anexe o `.md` do relatório

---

## Requisitos

- Python 3.8+ instalado localmente
- Conta Google (NotebookLM + Colab)
- Token ngrok gratuito — https://dashboard.ngrok.com
- Chrome ou Edge (recomendado para o Studio)

---

## Versão atual

**v2.14** — ver [CHANGELOG.md](CHANGELOG.md) para histórico completo.

---

## Desenvolvido por

Bruno Ferreira — 2026
