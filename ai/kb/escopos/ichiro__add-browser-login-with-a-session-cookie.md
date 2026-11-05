---
id: ichiro/add-browser-login-with-a-session-cookie
nome: Notas com dono, filtradas por RLS (issue #48)
areas: [dados, servidor, auth]
---
## Pedido (o que a branch entrega; cada item verificável)
1. Middleware lê o `X-User-Id` (posto pelo Caddy) numa contextvar; sem ele, 401 (menos
   `/health`).
2. `db.transaction()` grava o usuário na transação (`set_config('app.user_id', ..., true)`); o
   app conecta como `ichiro` (`ICHIRO_DATABASE_URL`), sem superusuário.
3. Migration: `owner_id` (default = usuário da transação), índice, título único por dono,
   policy `notes_owner`, `ENABLE` + `FORCE ROW LEVEL SECURITY`, `GRANT` ao `ichiro`. Notas que
   já existem vão para `alembic -x owner=<id> upgrade head`.
4. Testes: um usuário não vê, não lê, não edita, não apaga nem escreve na pasta do outro;
   mesmo título na raiz de dois usuários; sem `X-User-Id` → 401. Conectado como superusuário,
   3 deles falham (conferido).

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- `.env.example`, `Makefile`, CI (cria o usuário `ichiro` no Postgres do job).
- Nota `Estrutura do projeto/RLS ou filtro em cada consulta`.

## Fora (vira outra branch)
- Usuário `ichiro` no Postgres: `postgres/...`. `forward_auth`: `caddy/...`. Repasse do
  usuário pelo chat: `lonzo/...`.
