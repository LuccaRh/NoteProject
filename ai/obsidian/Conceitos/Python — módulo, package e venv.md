---
tags: [noteproject, conceito, servidor]
---
# Python — módulo, package e venv

Um programa Python cresce em vários arquivos e usa código pronto de outros, como um [[FastAPI|framework web]]. O `import` traz para um arquivo algo definido em outro; para isso o Python precisa de uma regra fixa de **onde procurar**, e cada projeto precisa das suas versões das libs sem brigar com os outros projetos da máquina.

## As peças

| Peça | O que é | Exemplo |
|---|---|---|
| Módulo | um arquivo `.py`; o nome é o do arquivo sem `.py` | `main.py` → módulo `main` |
| Package | pasta de módulos, importada com ponto; o `__init__.py` roda no import e marca a pasta como package | `routes/` → `api.routes` |
| Namespace package | pasta sem `__init__.py`, aceita desde o Python 3.3 (PEP 420) | raro em código próprio |
| Lib de fora | package pronto, escrito por outros | `fastapi/` |
| `site-packages` | pasta onde o instalador põe as libs de fora | `.venv/lib/python3.x/site-packages/` |
| venv | pasta com um `python` e um `site-packages` só daquele projeto | `.venv/` |
| Instalar | pôr um package numa pasta que o Python já procura | `uv add fastapi` |
| `sys.path` | lista de pastas onde o `import` procura | seção abaixo |

## O que vem depois do `from` e do `import`

| Forma | O que vai ali |
|---|---|
| `import X` / `from X import ...` | `X` é sempre módulo ou package |
| `from X import Y` | `Y` é um submódulo **ou** algo definido em `X`: classe, função, variável |

Em `from fastapi import FastAPI`, `fastapi` é um package (pasta) e `FastAPI` é uma **classe**, definida em `fastapi/applications.py`. O `fastapi/__init__.py` reexporta a classe (`from .applications import FastAPI`), por isso o import não precisa citar `applications` (fastapi 0.150.0).

## sys.path: a lista de pontos de partida

`sys.path` é uma lista de pastas, cada uma com o caminho completo. No `import a.b.c`:

1. o Python testa cada pasta da lista, em ordem, procurando `a` (um `a.py` ou uma pasta `a/`) **só no primeiro nível** dela;
2. a primeira pasta que tiver `a` vence;
3. cada ponto desce um nível a partir dali: entra em `a/`, depois em `b/`, e pega `c.py`.

A busca nunca desce sozinha em subpastas. Num venv só com o fastapi existem seis `utils.py` (`fastapi/utils.py`, `pydantic/utils.py`, `fastapi/security/utils.py`...); se a busca descesse, `import utils` teria seis candidatos. Os pontos deixam o caminho único.

| Item da lista | Quem põe |
|---|---|
| pasta do script que rodou (`python sub/x.py` → `sub/`, não a pasta do terminal) | o Python, ao iniciar |
| biblioteca padrão (`os`, `json`) | o Python, sempre |
| `site-packages` | o Python que rodou: o do sistema traz `/usr/lib/python3.x/site-packages`; o de um venv traz o do venv no lugar |
| caminhos escritos em arquivos `.pth` dentro do `site-packages` | o módulo `site`, ao iniciar |
| `pythonpath = [...]` em `[tool.pytest.ini_options]` do `pyproject.toml` | o pytest, só durante os testes |

O pytest não usa a pasta do terminal: num `tests/test_x.py` sem `__init__.py`, ele põe `tests/` na lista, e um `from main import app` falha com `ModuleNotFoundError` se o `main.py` estiver na pasta de cima (pytest 9.1.1).

## venv

Um `site-packages` comporta um só `fastapi/`: instalar a versão 0.100 apaga a 0.120, e um dos projetos que dependem dela quebra. O venv dá a cada projeto o seu:

```
projeto/.venv/
├── bin/python                      ← o Python deste projeto
└── lib/python3.x/site-packages/    ← os instalados só deste projeto
```

O `import` não muda com o venv; muda **qual Python** roda, e cada Python traz a sua lista:

```
python3 main.py             ← Python do sistema: site-packages do sistema
.venv/bin/python main.py    ← Python do venv: site-packages do venv
uv run python main.py       ← igual ao de cima; o uv escolhe o Python do .venv
```

O `.venv` é gerado: fica fora do git e não se edita à mão. O `uv add fastapi` baixa a lib, põe em `site-packages` e anota no `pyproject.toml` (a versão exata vai no `uv.lock`); com o `.venv` apagado, o `uv sync` reinstala tudo igual. É o mesmo papel do `node_modules/` com `package.json` e `package-lock.json`.

## pyproject e uv

O `pyproject.toml` é o pedido (o que o projeto precisa) e o `.venv` é o resultado (o que está instalado). Todo comando do uv deixa os dois iguais:

| Comando | O que faz |
|---|---|
| `uv init` | cria o `pyproject.toml`, o `.python-version` e a estrutura |
| `uv add <lib>` | 1. anota a lib no `pyproject.toml` e fixa as versões no `uv.lock`; 2. roda o `uv sync` (`--no-sync` pula esse passo) |
| `uv add --dev <lib>` | o mesmo, no grupo `dev` |
| `uv sync` | deixa o `.venv` igual ao `uv.lock`: cria o `.venv` se não existe, instala o que falta, remove o que sobra e instala o próprio projeto quando há `[build-system]` |
| `uv run <cmd>` | sincroniza e roda o comando com o Python do `.venv` |

Cada linha do `pyproject.toml` que o `uv init` gera:

| Linha | O que faz |
|---|---|
| `[project]` | dados do package, no formato padrão da PEP 621 (não só do uv) |
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

## Biblioteca, package e serviço

| | O que é | Quem usa |
|---|---|---|
| Package | o **formato**: pasta de módulos, instalável | qualquer código Python |
| Biblioteca | package feito para **outros importarem** | outros projetos, com `import` (fastapi, pydantic) |
| Serviço | programa que **roda** e atende pedidos | clientes pela rede (navegador, `curl`); ninguém importa |

Um serviço pode ter o formato de package: ser instalável só serve para o `import` achar o código do jeito que acharia uma biblioteca. Quem instala as dependências é o `uv sync`, na máquina de desenvolvimento e na construção da imagem; quem instala uma biblioteca recebe junto as `dependencies` dela.

## Estrutura plana × src/

As duas respondem à mesma pergunta: como o `import` acha o código **do próprio projeto**.

| | Plana | `src/` |
|---|---|---|
| Código | `projeto/main.py` | `projeto/src/api/main.py` |
| Como o Python acha | a pasta do projeto entra na lista (`pythonpath = ["."]` no pytest) | o package é **instalado** no venv, como uma lib de fora |
| Import | `from main import app` | `from api.main import app` |
| `uv init` (0.13.1) | `uv init --no-package`: `main.py` na raiz, sem `[build-system]` | padrão: cria `src/` e `[build-system]` |

No modo padrão do uv (instalação editável), instalar o próprio package não copia o código: o `uv sync` deixa em `site-packages` um arquivo `api.pth` com uma linha, o caminho de `src/`, e o Python põe essa pasta na lista ao iniciar. Editar `src/` vale no próximo import, sem reinstalar. Cópia de verdade só acontece na instalação não editável, a de uma [[Container e Docker Compose|imagem Docker]]; só nela um teste pega o arquivo que o pacote deixou de fora.

## Exemplo completo (`src/`)

```
projeto/
├── pyproject.toml              [build-system] → o uv instala "api"
├── src/api/                    ← package "api"
│   ├── __init__.py
│   ├── main.py                 from fastapi import FastAPI
│   │                           from api.routes import health
│   ├── config.py               (só define coisas, não importa nada do projeto)
│   └── routes/                 ← package dentro de package
│       ├── __init__.py
│       └── health.py           from fastapi import APIRouter
│                               from api.config import settings
├── tests/test_health.py        from fastapi.testclient import TestClient
│                               from api.main import app
└── .venv/lib/python3.x/site-packages/
    ├── fastapi/                ← instalado com uv add
    └── api.pth                 ← uma linha: projeto/src
```

A lista com `uv run pytest`:

```
projeto/tests                               ← pasta do teste (posta pelo pytest)
.../lib/python3.x                           ← biblioteca padrão
projeto/.venv/lib/python3.x/site-packages   ← tem fastapi/
projeto/src                                 ← posta pelo api.pth; tem api/
```

| Import | Primeiro nome achado em | Desce por |
|---|---|---|
| `fastapi` | `site-packages/fastapi/` | nada |
| `fastapi.testclient` | `site-packages/fastapi/` | `testclient.py` |
| `api.routes.health` | `src/api/` | `routes/` → `health.py` |
| `routes` | nenhum item | `ModuleNotFoundError` |

> [!warning] Erros comuns
> - `import FastAPI`: o módulo é `fastapi`, minúsculo; a classe vem com `from fastapi import FastAPI`.
> - `from .venv/fastapi import ...` ou `from ../main import ...`: o `import` não aceita caminho; muda-se o Python que roda (venv) ou a lista (`pythonpath`).
> - `import routes` com `routes/` dentro de `api/`: o primeiro nome tem de estar no primeiro nível de um item da lista; o certo é `api.routes`.
> - Esperar que o `__init__.py` faça a pasta ser achada: ele marca o que tem dentro; quem faz achar é a pasta **mãe** estar na lista.
> - `python sub/x.py` esperando achar módulos da pasta do terminal: o primeiro item da lista é `sub/`.

> [!example] Uso
> A escolha entre plana e `src/` da API de notas está em [[API de notas]].

## Fontes

- `sys.path`: https://docs.python.org/3/library/sys_path_init.html
- arquivos `.pth` e o módulo `site`: https://docs.python.org/3/library/site.html
- namespace packages: https://peps.python.org/pep-0420/
- `uv init` e estruturas: https://docs.astral.sh/uv/concepts/projects/init/
- `pyproject.toml`: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
- `pythonpath` do pytest: https://docs.pytest.org/en/stable/reference/reference.html#confval-pythonpath
- saídas conferidas em 2026-10-20 com Python 3.12 e 3.14, uv 0.13.1, pytest 9.1.1, fastapi 0.150.0.
