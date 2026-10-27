---
tags: [noteproject, conceito, servidor]
---
# Módulo Python

Um programa Python cresce em vários arquivos e usa código pronto de outros, como um [[FastAPI|framework web]]. O `import` traz para um arquivo algo definido em outro, e a unidade que ele traz é o módulo.

- **Módulo**: um arquivo `.py`; o nome é o do arquivo sem `.py` (`main.py` → módulo `main`).
- Uma pasta de módulos importada com ponto é um [[Package Python|package]]; onde o `import` procura os dois é o [[sys.path]].

## O que vem depois do `from` e do `import`

| Forma | O que vai ali |
|---|---|
| `import X` / `from X import ...` | `X` é sempre módulo ou [[Package Python\|package]] |
| `from X import Y` | `Y` é um submódulo **ou** algo definido em `X`: classe, função, variável |

Em `from fastapi import FastAPI`, `fastapi` é um package (pasta) e `FastAPI` é uma **classe**, definida em `fastapi/applications.py`. O `fastapi/__init__.py` reexporta a classe (`from .applications import FastAPI`), por isso o import não precisa citar `applications` (fastapi 0.150.0).

## O que o import executa

O primeiro `import` de um módulo **roda o arquivo inteiro, de cima a baixo**, uma vez; os imports seguintes do mesmo módulo reaproveitam o resultado. O Python primeiro lê e confere a sintaxe do arquivo todo, depois executa linha por linha:

| Linha | Ao importar |
|---|---|
| `x = 5`, `router = APIRouter()` | roda: cria o objeto |
| `def f(): ...` | roda como uma linha só: cria o objeto função e guarda o corpo; o corpo **não** roda |
| `@X` em cima de um `def` | roda logo depois do `def`: `f = X(f)` ([[Decorator\|decorator]]) |
| `import y` | roda o arquivo de `y` inteiro, se ainda não foi importado |

O corpo de uma função só roda quando alguém a chama com `()`. Numa API, isso separa dois momentos:

```
ao subir (uma vez)       o servidor importa main.py → main importa os arquivos de rotas
                         → cada @ registra uma rota → a lista de rotas está pronta
                         → o servidor abre a porta
a cada pedido            o framework acha a função na lista e a chama: só o corpo roda
```

Um arquivo de rotas que nenhum outro importa nunca roda, e as rotas dele não existem: o pedido recebe 404.

> [!warning] Erros comuns
> - `import FastAPI`: o módulo é `fastapi`, minúsculo; a classe vem com `from fastapi import FastAPI`.
> - `from .venv/fastapi import ...` ou `from ../main import ...`: o `import` não aceita caminho; muda-se o Python que roda ([[venv]]) ou a lista ([[sys.path]]).

## Fontes

- `import`: https://docs.python.org/3/reference/import.html
- saídas conferidas em 2026-10-20 com Python 3.14 e fastapi 0.150.0.
