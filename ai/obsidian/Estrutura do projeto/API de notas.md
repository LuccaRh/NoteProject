---
tags: [noteproject, servidor]
---
# API de notas

O serviço `notes` do [[Back — daemon e servidor|servidor]]: a API que o [[Navegador|navegador]] chama em `/api` para listar, abrir, salvar e buscar notas, e que serve o build do front. É uma app [[FastAPI]] em `apps/notes`, com imagem e [[Container e Docker Compose|container]] próprios ([[Um repo ou vários]]). Login fica em outro serviço, `auth` (M2).

## O que ela terá

| Rota | O quê | Etapa |
|---|---|---|
| `GET /health` | responde 200 se o processo está de pé; o healthcheck do [[Container e Docker Compose\|compose]] usa ([[Observabilidade]]) | ⏳ M0 (#10) |
| `/notes`, `/search` | as rotas que `apps/web/src/notes/api.ts` chama, com busca full-text no [[Postgres e migrations\|Postgres]] | ⏳ M1 (#46) |
| `/` e arquivos estáticos | o build do editor: uma URL só, nada instalado | ⏳ M1 (#47) |

- Rotas síncronas (`def`) até o banco entrar: sem `await`, a thread do pool é o caminho seguro ([[FastAPI]], "`async def` ou `def`").
- O [[Postgres e migrations|Postgres]] entra na #12, com o pool aberto no `lifespan`.
- O proxy do Vite (`make dev`) manda `/api` para `localhost:8000`; no ar, quem repassa é o [[Reverse proxy|Caddy]].

## Estrutura dentro de `apps/notes`: `src/`

A divisão entre serviços está em [[Um repo ou vários]]; aqui fica a de dentro do serviço, que vale para todo serviço Python do repo. Como o `import` acha o código em cada estrutura: [[Python — módulo, package e venv|módulo, package e venv]].

| | Plana | `src/` |
|---|---|---|
| Arquivos | `apps/notes/main.py`, `tests/`, `pyproject.toml` | `apps/notes/src/notes/main.py`, `tests/`, `pyproject.toml` |
| `uv init` (0.13.1) | `uv init --no-package` | padrão |
| Import nos testes | só com `pythonpath = ["."]` no pytest: sem isso a lista começa em `tests/` e `from main import app` falha | com o pacote instalado: o `uv sync` põe `src/` na lista por um `notes.pth` |
| Pega erro de empacotamento | não: o teste pode passar com arquivo que a imagem não copia | só com instalação não editável (a da imagem); a editável, padrão do uv, lê direto de `src/` |
| Rodar | `fastapi dev main.py` | `fastapi dev src/notes/main.py` ou `uvicorn notes.main:app` |

Escolha: **`src/`**, com o package instalado no `.venv` pelo `uv sync`.

- O código do serviço é achado de um jeito só, como package instalado: no teste, no `fastapi dev` e na imagem. Na plana, cada um depende de qual pasta entra na lista (`pythonpath` no pytest, pasta de trabalho no container).
- Todo import do serviço começa pelo nome dele (`notes.routes`, `auth.routes`): nome de módulo comum (`config`, `routes`) não colide com o de uma lib nem com o de outro serviço.
- É o padrão do `uv init` (0.13.1): nenhuma flag nem configuração a lembrar em cada serviço novo.
- Custo: um nível de pasta a mais (`src/notes/`) e um `[build-system]` no `pyproject.toml`.

Revisar se o serviço virar um script de um arquivo só, sem testes, ou se o empacotamento do uv atrapalhar a imagem ([[Container e Docker Compose|Docker]], #11).

Ainda a decidir: o alvo do `Makefile` que roda ruff, mypy e pytest do serviço (hoje só existem `check-web` e `check-tools`), com `uv run` na pasta `apps/notes`.

## Exercício

Montar o esqueleto da #10, sem banco e sem Docker:

1. Escolher a estrutura acima e registrar a escolha nesta página.
2. Criar o projeto Python em `apps/notes` com uv (Python 3.14), com `fastapi[standard]` e, como dependências de desenvolvimento, `pytest`, `ruff` e `mypy`.
3. Uma app [[FastAPI]] com `GET /health` devolvendo `{"status": "ok"}`.
4. Um teste com `TestClient` que confere o 200 e o corpo.
5. Um alvo no `Makefile` que roda ruff, mypy e pytest do serviço, chamado pelo `make check`.

Pronto quando:

- `fastapi dev` sobe a app e `curl -i localhost:8000/health` mostra `200 OK` com `{"status":"ok"}`;
- `localhost:8000/docs` lista a rota;
- `make check` roda e passa os testes do serviço; com o teste quebrado de propósito (esperar 201), ele falha.

Pergunta para responder antes da #11: com `fastapi dev`, um `curl` vindo de outra máquina da rede chega na app? E com `fastapi run`? Por quê?
