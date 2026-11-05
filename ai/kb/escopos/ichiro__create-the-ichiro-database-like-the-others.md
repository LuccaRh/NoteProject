---
id: ichiro/create-the-ichiro-database-like-the-others
nome: Banco do ichiro como os outros, com migrator e .env organizado (sem issue, pedido na sessão)
areas: [dados, infra]
---
## Pedido (o que a branch entrega; cada item verificável)
1. `postgres/init/create-ichiro-database.sh` cria o banco `ichiro`, o usuário `ichiro` (só
   linhas) e o `ichiro_migrator` (dono das tabelas), com `POSTGRES_DB=postgres`.
2. `.env` e `.env.example` agrupados por serviço; `DATABASE_URL` vira `ICHIRO_MIGRATION_URL`.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
Saiu da branch `chimchar/disable-the-login-button-until-the-form-is-valid`: o W13 acusa
`apps/chimchar` até ela entrar na `master`. `Makefile`, CI, `migrations/env.py` e README
acompanham. Lonzo e nujabes têm branches próprias em cima desta.

## Fora (vira outra branch)
- `env_file: .env` do ichiro no compose (entrega todos os segredos ao container).
