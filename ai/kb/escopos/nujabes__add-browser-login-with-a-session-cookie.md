---
id: nujabes/add-browser-login-with-a-session-cookie
nome: Serviço nujabes — login por cookie de sessão (issue #48)
areas: [auth, servidor]
---
## Pedido (o que a branch entrega; cada item verificável)
1. `apps/nujabes/` (FastAPI, uv), container no compose, alvo `check-nujabes` no `make check`.
2. Banco `nujabes` com Alembic: `users` (senha pelo `crypt()` do pgcrypto) e `sessions` (hash
   do token, 30 dias). Usuário criado à mão no banco por enquanto.
3. `POST /auth/login` → cookie `session` httpOnly, Secure, SameSite=Lax; `POST /auth/logout`
   apaga a sessão e o cookie; `GET /auth/session` → `{user_id}` + header `X-User-Id`, ou 401
   (é a pergunta do `forward_auth` do Caddy).
4. Testes: login certo/errado, sessão sem cookie, inventada, expirada, logout, token só em hash.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- `.env.example` (`NUJABES_DATABASE_URL`), `docker-compose-dev.yml`, `Makefile`.
- Decisão (2026-11-03): `forward_auth` do Caddy; senha no `crypt()` (o mais simples no código).

## Fora (vira outra branch)
- Banco e usuário no Postgres: `postgres/...`. `/api/auth` e `forward_auth`: `caddy/...`.
- RLS e `owner_id`: `ichiro/...`; repasse do usuário: `lonzo/...`; tela de login: `chimchar/...`.
- Cadastro de usuário (o Lucca faz depois).
