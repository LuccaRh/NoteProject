---
tags: [noteproject, servidor]
---
# Criar um serviço Python

Cada API do servidor é um serviço próprio em `apps/<serviço>/`, com pasta, imagem e [[Container|container]] separados ([[Um repo ou vários]]). Esta página é o roteiro que montou o `lonzo` (commits `4300bc4` a `5df653a`), na ordem dos commits; o próximo serviço (`auth`, #48) segue o mesmo caminho. Nos exemplos, `auth` está no lugar do nome do serviço.

## 1. Projeto uv

```bash
cd apps
uv init --python 3.14 auth      # uv 0.13.5: package em src/auth/, [build-system] uv_build
cd auth
uv add 'fastapi[standard]'
uv add --dev ruff mypy pytest
```

- O padrão do `uv init` (conferido no 0.13.5) cria `src/auth/__init__.py`, `pyproject.toml`, `.python-version` e `README.md`, como [[Package Python|package]] instalado no [[venv]]; o porquê do `src/` está em [[API de notas]].
- Do que ele gera, sai o `[project.scripts]` e a função `main()` do `__init__.py`, que fica vazio: quem roda o serviço é o `fastapi dev`.
- A versão começa em `0.1.0`; cada branch que mexe no serviço sobe a minor (lint W11).
- Commit: `Create the auth project with FastAPI` (com o `uv.lock`).

## 2. ruff e mypy no pyproject

```toml
[tool.ruff]
line-length = 80

[tool.ruff.lint]
extend-select = ["E501"]

# Two blank lines between imports and the globals (CLAUDE.md, W16)
[tool.ruff.lint.isort]
lines-after-imports = 2

[tool.mypy]
strict = true
```

Igual ao do `ichiro` e do `lonzo`: 80 colunas, as três partes do arquivo e tudo tipado. Commit: `Configure ruff and mypy for auth`.

## 3. Rota de health e `make check`

```
src/auth/
├── __init__.py
├── main.py              app = FastAPI(...); app.include_router(health.router)
└── routers/health.py    GET /health → {"status": "ok"}
tests/test_health.py
```

No `Makefile`, um alvo por serviço, e o `check` passa a chamar ele:

```make
check: check-chimchar check-ichiro check-lonzo check-auth

check-auth:
	cd apps/auth && uv run ruff check && uv run mypy src tests \
		&& uv run pytest
```

Commits: `Add the auth health endpoint` e `Run the auth checks in make check`. As camadas (`routers/` → `services/` → `clients/` ou `repositories/`) nascem conforme as rotas pedem.

## 4. Container no compose

`apps/auth/Dockerfile.dev`, cópia do do `lonzo`:

```dockerfile
FROM python:3.14-slim
COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /uvx /bin/
WORKDIR /app

# Dependencies first: the layer is reused while the lockfile does not change
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project

COPY . .
RUN uv sync --locked

EXPOSE 8000

CMD ["uv", "run", "fastapi", "dev", "src/auth/main.py", \
     "--host", "0.0.0.0", "--port", "8000"]
```

`.dockerignore` com `.venv`, `__pycache__`, `.mypy_cache`, `.pytest_cache` e `.ruff_cache`. No `docker-compose-dev.yml`, o serviço entra em ordem alfabética (lint W17):

```yaml
    auth:
        build:
            context: ./apps/auth
            dockerfile: Dockerfile.dev
        volumes:
            - ./apps/auth:/app
            - /app/.venv
        environment:
            - AUTH_DATABASE_URL=${AUTH_DATABASE_URL}
        depends_on:
            - postgres
```

- O volume `./apps/auth:/app` faz o `fastapi dev` recarregar a cada arquivo salvo; o `/app/.venv` anônimo impede que a pasta do host apague o [[venv]] da imagem.
- Sem `ports`: só o [[Reverse proxy|Caddy]] fala com o serviço, pela rede do [[Docker Compose|compose]].
- Commit: `Run auth in its own container`. Depois de um `uv add`, `dc up -d --build auth` ([[Comandos do Docker no dev]]).

## 5. Rota no Caddy

```caddy
    @auth path /api/auth /api/auth/*
    handle @auth {
        uri strip_prefix /api
        reverse_proxy auth:8000
    }
```

Antes do `handle /api/*` que responde 404. O serviço vê `/auth/...`, sem o `/api`. É uma branch à parte (`caddy/...`): um serviço por branch.

## 6. Banco próprio e Alembic

Cada serviço tem o seu banco no mesmo [[Postgres]], com usuário próprio, e as suas [[Migration|migrations]].

| Peça | Onde |
|---|---|
| usuário e banco | `postgres/init/create-auth-database.sh` (cópia do do `lonzo`): roda só na primeira subida, com o volume vazio; no volume do dev, roda-se o mesmo SQL à mão |
| senha e URL | `.env` e `.env.example`: `AUTH_DB_PASSWORD` e `AUTH_DATABASE_URL` (`postgresql+psycopg://auth:...@postgres:5432/auth`) |
| libs | `uv add alembic 'psycopg[binary]' 'sqlalchemy[asyncio]'` |
| Alembic | `uv run alembic init migrations`; no `migrations/env.py`, `config.set_main_option("sqlalchemy.url", os.environ["AUTH_DATABASE_URL"])` |
| conexão | `src/auth/db.py`: `engine` global e `transaction()` (`engine.begin()`) |
| testes | o `check-auth` passa `AUTH_DATABASE_URL` com `localhost` no lugar de `postgres`, como o `check-lonzo` |

O banco e o script do Postgres vão numa branch `postgres/...`; o resto, na do serviço, um commit por linha da tabela.

## Revisar se...

- Um terceiro serviço repetir tudo isto: vale um `ai/np` que gere o esqueleto (pyproject, Dockerfile, health, alvo do `make`).
- O código que os serviços dividem crescer (conexão, handlers): pacote comum, ainda em aberto em [[Um repo ou vários]].
