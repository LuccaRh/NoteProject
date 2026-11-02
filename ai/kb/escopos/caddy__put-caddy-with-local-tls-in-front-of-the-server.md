---
id: caddy/put-caddy-with-local-tls-in-front-of-the-server
nome: Caddy com TLS local na frente do dev (issue #16, PR 1 de 2)
areas: [infra]
---
## Pedido (o que a branch entrega; cada item verificável)
1. `caddy/Caddyfile`: `notes.localhost` com `tls internal`; `/api/*` → `notes:8000` sem o `/api`; o resto → `web:5173`.
2. Serviço `caddy` (`caddy:2.11`) no `docker-compose-dev.yml`, só no loopback (80, 443), com volumes `/data` e `/config`.
3. `web` e `notes` sem `ports:`; `web` sem o `API_URL`.
4. `curl -k https://notes.localhost/api/notes` → 200; `/` devolve o `index.html` do Vite; `:8000` e `:5173` fechadas.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- Decisão: vault `Estrutura do projeto/Navegador` ("Quem entrega o front") e `Infra — deploy e operação`.
- `caddy` entra como serviço de branch no W13 (container do compose com config em pasta própria, como `postgres`).

## Fora (vira outra branch)
- Tirar o proxy `/api` do `vite.config.ts`: PR 2, branch `web/route-api-requests-through-caddy`.
- `/api/auth` (#48) e servir o `dist/` em produção (#47).
- Confiar na CA local no navegador: passo manual do usuário.
