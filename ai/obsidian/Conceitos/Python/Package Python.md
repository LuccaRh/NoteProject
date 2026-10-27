---
tags: [noteproject, conceito, servidor]
---
# Package Python

Quando o código passa de alguns arquivos, os [[Módulo Python|módulos]] se agrupam em pastas. O package é essa pasta, importada com ponto (`api.routes`), e é também o formato em que as libs de fora chegam ao projeto.

| Peça | O que é | Exemplo |
|---|---|---|
| Package | pasta de módulos, importada com ponto; o `__init__.py` roda no import e marca a pasta como package | `routes/` → `api.routes` |
| Namespace package | pasta sem `__init__.py`, aceita desde o Python 3.3 (PEP 420) | raro em código próprio |
| Lib de fora | package pronto, escrito por outros | `fastapi/` |
| `site-packages` | pasta onde o instalador põe as libs de fora | `.venv/lib/python3.x/site-packages/` |
| Instalar | pôr um package numa pasta que o Python já procura ([[sys.path]]) | `uv add fastapi` ([[uv]]) |

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
| Como o Python acha | a pasta do projeto entra na lista (`pythonpath = ["."]` no pytest) | o package é **instalado** no [[venv]], como uma lib de fora |
| Import | `from main import app` | `from api.main import app` |
| `uv init` (0.13.1) | `uv init --no-package`: `main.py` na raiz, sem `[build-system]` | padrão: cria `src/` e `[build-system]` |

No modo padrão do [[uv]] (instalação editável), instalar o próprio package não copia o código: o `uv sync` deixa em `site-packages` um arquivo `api.pth` com uma linha, o caminho de `src/`, e o Python põe essa pasta no [[sys.path]] ao iniciar. Editar `src/` vale no próximo import, sem reinstalar. Cópia de verdade só acontece na instalação não editável, a de uma [[Container|imagem Docker]]; só nela um teste pega o arquivo que o pacote deixou de fora.

Por que `src/`: a pasta do script que rodou entra no começo da lista, então, na estrutura plana, `import api` acha o código da pasta atual mesmo sem nada instalado, por acaso. Com `src/`, o import só funciona pelo package instalado, e os testes rodam contra o mesmo package que vai para a imagem.

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

Como o `import` acha cada nome dessa árvore está em [[sys.path#Exemplo com src/|sys.path]].

### Como o uv acha a pasta do package

O `uv_build` monta o caminho com duas chaves de `[tool.uv.build-backend]`; sem a seção, valem os padrões:

| Chave | Padrão | Exemplo com `name = "meu-app"` |
|---|---|---|
| `module-root` | `src` | `src/` |
| `module-name` | o `name` do `[project]`, com `-` trocado por `_` | `meu_app` |
| caminho esperado | `<module-root>/<module-name>/__init__.py` | `src/meu_app/__init__.py` |

- O `src/` não vira package: é só onde procurar, e é ele que o `.pth` põe na lista.
- Pasta com outro nome: o build falha com `Expected a Python module at: src/meu_app/__init__.py` (uv 0.13.1). Saída: renomear a pasta ou declarar `module-name = "outro"`.

> [!warning] Erros comuns
> - Esperar que o `__init__.py` faça a pasta ser achada: ele marca o que tem dentro; quem faz achar é a pasta **mãe** estar na lista.

> [!example] Uso
> A escolha entre plana e `src/` da API de notas está em [[API de notas]].

## Fontes

- namespace packages: https://peps.python.org/pep-0420/
- `uv init` e estruturas: https://docs.astral.sh/uv/concepts/projects/init/
- [uv — build backend](https://docs.astral.sh/uv/concepts/build-backend/)
- saídas conferidas em 2026-10-20 com Python 3.12 e 3.14, uv 0.13.1, fastapi 0.150.0.
