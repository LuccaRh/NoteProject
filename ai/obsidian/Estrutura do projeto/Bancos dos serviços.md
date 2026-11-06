---
tags: [noteproject, dados, infra]
---
# Bancos dos serviços

Cada serviço tem um banco próprio no mesmo [[Postgres]], com dois usuários, seguindo os papéis de [[Usuários do banco]]. Um serviço não enxerga os dados de outro.

| Serviço | Banco | Migrator (dono) | App |
|---|---|---|---|
| ichiro | `ichiro` | `ichiro_migrator` | `ichiro` |
| lonzo | `lonzo` | `lonzo_migrator` | `lonzo` |
| nujabes | `nujabes` | `nujabes_migrator` | `nujabes` |

![[esquema-do-postgres.drawio.svg]]
*Uma cor por banco; linha tracejada guarda o id de outro banco sem FK, porque o Postgres não liga bancos diferentes.*

O admin (`POSTGRES_USER`) é o quarto papel, com um por servidor: a imagem o cria, e `POSTGRES_DB=postgres` só diz onde os scripts conectam.

## Primeira subida

Com o [[Volume do Docker|volume]] vazio, a imagem cria o admin e roda `postgres/init/create-<serviço>-database.sh`. Cada script cria os dois usuários, o banco com o migrator como dono e o `ALTER DEFAULT PRIVILEGES` que libera as tabelas novas para a app. Com o volume já preenchido, os scripts não rodam, e mudança de usuário é feita à mão no `psql`.

## Variáveis

| Variável | Quem usa | Para quê |
|---|---|---|
| `<SERVIÇO>_DB_PASSWORD` | script de init | senha do usuário da app |
| `<SERVIÇO>_MIGRATOR_PASSWORD` | script de init | senha do migrator |
| `<SERVIÇO>_DATABASE_URL` | app | conexão da app |
| `<SERVIÇO>_MIGRATION_URL` | [[Migration|Alembic]] | conexão do migrator |

- ichiro e lonzo têm [[Row-Level Security]] com `FORCE`, então os migrators deles têm `BYPASSRLS`. O nujabes não tem RLS.
- ⏳ Em produção, a `MIGRATION_URL` entra só no passo que roda o Alembic. No dev ela ainda está no container, para o `exec` do Alembic funcionar.
- A tabela `alembic_version` também recebe os `GRANT`s da app, porque o `ALTER DEFAULT PRIVILEGES` vale para toda tabela do migrator.
