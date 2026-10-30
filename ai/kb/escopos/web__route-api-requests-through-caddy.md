---
id: web/route-api-requests-through-caddy
nome: Tirar o proxy /api do Vite, agora no Caddy (issue #16, PR 2 de 2)
areas: [cliente-api, infra]
---
## Pedido (o que a branch entrega; cada item verificável)
1. `vite.config.ts` sem `server.proxy`; o `api.ts` segue chamando `/api/notes` (URL relativa).
2. Por `https://notes.localhost`, `/api/notes` → 200 e o reload do Vite passa pelo Caddy (WebSocket 101).
3. Versão do web 0.4.0 → 0.5.0.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- Sai da branch `caddy/put-caddy-with-local-tls-in-front-of-the-server` (PR 1 de 2).
- Reload: o cliente do Vite usa a porta da página quando `hmrPort` é `null`, então não precisa de `server.ws.clientPort` (card `ai/kb/libs/vite.md`).

## Fora (vira outra branch)
- `make dev` (Vite no host) fica sem API: só o compose tem o Caddy.
- `/api/docs` do FastAPI atrás do prefixo (`root_path`): branch do `notes`.
