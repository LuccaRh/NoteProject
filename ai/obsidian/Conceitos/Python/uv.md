---
tags: [noteproject, conceito, servidor]
---
# uv

Um projeto Python precisa dizer de quais libs depende e ter essas libs instaladas no seu [[venv]], iguais em toda máquina. O uv (da Astral) cuida das duas pontas: o `pyproject.toml` é o pedido (o que o projeto precisa) e o `.venv` é o resultado (o que está instalado). Todo comando do uv deixa os dois iguais.

| Comando | O que faz |
|---|---|
| `uv init` | cria o `pyproject.toml`, o `.python-version` e a estrutura |
| `uv add <lib>` | 1. anota a lib no `pyproject.toml` e fixa as versões no `uv.lock`; 2. roda o `uv sync` (`--no-sync` pula esse passo) |
| `uv add --dev <lib>` | o mesmo, no grupo `dev` |
| `uv sync` | deixa o `.venv` igual ao `uv.lock`: cria o `.venv` se não existe, instala o que falta, remove o que sobra e instala o próprio projeto quando há `[build-system]` |
| `uv run <cmd>` | sincroniza e roda o comando com o Python do `.venv` |

- O `uv add fastapi` baixa a lib, põe em `site-packages` e anota no `pyproject.toml`; a versão exata vai no `uv.lock`.
- O uv não tem relação com o **uvicorn**: um instala libs e roda comandos; o outro é o servidor ASGI que escuta a porta de uma app [[FastAPI]]. O "uv" do uvicorn vem do uvloop, o event loop que ele usa *(geral)*.

## O pyproject.toml

Cada linha que o `uv init` gera:

| Linha | O que faz |
|---|---|
| `[project]` | dados do [[Package Python\|package]], no formato padrão da PEP 621 (não só do uv) |
| `name = "api"` | nome do package: o `api` do `import api` e do `api.pth` |
| `version = "0.1.0"` | versão do package; só pesa para quem publica ou depende dele |
| `description`, `readme`, `authors` | informação para quem publica; não muda nada ao rodar |
| `requires-python = ">=3.14"` | o uv recusa Python mais velho |
| `dependencies = ["fastapi[standard]>=0.150.0"]` | o que o código precisa para rodar; `[standard]` pede os extras da lib (no fastapi, o uvicorn e o comando `fastapi`); `>=` aceita essa versão ou mais nova, e a exata fica no `uv.lock` |
| `[project.scripts]` → `api = "api:main"` | cria um comando de terminal `api` em `.venv/bin/` que chama a função `main` do módulo `api`; útil para programa de linha de comando (o `ruff` é um comando criado assim), dispensável numa API HTTP, que roda pelo `fastapi` ou `uvicorn` |
| `[build-system]` | diz que o projeto é um package e quem sabe montá-lo; é o que faz o `uv sync` instalar o próprio projeto (PEP 517 e 518) |
| `requires = ["uv_build>=0.13.1,<0.14.0"]` | a ferramenta que monta o package, numa faixa de versões |
| `build-backend = "uv_build"` | o nome dela, para o instalador chamar |
| `[dependency-groups]` → `dev = [...]` | libs só de desenvolvimento (pytest, ruff, mypy); o `uv sync` instala por padrão, mas ficam fora do package publicado (PEP 735) |
| `[tool.<ferramenta>]` | configuração de cada ferramenta, lida por ela: `[tool.ruff]`, `[tool.mypy]`, `[tool.pytest.ini_options]` |

Onde o `uv_build` procura o código do package: [[Package Python#Como o uv acha a pasta do package|como o uv acha a pasta do package]].

## Fontes

- `uv init` e estruturas: https://docs.astral.sh/uv/concepts/projects/init/
- `pyproject.toml`: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
- saídas conferidas em 2026-10-20 com uv 0.13.1.
