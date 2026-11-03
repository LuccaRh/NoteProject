---
tags: [noteproject, servidor]
---
# API de notas

O serviço `ichiro` do [[Back — daemon e servidor|servidor]]: a API que o [[Navegador|navegador]] chama em `/api` para listar, abrir, salvar e buscar notas, e que serve o build do front. É uma app [[FastAPI]] em `apps/ichiro`, com imagem e [[Container|container]] próprios ([[Um repo ou vários]]). Login fica em outro serviço, `auth` (M2).

## O que ela terá

| Rota | O quê | Etapa |
|---|---|---|
| `GET /health` | responde 200 se o processo está de pé; o healthcheck do [[Docker Compose\|compose]] usa ([[Observabilidade]]) | ⏳ M0 (#10) |
| `/notes` | CRUD das notas e pastas no [[Postgres]] | ⏳ M1 (#46) |
| `GET /notes/search?q=&parent_id=` | [[Busca full-text no Postgres\|busca full-text]] no título e no corpo, `[{id, title}]` por título, só dentro de `parent_id` (qualquer profundidade) quando vem; declarada antes de `/notes/{note_id}`, que pegaria o `search` | ✅ M1 (#56) |
| `GET /notes/search-titles?q=&parent_id=` | `ILIKE` no título: acha pedaço de palavra, em notas e pastas, `[{id, title, is_folder}]` por título; o mesmo filtro por pasta da busca acima | ✅ M1 (#107) |

O build do editor não passa pela api: o [[Reverse proxy|Caddy]] serve os [[Arquivo estático|arquivos estáticos]] na mesma origem ([[Navegador]], #47).

- Rotas síncronas (`def`) até o banco entrar: sem `await`, a thread do pool é o caminho seguro ([[FastAPI]], "`async def` ou `def`").
- O [[Postgres]] entra na #12, com o pool aberto no `lifespan`.

## Banco ⏳ #12, #46

| Peça | Onde | Etapa |
|---|---|---|
| `DATABASE_URL` no `.env`, com o host `postgres` (nome do serviço) | raiz, injetada pelo [[Docker Compose\|compose]] | ⏳ #12 |
| [[Migration\|migrations]]: `alembic.ini`, `migrations/env.py` (lê a `DATABASE_URL`), `migrations/versions/` | `apps/ichiro` | ⏳ #12 |
| primeira migration: `users` e `notes` | `migrations/versions/` | ⏳ #12 |
| [[SQLAlchemy\|engine]] criado com a mesma URL; `/health` faz um `SELECT 1` | `apps/ichiro/src/ichiro/` | ⏳ #12 |
| conexão por pedido (`Depends`) e as consultas das rotas | `apps/ichiro/src/ichiro/` | ⏳ #46 |

- O Alembic roda dentro do container `ichiro` ([[Comandos do Docker no dev|`dc exec ichiro uv run alembic upgrade head`]]): fora da rede do compose, o host `postgres` não resolve ([[Rede de containers]]).
- Quem manda `/api/notes` para o `ichiro:8000`, tirando o `/api`, é o [[Reverse proxy|Caddy]], no compose de dev e no ar. Toda rota do `ichiro` fica dentro de `/notes`, o recurso: rota nova não pede linha no Caddy ([[Reverse proxy#Prefixo nomeia o recurso|prefixo por recurso]]).

## Estrutura dentro de `apps/ichiro`: `src/`

A divisão entre serviços está em [[Um repo ou vários]]; aqui fica a de dentro do serviço, que vale para todo serviço Python do repo. Como o `import` acha o código em cada estrutura: [[Módulo Python|módulo]], [[Package Python|package]] e [[venv]].

| | Plana | `src/` |
|---|---|---|
| Arquivos | `apps/ichiro/main.py`, `tests/`, `pyproject.toml` | `apps/ichiro/src/ichiro/main.py`, `tests/`, `pyproject.toml` |
| `uv init` (0.13.1) | `uv init --no-package` | padrão |
| Import nos testes | só com `pythonpath = ["."]` no pytest: sem isso a lista começa em `tests/` e `from main import app` falha | com o pacote instalado: o `uv sync` põe `src/` na lista por um `notes.pth` |
| Pega erro de empacotamento | não: o teste pode passar com arquivo que a imagem não copia | só com instalação não editável (a da imagem); a editável, padrão do uv, lê direto de `src/` |
| Rodar | `fastapi dev main.py` | `fastapi dev src/notes/main.py` ou `uvicorn notes.main:app` |

Escolha: **`src/`**, com o package instalado no `.venv` pelo `uv sync`.

- O código do serviço é achado de um jeito só, como package instalado: no teste, no `fastapi dev` e na imagem. Na plana, cada um depende de qual pasta entra na lista (`pythonpath` no pytest, pasta de trabalho no container).
- Todo import do serviço começa pelo nome dele (`notes.routes`, `auth.routes`): nome de módulo comum (`config`, `routes`) não colide com o de uma lib nem com o de outro serviço.
- É o padrão do `uv init` (0.13.1): nenhuma flag nem configuração a lembrar em cada serviço novo.
- Custo: um nível de pasta a mais (`src/notes/`) e um `[build-system]` no `pyproject.toml`.

Revisar se o serviço virar um script de um arquivo só, sem testes, ou se o empacotamento do uv atrapalhar a imagem ([[Container|Docker]], #11).

## Pastas dentro de `src/notes`

Uma pasta por papel, e dentro dela um arquivo por recurso (`notes.py`, depois `folders.py`, `search.py`): quem procura as notas acha a rota, o formato e o erro com o mesmo nome em três pastas.

| Pasta ou arquivo | O que tem | Etapa |
|---|---|---|
| `main.py` | o `FastAPI()` e um `include_router` por arquivo de `routers/` | ✅ |
| `db.py` | o [[SQLAlchemy\|engine]] e o `get_conn`, a dependência da conexão por pedido | ✅ #12 |
| `routers/` | as rotas de cada recurso, num `APIRouter` com `prefix` | ✅ `health`, `notes`; ⏳ `search` (#56) |
| `schemas/` | os modelos Pydantic de entrada e saída (`Note`, `NoteCreate`, `NoteUpdate`): o formato do JSON, separado da tabela | ✅ `notes` (#46) |
| `errors/` | as respostas de erro de cada recurso (`not_found` → 404) | ✅ `notes` (#46) |

- Cada parâmetro das rotas vem do caminho, da query, do corpo ou de um `Depends` pela regra do [[FastAPI#De onde vem cada parâmetro|FastAPI]].
- `schemas/` e a tabela andam juntos sem ser a mesma coisa: coluna nova na [[Migration|migration]] só aparece na API se entrar no modelo e na lista de colunas da consulta.

## Imagem ⏳ #11

O serviço roda num [[Container|container]] do compose, com imagem feita pelo `apps/ichiro/Dockerfile` ([[Dockerfile]]):

- base com Python 3.14 e o uv; libs do `uv.lock` instaladas **antes** de copiar o `src/`, para a edição do código não reinstalar as libs;
- `.dockerignore` com a `.venv` do host;
- sobe com `fastapi run`, que escuta em `0.0.0.0`: o pedido do host chega pela rede do Docker, não pelo loopback do container ([[Rede de containers]]).

Ainda a decidir: o alvo do `Makefile` que roda ruff, mypy e pytest do serviço (hoje só existem `check-chimchar` e `check-tools`), com `uv run` na pasta `apps/ichiro`.

## Exercício

Montar o esqueleto da #10, sem banco e sem Docker:

1. Escolher a estrutura acima e registrar a escolha nesta página.
2. Criar o projeto Python em `apps/ichiro` com uv (Python 3.14), com `fastapi[standard]` e, como dependências de desenvolvimento, `pytest`, `ruff` e `mypy`.
3. Uma app [[FastAPI]] com `GET /health` devolvendo `{"status": "ok"}`.
4. Um teste com `TestClient` que confere o 200 e o corpo.
5. Um alvo no `Makefile` que roda ruff, mypy e pytest do serviço, chamado pelo `make check`.

Pronto quando:

- `fastapi dev` sobe a app e `curl -i localhost:8000/health` mostra `200 OK` com `{"status":"ok"}`;
- `localhost:8000/docs` lista a rota;
- `make check` roda e passa os testes do serviço; com o teste quebrado de propósito (esperar 201), ele falha.

Pergunta para responder antes da #11: com `fastapi dev`, um `curl` vindo de outra máquina da rede chega na app? E com `fastapi run`? Por quê?

> [!note]- Resposta
> Com `fastapi dev` não: ele escuta em `127.0.0.1`, e o pedido de fora chega pelo IP de rede da máquina. Com `fastapi run` sim: `0.0.0.0` aceita por todos os IPs. No container vale o mesmo, porque o pedido do host chega pela rede do Docker (`172.18.0.x`), não pelo loopback do container ([[Rede de containers]]).
