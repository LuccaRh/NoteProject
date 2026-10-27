---
tags: [noteproject, conceito, servidor]
---
# Python — decorator, with e yield

Duas situações se repetem em todo programa: registrar uma função numa lista para outro código chamá-la depois (as rotas de um [[FastAPI|framework web]]), e garantir que um recurso aberto seja fechado mesmo se o código do meio quebrar (arquivo, conexão com o banco). O Python tem uma sintaxe para cada uma: o `@` (decorator) e o `with` (context manager). O `yield` liga as duas e deixa escrever um context manager como uma função comum.

Os dois dependem de **quando** cada linha roda: o import executa o arquivo de cima a baixo, e o `def` cria a função sem rodar o corpo ([[Python — módulo, package e venv#O que o import executa|o que o import executa]]).

## Decorator: o `@`

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

### Exemplo sem lib

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

### Decorator com argumento: a fábrica

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

## `with`: entrada, bloco e saída garantida

O `with` roda um código de **entrada** antes do bloco e um de **saída** depois, **sempre**, mesmo se o bloco quebrar. Equivale a um `try/finally`:

```python
with open("a.txt") as f:      # é o mesmo que:
    f.read()
                              # f = open("a.txt")      ← entrada
                              # try:
                              #     f.read()           ← bloco
                              # finally:
                              #     f.close()          ← saída: roda sempre
```

Encadear `open("a.txt").read()` também abre e lê, mas não garante o `close()` se o `read()` quebrar.

### Quem decide a entrada e a saída: `__enter__` e `__exit__`

O `with` não sabe abrir nem fechar nada: chama dois métodos de nome fixo do objeto que vem depois dele. Um objeto com os dois é um **context manager**.

```python
with X as c:          # c = X.__enter__()
    ...               # o bloco
                      # X.__exit__(tipo_do_erro, erro, traceback)
                      #   sem erro: os três chegam como None
```

O `__exit__` recebe o erro e escolhe o que fazer com ele. Uma versão de brinquedo de uma transação de banco:

```python
class Transacao:
    def __enter__(self):
        print("BEGIN")
        return self                      # vai para o "as ..."

    def __exit__(self, tipo, erro, tb):
        if tipo is None:
            print("COMMIT")
        else:
            print("ROLLBACK por causa de:", repr(erro))

with Transacao():
    print("  INSERT ...")

with Transacao():
    print("  INSERT ...")
    1 / 0
```

```
BEGIN
  INSERT ...
COMMIT
BEGIN
  INSERT ...
ROLLBACK por causa de: ZeroDivisionError('division by zero')
```

- O arquivo do `open()` é um `_io.TextIOWrapper`, cujo `__exit__` chama `close()`.
- Objeto sem os dois métodos: o `with` recusa antes do bloco, com `TypeError: 'X' object does not support the context manager protocol (missed __exit__ method)` (Python 3.14.8).
- Um `with` dentro de outro fecha **de dentro para fora**: o `__exit__` de dentro roda primeiro.

## `yield` e `@contextmanager`

O `yield` funciona como um `return` que **pausa** a função: entrega um valor e, quando alguém pede, continua da linha seguinte. O decorator `@contextlib.contextmanager` usa isso para montar um context manager sem escrever a classe:

| Parte da função | Vira |
|---|---|
| antes do `yield` | o `__enter__` |
| o valor do `yield` | o que vai para o `as ...` |
| depois do `yield` | o `__exit__` |
| erro no bloco | aparece na linha do `yield`, onde um `try/except` o trata |

```python
from contextlib import contextmanager

@contextmanager
def transacao():
    print("BEGIN")
    try:
        yield "conexão"
        print("COMMIT")
    except Exception:
        print("ROLLBACK")
        raise

with transacao() as c:
    print("  bloco recebeu:", c)

try:
    with transacao() as c:
        1 / 0
except ZeroDivisionError as e:
    print("erro segue adiante:", repr(e))
```

```
BEGIN
  bloco recebeu: conexão
COMMIT
BEGIN
ROLLBACK
erro segue adiante: ZeroDivisionError('division by zero')
```

- Com `return` no lugar do `yield`, a função acabaria ali: a saída rodaria **antes** do bloco, e o bloco receberia um recurso já fechado.
- `type(...)` de um desses é `contextlib._GeneratorContextManager`. O `engine.begin()` do [[SQLAlchemy — engine e conexão|SQLAlchemy]] é feito assim ([[SQLAlchemy — engine e conexão#Transação|transação]]), e o `Depends` do [[FastAPI]] aceita função com `yield` pelo mesmo formato.

> [!warning] Erros comuns
> - Achar que o `@` roda a cada chamada da função: roda uma vez, ao ler o `def`.
> - `@anota()` com um decorator que espera a função: chama sem argumento e dá `TypeError`.
> - Esquecer o `return func` no decorator: o nome passa a valer `None`.
> - `open(...).read()` sem `with`: o arquivo fica aberto se o `read()` quebrar.
> - Engolir o erro no `except` de um `@contextmanager` sem `raise`: o bloco parece ter dado certo.

## Fontes

- decorators: https://docs.python.org/3/glossary.html#term-decorator
- `with` e context managers: https://docs.python.org/3/reference/compound_stmts.html#the-with-statement
- `contextlib.contextmanager`: https://docs.python.org/3/library/contextlib.html#contextlib.contextmanager
- saídas conferidas em 2026-10-26 com Python 3.14.8, fastapi 0.150.0, SQLAlchemy 2.1.6.
