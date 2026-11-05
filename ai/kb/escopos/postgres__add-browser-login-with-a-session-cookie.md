---
id: postgres/add-browser-login-with-a-session-cookie
nome: Banco do nujabes e usuário sem superpoder para o ichiro (issue #48)
areas: [dados, auth, infra]
---
## Pedido (o que a branch entrega; cada item verificável)
1. `postgres/init/create-nujabes-database.sh`: na primeira subida cria o usuário `nujabes`
   (senha `NUJABES_DB_PASSWORD`) e o banco `nujabes`, dono dele.
2. `postgres/init/create-ichiro-user.sh`: cria o usuário `ichiro` (senha `ICHIRO_DB_PASSWORD`),
   sem superusuário nem `BYPASSRLS`, para o RLS valer nas conexões do app (as migrations
   seguem com o usuário do `POSTGRES_USER`).
3. `.env.example` com `NUJABES_DB_PASSWORD` e `ICHIRO_DB_PASSWORD`.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- Volume que já existe não roda os scripts: o mesmo SQL vai uma vez à mão (`psql` no container).
- Decisão (2026-11-03): login por `forward_auth` do Caddy; senha conferida pelo `crypt()` do
  pgcrypto no banco do nujabes; usuários criados à mão no banco por enquanto.

## Fora (vira outra branch)
- Tabelas, rotas e container do nujabes: `nujabes/add-browser-login-with-a-session-cookie`.
- `GRANT` nas tabelas, `owner_id` e policy: `ichiro/add-browser-login-with-a-session-cookie`.
- `/api/auth` e `forward_auth`: `caddy/...`; repasse do usuário: `lonzo/...`; tela: `chimchar/...`.
