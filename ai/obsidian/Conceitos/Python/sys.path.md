---
tags: [noteproject, conceito, servidor]
---
# sys.path

O `import` precisa de uma regra fixa de **onde procurar** os [[Módulo Python|módulos]] e [[Package Python|packages]]. O `sys.path` é essa regra: uma lista de pastas, cada uma com o caminho completo, testadas em ordem.

## Como a busca anda

No `import a.b.c`:

1. o Python testa cada pasta da lista, em ordem, procurando `a` (um `a.py` ou uma pasta `a/`) **só no primeiro nível** dela;
2. a primeira pasta que tiver `a` vence;
3. cada ponto desce um nível a partir dali: entra em `a/`, depois em `b/`, e pega `c.py`.

A busca nunca desce sozinha em subpastas. Num [[venv]] só com o fastapi existem seis `utils.py` (`fastapi/utils.py`, `pydantic/utils.py`, `fastapi/security/utils.py`...); se a busca descesse, `import utils` teria seis candidatos. Os pontos deixam o caminho único.

## Quem põe cada pasta

| Item da lista | Quem põe |
|---|---|
| pasta do script que rodou (`python sub/x.py` → `sub/`, não a pasta do terminal) | o Python, ao iniciar |
| biblioteca padrão (`os`, `json`) | o Python, sempre |
| `site-packages` | o Python que rodou: o do sistema traz `/usr/lib/python3.x/site-packages`; o de um [[venv]] traz o do venv no lugar |
| caminhos escritos em arquivos `.pth` dentro do `site-packages` | o módulo `site`, ao iniciar |
| `pythonpath = [...]` em `[tool.pytest.ini_options]` do `pyproject.toml` | o pytest, só durante os testes |

O pytest não usa a pasta do terminal: num `tests/test_x.py` sem `__init__.py`, ele põe `tests/` na lista, e um `from main import app` falha com `ModuleNotFoundError` se o `main.py` estiver na pasta de cima (pytest 9.1.1).

## Exemplo com src/

Com a árvore de [[Package Python#Estrutura plana × src/|estrutura `src/`]], a lista com `uv run pytest` fica:

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
> - `import routes` com `routes/` dentro de `api/`: o primeiro nome tem de estar no primeiro nível de um item da lista; o certo é `api.routes`.
> - `python sub/x.py` esperando achar módulos da pasta do terminal: o primeiro item da lista é `sub/`.

## Fontes

- `sys.path`: https://docs.python.org/3/library/sys_path_init.html
- arquivos `.pth` e o módulo `site`: https://docs.python.org/3/library/site.html
- `pythonpath` do pytest: https://docs.pytest.org/en/stable/reference/reference.html#confval-pythonpath
- saídas conferidas em 2026-10-20 com Python 3.12 e 3.14, uv 0.13.1, pytest 9.1.1.
