# 📓 NotebookLM + Claude Studio

Terminal visual para integrar o **NotebookLM** (análise de documentos com citações) ao **Claude** (interpretação, redação e elaboração) — via notebooklm-py, Google Colab e ngrok.

---

## O que é isso?

O NotebookLM processa centenas de documentos e responde perguntas com citações precisas das fontes. O Claude interpreta, estrutura argumentos e redige conteúdo complexo. Este projeto conecta os dois:

```
Studio HTML → ngrok → Flask/Colab → notebooklm-py → NotebookLM Google
```

Você usa o **Studio** para consultar o NotebookLM, e o botão **Contexto** transfere tudo para o Claude com um clique — notebook ativo, fontes carregadas e todas as respostas da sessão.

---

## Arquivos incluídos no pacote

```
notebooklm-studio/
├── studio/
│   └── notebooklm_studio.html   ← Abrir no Chrome
├── guia/
│   └── guia_notebooklm_claude.html ← Guia completo passo a passo
├── colab/
│   └── servidor_colab.py              ← Servidor Flask para o Google Colab
├── README.md
└── CHANGELOG.md
```

---

## Como usar

### 1. Configuração local (uma única vez)

Instale o notebooklm-py e faça login com sua conta Google:

```bash
pip install notebooklm-py playwright
playwright install chromium
notebooklm login
```

O login abre uma janela do Chrome para autenticação no Google. Após concluir, o arquivo de credenciais é salvo automaticamente em:

- **Windows:** `%USERPROFILE%\.notebooklm\storage_state.json`
- **Mac/Linux:** `~/.notebooklm/storage_state.json`

### 2. Google Colab

1. Acesse [colab.research.google.com](https://colab.research.google.com) e crie um novo notebook
2. Crie uma célula (botão **+ Código**) e execute o script de setup — instruções detalhadas estão no Guia
3. Configure o token do ngrok via **Colab Secrets** (ícone 🔑 na barra lateral esquerda)
4. Execute a célula do `servidor_colab.py` — ela exibe a URL pública no formato `https://xxxx.ngrok-free.app`

### 3. Studio

1. Abra `studio/notebooklm_studio.html` no Chrome
2. Cole a URL do ngrok e clique em **Conectar**
   - O Studio verifica as credenciais automaticamente — se expiradas, exibe instruções de renovação antes de liberar o acesso
   - Se houver uma versão mais recente disponível, um aviso aparece no terminal após a conexão
3. Use a paleta lateral para executar comandos ou digite diretamente no terminal

### 4. Transferir contexto para o Claude

1. Execute perguntas no Studio com o comando `ask` — cada resposta do NotebookLM fica salva na sessão
2. Clique no botão **Contexto** na barra superior
3. O Studio coleta automaticamente: notebook ativo, fontes carregadas e todas as respostas de `ask` da sessão
4. Copie o bloco gerado e cole em uma nova conversa no Claude

---

## Principais recursos

- **Paleta de comandos** — execute `list`, `use`, `ask`, `generate`, `source list` e mais com um clique
- **Fila automática** — comandos executam em sequência, sem conflitos
- **Playbooks** — salve sequências de comandos como rotinas de 1 clique; edite, reordene e adicione comandos a qualquer momento
- **Histórico persistente** — salvo no navegador, sobrevive a reinicializações do Colab; exportar/importar JSON
- **Contexto inteligente** — captura respostas de `ask` limpas (sem ruído de terminal), fontes e metadados do notebook
- **Verificação de credenciais** — detecta expiração antes de conectar e antes de gerar contexto
- **Verificação de atualizações** — alerta sobre nova versão ao conectar
- **PWA** — instalável como app nativo no desktop e mobile
- **Painel Debug** — últimos comandos com duração, código de retorno e JSON bruto

---

## Requisitos

- Python 3.8+ instalado localmente
- Conta Google (para NotebookLM e Colab)
- Token ngrok gratuito — [dashboard.ngrok.com](https://dashboard.ngrok.com)
- Chrome ou Edge (para o Studio)

---

## Guia completo

Abra o arquivo `guia/guia_notebooklm_claude.html` no navegador para instruções detalhadas de instalação, configuração, uso diário, playbooks e transferência de contexto.

---

Desenvolvido por **Bruno Ferreira** — 2026
