---
id: postgres/create-the-lonzo-database
nome: Banco e usuário do lonzo no Postgres do compose (issue #75)
areas: [dados, infra]
---
## Pedido (o que a branch entrega; cada item verificável)
1. `postgres/init/create-lonzo-database.sh`, montado em `/docker-entrypoint-initdb.d`: na
   primeira subida (volume vazio) cria o usuário `lonzo` (senha `LONZO_DB_PASSWORD` do `.env`)
   e o banco `lonzo`, dono dele.
2. `.env.example` com `LONZO_DB_PASSWORD`.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- Volume que já existe não roda o script: o mesmo SQL vai uma vez à mão (`psql` no container).
- Conferido (2026-11-02) num `postgres:18` descartável: `lonzo` entra no banco `lonzo`.

## Fora (vira outra branch)
- Tabelas, `LONZO_DATABASE_URL` no lonzo, CI do lonzo: `lonzo/keep-chat-conversations-on-the-server`.
