---
tags: [noteproject, servidor, infra]
---
# Testes, CI e qualidade

Todo commit passa no `make check`: ruff, mypy `strict` e pytest de cada serviço Python, mais `tsc` e build do front. O mesmo roda no GitHub Actions em cada PR.

## Testes com banco de verdade

Os testes falam com um [[Postgres]] real (o do compose no PC, um service container na CI), não com mock. Assim [[Row-Level Security|RLS]], CTE recursiva e unicidade são testados de fato.

| Serviço | Como cada teste fica isolado |
|---|---|
| `ichiro` | uma conexão aberta por teste; o `transaction` dos services é trocado (monkeypatch) por um que abre **savepoint** (`begin_nested()`); no fim, rollback de tudo |
| `lonzo` | engine async com `NullPool` (conexão async presa a um event loop); no fim, apaga as linhas criadas desde o início do teste |

- O savepoint por "transação do service" deixa um pedido que falha (rollback) sem estragar o resto do teste.
- O teste conecta como o usuário do app (sem `BYPASSRLS`), então um teste de "outro usuário não vê" (`test_owners.py`) prova a policy.
- Migrations rodam uma vez por sessão de teste (`alembic upgrade head`): a CI começa vazia e testa as migrations também.
- `lonzo`: `FakeIchiro` no lugar da API de notas; o código não muda para facilitar o teste, o teste se adapta (monkeypatch, fake, transport).
- ~180 testes nos três serviços.

## CI

- `.github/workflows/ci.yml`: um job por serviço (`chimchar`, `ichiro`, `lonzo`, `nujabes`) + `tools` (ferramentas do workspace).
- Cada job Python sobe `postgres:18` como service com healthcheck (`pg_isready`), roda o mesmo `postgres/init/create-<serviço>-database.sh` do compose e depois `make check-<serviço>`.
- `POSTGRES_HOST_AUTH_METHOD: trust`: banco descartável, sem senha para guardar no git.
- `uv` com versão fixada (`astral-sh/setup-uv`); front com `npm ci` e cache do npm.
- A `master` só recebe PR (ruleset do GitHub); merge com merge commit.

## Regras como lint

Regras de estilo e de arquitetura que dá para checar por código viraram lint (`ai/np lint`, W01–W25), não instrução escrita: camadas (router não chama repository), commit por camada, docstring em todo `def`, 80 colunas, código em inglês, prompt fora do Python, versão do serviço subida na branch.

## Se perguntarem

- **"Por que não SQLite em memória nos testes?"** RLS, `uuidv7()`, `NULLS NOT DISTINCT`, full-text e CTE são do Postgres; testar em outro banco não provaria nada disso.
- **"Testes lentos?"** Savepoint é barato (sem recriar banco); o custo é ter Postgres de pé, resolvido pelo compose e pelo service da CI.
