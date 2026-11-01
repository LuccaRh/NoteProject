---
id: caddy/route-each-api-prefix-to-its-service
nome: Um prefixo da API por serviço no Caddy (issue #74, PR 2 de 2)
areas: [infra]
---
## Pedido (o que a branch entrega; cada item verificável)
1. `/api/notes` e `/api/notes/*` → `ichiro:8000`, `/api/chat` e `/api/chat/*` → `lonzo:8000`, os dois sem o `/api`.
2. Outro `/api/*` → 404 do Caddy, nunca o front; o resto → `chimchar:5173`.
3. `curl -N -X POST https://notes.localhost/api/chat` mostra a resposta chegando aos pedaços.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- Sai de `lonzo/answer-chat-questions-through-the-lonzo-service` (PR 1 de 2).
- Matcher nomeado (`@lonzo path ...`) + `uri strip_prefix /api`: o `handle_path /api/chat/*` cortaria o `/api/chat` inteiro.
- O Caddyfile entra no container por bind mount de arquivo: depois de `git switch`/rebase, o Caddy segue com o arquivo antigo até `restart` (o reload não basta).

## Fora (vira outra branch)
- `/api/health` do ichiro deixa de passar pelo Caddy (só `/notes`); o `/docs` atrás do prefixo segue pendente (`root_path`).
