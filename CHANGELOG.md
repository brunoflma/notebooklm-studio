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
