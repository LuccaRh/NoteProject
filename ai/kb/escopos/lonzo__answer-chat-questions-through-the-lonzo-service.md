---
id: lonzo/answer-chat-questions-through-the-lonzo-service
nome: Serviço lonzo responde o chat com regras fixas (issue #74, PR 1 de 2)
areas: [ia, servidor, infra]
---
## Pedido (o que a branch entrega; cada item verificável)
1. `apps/lonzo` (FastAPI) com `GET /health`, no `make check` e na CI.
2. Container próprio no compose de dev; a `ANTHROPIC_API_KEY` só nele, quando a rota de chat usar
   (uma key do ambiente, provisória até o login).
3. `POST /api/chat {question}` (no lonzo, `/chat`): API crua (`anthropic`, Haiku, `max_tokens` baixo),
   regras de um `.md` no system prompt, resposta em SSE com eventos nomeados (`message_start`,
   `text_delta`, `message_end`, `error`). Decidido (2026-11-01): sem Agent SDK e sem `status`
   (só com ferramentas, #77).
4. Versão do lonzo começa em 0.1.0.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- Sai de `ichiro/align-the-uv-version` (#82): mesmo uv 0.13.5 nas imagens e na CI.
- Vault: `IA no projeto/Caminho de uma pergunta`, `Chat com o workspace`.

## Fora (vira outra branch)
- Rota `/api/chat` no Caddy: branch `caddy/...`, PR 2 de 2 da #74. Decidido (2026-11-01): um prefixo
  por recurso, sem pega-tudo (`/api/notes/*` → ichiro, `/api/chat/*` → lonzo); o `handle_path` corta o `/api`.
- `workspace` e `conversation` no body; regras do `.workspace/` vindas do ichiro (#73); conversas no banco do lonzo (#75); tela do chat (#76).
- Key de cada usuário, cifrada no banco do lonzo: depois do login (M2).
