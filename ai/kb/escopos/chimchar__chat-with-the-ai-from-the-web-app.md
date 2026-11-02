---
id: chimchar/chat-with-the-ai-from-the-web-app
nome: Abas no front, aba de chat e criar workspace pelo pop-up (issue #76)
areas: [ui, cliente-api]
---
## Pedido (o que a branch entrega; cada item verificável)
1. Barra de abas: cada aba é uma nota ou um chat; dá para abrir várias e fechar com ×.
   Abrir nota pela árvore abre (ou volta para) a aba dela.
2. Aba de chat: escolhe o workspace (pasta), lista as conversas dele, caixa de pergunta;
   a resposta aparece enquanto é gerada (SSE do `POST /api/chat`); abrir uma conversa
   mostra as mensagens e a próxima pergunta continua nela.
3. Botão "Create workspace": pop-up com a pasta e a descrição, que já vem preenchida com
   um modelo em ordem (objetivo, como responder, fatos fixos, estado, fontes) e diz que
   dá para ir além ou apagar e escrever o próprio; manda `POST /api/chat/workspaces`.
4. `make check-chimchar` passa; conferido no navegador pelo Caddy; versão 0.6.0 → 0.7.0.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- Rotas do lonzo da #75 (`GET /api/chat/conversations`, `/{id}`): a branch sai da
  `lonzo/keep-chat-conversations-on-the-server` e vai para cima da `master` quando ela
  for mergeada.
- `cliente-api` (área do usuário): o Lucca pediu a task inteira pronta (2026-11-02);
  no fim, mostrar onde ler cada parte.

## Fora (vira outra branch)
- Mudança no lonzo ou no ichiro (ex.: rota que lista só as pastas com `.workspace`).
- Markdown renderizado na resposta, abas guardadas entre recargas, evento `status` (#77).
