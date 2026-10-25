---
pacote: alembic
versao: 1.20.1
fonte: apps/notes/.venv/lib/python3.14/site-packages/alembic/
areas: [dados]
---
# alembic — migrations do Postgres

Card destilado do código instalado (fonte acima, linhas citadas). Versão mudou → `./np lint`
avisa; reconfira as linhas antes de confiar no card. Junto: sqlalchemy 2.1.6, psycopg 3.3.6.

## Comandos (`command.py`)

| CLI | Função | Faz |
|---|---|---|
| `alembic init <pasta>` | `init` (:39), `template="generic"` | cria `alembic.ini` + `<pasta>/env.py`, `script.py.mako`, `versions/` |
| `alembic init -t pyproject <pasta>` | idem, template `pyproject` | config no `pyproject.toml` em vez do `alembic.ini` |
| `alembic revision -m "<msg>"` | `revision` (:191) | arquivo novo em `versions/`, com `upgrade()`/`downgrade()` vazios |
| `alembic upgrade head` | `upgrade` (:446) | aplica até a última; grava a atual em `alembic_version` |
| `alembic downgrade -1` | `downgrade` (:490) | desfaz a última |

Templates disponíveis: `templates/` (generic, async, multidb, pyproject, pyproject_async).

## URL do banco (`templates/generic/env.py`)

- O `env.py` lê a URL de `sqlalchemy.url` do `alembic.ini` (:41 offline; :60 online, por
  `engine_from_config(..., prefix="sqlalchemy.")`).
- Para vir do ambiente: `config.set_main_option("sqlalchemy.url", os.environ[...])` no `env.py`
  (`config.py:339`), e nada de senha no `alembic.ini`.
- Driver psycopg 3 na URL: `postgresql+psycopg://` (`sqlalchemy/dialects/postgresql/psycopg.py:88`).

## Operações na migration (`op.pyi`)

- `op.create_table(nome, *colunas)` (:811), colunas `sa.Column(nome, tipo, ...)`.
- `op.drop_table(nome)` (:1075): o `downgrade()` da `create_table`.
- `op.add_column(tabela, sa.Column(...))` (:55) / `op.drop_column(tabela, coluna)` (:970): par de uma coluna nova.
- `op.execute(sql)` (:1125): SQL escrito à mão.

## Tipos de coluna (sqlalchemy 2.1.6)

| Postgres | SQLAlchemy | Fonte |
|---|---|---|
| `UUID` | `sa.Uuid` | `sql/sqltypes.py:3823` |
| `TEXT` | `sa.Text` | `sql/sqltypes.py:327` |
| `BIGINT` | `sa.BigInteger` | `sql/sqltypes.py:468` |
| `BOOLEAN` | `sa.Boolean` | `sql/sqltypes.py:2135` |
| `TIMESTAMPTZ` | `sa.DateTime(timezone=True)` | `sql/sqltypes.py:854` |
| `JSONB` | `postgresql.JSONB` (`sqlalchemy.dialects.postgresql`) | `dialects/postgresql/json.py:240` |

- Chave estrangeira: `sa.ForeignKey("tabela.coluna", ondelete="CASCADE")` (`sql/schema.py:3227`).
- Padrão no banco: `server_default=...` na `sa.Column`; função SQL por `sa.func.now()` (`sql/functions.py:1366`).
