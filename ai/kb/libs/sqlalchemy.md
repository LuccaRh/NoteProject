---
pacote: sqlalchemy
versao: 2.1.6
fonte: apps/lonzo/.venv/lib/python3.14/site-packages/sqlalchemy/
areas: [dados, servidor]
---
# sqlalchemy — Core async (lonzo)

Card destilado do código instalado (fonte acima, linhas citadas). Versão mudou → `ai/np lint`
avisa; reconfira as linhas. O ichiro usa o Core **síncrono** (`create_engine`, `ichiro/db.py`);
o lonzo usa o **async**, porque o chat responde em streaming.

## Instalar

- O async precisa do extra: `sqlalchemy[asyncio]` (traz `greenlet`; `METADATA:31-32`). Sem ele,
  `create_async_engine` falha ao conectar.

## Engine e transação (`ext/asyncio/engine.py`)

| Uso | Linha | Faz |
|---|---|---|
| `create_async_engine(url)` | :76 | engine com pool; `postgresql+psycopg://` já escolhe o psycopg async (`dialects/postgresql/psycopg.py:40-44`) |
| `async with engine.begin() as conn` | :1069 | conexão + transação: commit no fim do bloco, rollback se levantar |
| `await conn.execute(text(...), {...})` | :612 | mesmo `text()` com `:nome` do Core síncrono |
| `await engine.dispose()` | :1145 | fecha o pool (no `lifespan` do app) |

## Resultado (`engine/result.py`)

- `result.mappings()` (:774) → linhas como dict, prontas para `Model.model_validate(row)`.
- `.one()`, `.one_or_none()` (:1401 no `MappingResult`), `result.scalar_one()` (:1053).

## Armadilhas (conferidas no lonzo, 2026-11-02)

- Conexão do pool fica presa ao event loop em que nasceu; o `TestClient` sem `with` abre um loop
  por pedido → nos testes, engine com `poolclass=NullPool` (`pool/impl.py:279`).
- `jsonb` com `text()`: mandar `json.dumps(...)` e `CAST(:x AS jsonb)`; uma lista Python iria
  como array do Postgres. Na leitura, o psycopg devolve o objeto Python.
- `folder_id = :id` com `None` não acha nada: raiz precisa de `IS NULL`.
