---
tags: [noteproject, conceito, servidor]
---
# Decorator

Todo framework precisa registrar funções numa lista para chamá-las depois: as rotas de um [[FastAPI|framework web]], os comandos de uma CLI. O decorator é a sintaxe do Python para isso: o `@` em cima de um `def`.

Ele depende de **quando** cada linha roda: o import executa o arquivo de cima a baixo, e o `def` cria a função sem rodar o corpo ([[Módulo Python#O que o import executa|o que o import executa]]).

## O `@`

Um decorator é uma função que recebe outra função logo depois de ela ser criada. O `@` é só um atalho de escrita:

```python
@X
def f(): ...

# o Python troca por:
def f(): ...
f = X(f)
```

- O `@` é **sintaxe** do Python, como o `=`: não é função e não devolve nada. Quem devolve algo é o `X`, que é uma função comum.
- Depois do `@` vem qualquer expressão que dê uma função; embaixo dele, só `def` ou `class`. A função (ou classe) de baixo é o parâmetro.
- Roda **uma vez, ao ler o `def`**: no import do arquivo, antes de qualquer chamada de `f`.

## Exemplo sem lib

```python
lista = []

def anota(func):           # função comum, que recebe uma função
    print("anota recebeu:", func.__name__)
    lista.append(func)
    return func

@anota                     # = depois do def, fazer: ola = anota(ola)
def ola():
    print("olá!")

print("lista:", lista)
ola()
```

```
anota recebeu: ola                            ← o @ rodou ao ler o def
lista: [<function ola at 0x7f9eac19b060>]     ← a função entrou na lista
olá!                                          ← o corpo só rodou no ola()
```

A lista guarda **a própria função**, sem chamá-la: `lista.append(func)`, sem `()`. Quem quiser rodá-la depois faz `lista[0]()`.

## Decorator com argumento: a fábrica

Para registrar uma rota, o decorator precisa saber o caminho. Então uma função recebe o caminho e **fabrica** o decorator; só o fabricado vai no `@`:

```python
rotas = {}

def get(caminho):                 # a fábrica
    def anota(funcao):            # o decorator fabricado, que já conhece o caminho
        rotas[("GET", caminho)] = funcao
        return funcao
    return anota

@get("/health")                   # 1º get("/health") devolve anota
def health():                     # 2º o def cria health, sem rodar o corpo
    return {"status": "ok"}       # 3º o Python chama anota(health) → entra no dicionário

rotas[("GET", "/health")]()       # um pedido: só agora o corpo roda
```

![[decorator-no-import.drawio.svg]]
*Em cima, o que roda uma vez ao importar o arquivo; embaixo, o que roda a cada pedido.*

O `@router.get("/health")` do [[FastAPI]] tem esse formato: `router.get` fabrica um `decorator`, que chama `add_api_route` e faz `self.routes.append(route)`; depois devolve a função sem mudança (fastapi 0.150.0, `fastapi/routing.py:3106-3136` e `:3073`). O `@` é do Python; a fábrica, o decorator e a lista são da lib.

| Escrito | O que roda ao ler o arquivo | Registra? |
|---|---|---|
| `get("/health")` solto, sem `@` | fabrica o `anota` e o joga fora | não: ninguém passou `health` a ele |
| `@get("/health")` + `def health` | fabrica o `anota`, cria `health`, chama `anota(health)` | sim |
| `@anota()` com parênteses | chama `anota()` sem a função | `TypeError: anota() missing 1 required positional argument: 'func'` |

- O `@contextlib.contextmanager` é um decorator da biblioteca padrão que transforma uma função com `yield` num [[Context manager|context manager]].

> [!warning] Erros comuns
> - Achar que o `@` roda a cada chamada da função: roda uma vez, ao ler o `def`.
> - `@anota()` com um decorator que espera a função: chama sem argumento e dá `TypeError`.
> - Esquecer o `return func` no decorator: o nome passa a valer `None`.

## Fontes

- decorators: https://docs.python.org/3/glossary.html#term-decorator
- saídas conferidas em 2026-10-26 com Python 3.14.8 e fastapi 0.150.0.
