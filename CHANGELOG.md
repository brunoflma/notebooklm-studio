## v2.16
- Nomes de arquivo padronizados e fixos: notebooklm_studio.html e guia_notebooklm_claude.html — sem número de versão no filename. Cada release substitui o arquivo anterior automaticamente, sem deixar versões antigas na pasta
- release.py: build_zip e git_commit_push atualizados para os nomes fixos
- README.md: referências de arquivo atualizadas para os nomes fixos

## v2.15
- Studio: verificação de nova versão ao conectar — consulta o GitHub e exibe alerta não-bloqueante se existir versão mais recente, com link direto para o release
- Studio: constante STUDIO_VERSION centraliza a versão atual no JS — atualizar a cada release
- release.py: git add seletivo — commita apenas os arquivos do projeto (Studio, Guia, servidor, README, CHANGELOG); release.py e .gitignore não entram no commit automático de versão
- release.py: changelog compilado — consulta o GitHub para identificar a última versão publicada e compila todas as entradas intermediárias do CHANGELOG em um único release notes
- release.py: load_config com strip de aspas e espaços nos valores do .github_config
- README.md: revisão completa — informações atualizadas, recursos documentados, seção de contexto corrigida (botão agora chamado "Contexto"), referências de versão genéricas

## v2.14
- release.py: zip validado após geração — se qualquer arquivo fora da allowlist (release.py, .gitignore, etc.) for encontrado dentro do zip, o script aborta, apaga o zip e exibe o arquivo infrator antes de publicar qualquer coisa

## v2.13
- Studio: verificação de credenciais movida para dentro do processo de conexão — o terminal só abre se as credenciais estiverem válidas. Se expiradas, a tela de setup exibe as instruções completas de renovação sem entrar no Studio
- Guia: exemplo do bloco de contexto substituído por dados genéricos fictícios — removidas todas as referências a casos e nomes reais
- release.py: token do GitHub nunca mais hardcoded — lido de arquivo `.github_config` local (gitignored) ou variável de ambiente. Estrutura do zip corrigida para manter subpastas `studio/` e `guia/`
- .gitignore: adicionados `.github_config` e `github.txt` para garantir que credenciais nunca sejam commitadas

## v2.12
- Removida seção "Outros notebooks disponíveis" do bloco de contexto — não agrega ao Claude que trabalha em um caso específico; a troca de notebook é função do Studio
- Eliminada chamada `list --json` interna do showContext — era usada apenas para gerar essa seção, agora desnecessária (uma chamada de rede a menos, contexto mais rápido)
- Contexto agora focado exclusivamente no notebook ativo: dados do caso, fontes carregadas e respostas substantivas da sessão

## v2.11
- Contexto completamente reescrito — filtra comandos operacionais (use, list, status, source list, artifact list, download, generate) que não agregam ao Claude
- Remove tabelas ASCII do CLI (┏━━━, ┃, └──) e linhas de sistema (Continuing conversation, Resumed conversation, Matched:) antes de incluir no bloco
- Inclui apenas respostas de comandos `ask`, formatadas como "Pergunta: ... / [resposta limpa]"
- Seção "Status do servidor" substituída por bloco "Notebook ativo" com dados parseados de forma limpa (nome, ID, data, contagem de fontes)
- Lista de fontes sem a coluna de status técnico ("ready") — apenas os nomes dos documentos
- Notebook ativo é excluído da lista de "Outros notebooks" para evitar duplicação
- Guia: passo 3 da seção "Transferir contexto" atualizado com descrição precisa dos 4 itens coletados e exemplo real do bloco gerado

## v2.10
- Studio: verificação silenciosa de credenciais imediatamente após conectar — exibe alerta e desabilita botão Contexto antes de qualquer comando manual
- Studio: `showContext()` verifica credenciais nos resultados internos de `status`/`list`/`source list` e aborta com modal de renovação se expiradas — elimina o caso de contexto vazio gerado com credencial inválida
- Guia: TOC com offset dinâmico (`toc-wrap.getBoundingClientRect().bottom`) que se adapta a qualquer zoom, tamanho de fonte e redimensionamento de janela
- Guia: TOC atualizado via `requestAnimationFrame` — evita múltiplas recalculações por evento scroll e garante execução após reflow do layout
- Guia: auto-scroll horizontal do nav corrigido com `getBoundingClientRect()` relativo ao nav (era `offsetLeft` relativo ao documento, incorreto quando nav tem scroll)

## v2.9
- Design dos blocos de comando (cmd-lines) corrigido: bloco unificado com borda única, número de linha sutil, botão "copiar" totalmente visível à direita com hover teal, comentários com fundo levemente distinto sem preto puro
- Seção "Transferir contexto" (passo 3) reescrita: explica os 3 passos internos do botão Contexto, destaca a captura de perguntas/respostas da sessão, mostra exemplo real do bloco gerado incluindo seção ask, e adiciona aviso sobre credenciais expiradas

## v2.8
- Contexto ampliado: `showContext()` agora captura toda a sessão do terminal — todos os `ask` executados e seus outputs são incluídos na seção "Perguntas e respostas desta sessão"
- Copiar por linha nos Playbooks do guia: cada comando tem botão de cópia individual; comentários exibidos em itálico sem botão
- Status "Conectado" na barra: substituído texto técnico de keepalive por "Conectado" e "Conectado — HH:MM"
- Edição de playbooks existentes: botão ✎ por playbook abre modal com renomear, reordenar (↑↓), excluir linhas e adicionar comandos novos livres
- Modal de novo playbook também aceita comandos digitados manualmente (não só do histórico)
- Botão Contexto desabilitado enquanto credenciais estiverem expiradas — bloqueia execução e abre modal de renovação

## v2.7
- Fix TOC do guia: substituído `offsetTop + break` por `getBoundingClientRect()` — funciona corretamente em qualquer nível de zoom e em todos os navegadores
- Fix responsividade: novo breakpoint em 960px reduz padding do container e padding dos steps, aliviando quebra prematura de texto em telas médias ou com zoom aumentado
- CSS defensivo: `max-width:none` e `overflow-wrap:break-word` explícitos em `section-desc` e `step-desc`
- Corrigida tabela de histórico no guia: versões v2.4 e v2.5 estavam ausentes; entrada de v2.6 tinha descrição incorreta (descrevia features do v2.4)

## v2.6
- Receitas práticas no guia: petição, dossiê, revisão bibliográfica, análise financeira
- Logs estruturados no servidor (JSONL em /content/server_log.jsonl)
- Timeouts diferenciados por tipo de comando (generate 10min, ask 2min)
- Painel Debug no Studio: últimos comandos com duração, rc, raw JSON e botão copiar
- Modo Playbook na paleta: salve sequências do histórico como rotinas de 1 clique

# Changelog — NotebookLM + Claude Studio

## v2.5
- Separação visual clara por categoria na paleta de comandos (ícone + linha colorida)
- Ordem dos botões reorganizada por prioridade: contexto → histórico → notebook → limpar → ajuda → desconectar
- Botão desconectar destacado em vermelho para evitar cliques acidentais
- Fontes maiores em todo o Studio (terminal, paleta, inputs, status)
- "Conectado" exibido apenas uma vez na barra de status, sem duplicidade
- Instruções do token ngrok aprimoradas no guia (name/value/toggle explícitos)
- URL do ngrok exibe apenas o endereço limpo (sem objeto NgrokTunnel)
- Referências de versão removidas do corpo do guia (mantidas apenas no changelog)
- Rodapé do guia atualizado
- Instruções para botão "+ Código" do Colab adicionadas ao guia

## v2.4
- PWA instalável como app nativo (desktop e mobile)
- Service worker com cache offline do shell
- Correção: SW isolado em try-catch para não quebrar em file://

## v2.3
- Histórico: exportar JSON, importar JSON (merge dedup), sincronizar via Google Drive
- Rota /save-history no servidor Flask

## v2.2
- Fila de comandos serializada: todos os comandos executam em ordem sem conflito
- Badge contador "N na fila" ao lado do título

## v2.1
- Keep-alive automático no servidor Colab (ping a cada 25 minutos)
- Detecção de credenciais expiradas no Studio com alerta vermelho e instruções passo a passo

## v2.0
- Versão major: audit completo, guia e Studio totalmente sincronizados
- Nomenclatura unificada em todos os arquivos

## v1.6
- Busca em tempo real na paleta de comandos
- Histórico persistente de comandos (salvo no localStorage do navegador)
- Switch rápido entre notebooks sem digitar ID
- Notificações ao concluir geração (badge + notificação do sistema)
- Retry automático em rate limits do Google (3x com backoff)
- Token ngrok via Colab Secrets
- Suporte a Google Drive para credenciais
- Cloudflare Tunnel como alternativa gratuita ao ngrok

## v1.5
- Paleta teal (cores suaves em todo o Studio)
- Botão "📋 copiar contexto" para transferir estado ao Claude
- Botão limpar tela sem perder conexão
- Versionamento explícito no título
- Guia com seção de fluxo avançado (transferência de contexto entre conversas)

## v1.4
- Spinner com cronômetro em tempo real durante execução
- Auto artifact wait após generate
- Auto download de relatórios e podcasts após geração concluída

## v1.3
- Modal personalizado substituindo window.prompt
- Fix do comando ask: aspas adicionadas automaticamente

## v1.2
- Paleta de comandos lateral
- Renderização smart de JSON: notebooks e artefatos exibidos como cards clicáveis

## v1.1
- Guia completo criado (instalação, autenticação, Colab, Studio, uso diário)

## v1.0
- Terminal visual básico
- Conexão via ngrok ao Google Colab
- Execução de comandos notebooklm-py
