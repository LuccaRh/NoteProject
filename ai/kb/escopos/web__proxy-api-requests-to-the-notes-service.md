---
id: web/proxy-api-requests-to-the-notes-service
nome: Proxy /api do Vite para o serviço notes (issue #64)
areas: [cliente-api]
---
## Pedido (o que a branch entrega; cada item verificável)
1. `server.proxy` no `apps/web/vite.config.ts`: `/api/*` vai ao `notes` como `/*`.
2. Alvo por `API_URL`: `http://notes:8000` no compose (`docker-compose-dev.yml`), `http://localhost:8000` fora dele.
3. `curl localhost:5173/api/health` devolve `{"status":"ok"}` com o compose de pé; `make check` passa.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- Notas `Conceitos/Rede/Proxy de desenvolvimento`, `Conceitos/Rede/CORS`, `Conceitos/Rede/Reverse proxy` e o mapa de conceitos.

## Fora (vira outra branch)
- Cliente da API, lista de notas e editor (#62, branch `web/list-create-and-edit-notes-in-the-editor`, feita em cima desta).
- Servir o build pelo servidor (#47) e o reverse proxy de produção (Caddy, #16).
