---
tags: [noteproject, conceito, servidor]
---
# Context manager

Um recurso aberto (arquivo, conexão com o banco, [[Transação|transação]]) precisa ser fechado mesmo se o código do meio quebrar. O context manager é o objeto que sabe abrir e fechar; o `with` é a sintaxe que o usa; e o `yield` deixa escrever um context manager como uma função comum.

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

## Quem decide a entrada e a saída: `__enter__` e `__exit__`

O `with` não sabe abrir nem fechar nada: chama dois métodos de nome fixo do objeto que vem depois dele. Um objeto com os dois é um **context manager**.

```python
with X as c:          # c = X.__enter__()
    ...               # o bloco
                      # X.__exit__(tipo_do_erro, erro, traceback)
                      #   sem erro: os três chegam como None
```

O `__exit__` recebe o erro e escolhe o que fazer com ele. Uma versão de brinquedo de uma [[Transação|transação]] de banco:

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

O `yield` funciona como um `return` que **pausa** a função: entrega um valor e, quando alguém pede, continua da linha seguinte. O [[Decorator|decorator]] `@contextlib.contextmanager` usa isso para montar um context manager sem escrever a classe:

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
- `type(...)` de um desses é `contextlib._GeneratorContextManager`. O `engine.begin()` do [[SQLAlchemy]] é feito assim ([[Transação#Transação no SQLAlchemy|transação]]), e o `Depends` do [[FastAPI]] aceita função com `yield` pelo mesmo formato.

> [!warning] Erros comuns
> - `open(...).read()` sem `with`: o arquivo fica aberto se o `read()` quebrar.
> - Engolir o erro no `except` de um `@contextmanager` sem `raise`: o bloco parece ter dado certo.

## Fontes

- `with` e context managers: https://docs.python.org/3/reference/compound_stmts.html#the-with-statement
- `contextlib.contextmanager`: https://docs.python.org/3/library/contextlib.html#contextlib.contextmanager
- saídas conferidas em 2026-10-26 com Python 3.14.8 e SQLAlchemy 2.1.6.
