---
tags: [noteproject, conceito, servidor]
---
# Gerador

Uma lista precisa existir inteira antes do `for` começar. Quando os itens chegam aos poucos (linhas de um arquivo grande, pedaços de uma resposta pela rede), o gerador entrega um item por vez, só quando alguém pede, e pausa entre um e outro.

## `yield` e `for`

Uma função com `yield` é um gerador. Chamar a função não roda o corpo: devolve um objeto parado no começo. Cada `next()` roda até o próximo `yield`, entrega o valor e pausa ali.

```python
def contar():
    print("começou")
    yield 1
    yield 2

g = contar()     # nada é impresso: o corpo ainda não rodou
print(next(g))   # imprime "começou" e depois 1
print(next(g))   # continua do primeiro yield: 2
```

O `for` é quem faz os `next()`, um por volta, até a função acabar:

```python
for n in contar():   # por baixo:
    print(n)         # it = iter(contar())
                     # n = next(it)  ← a cada volta, até acabar
```

O mesmo `yield` monta o [[Context manager|context manager]] do `@contextmanager`, onde ele divide a entrada da saída.

## `async for`: cada item pode demorar

Um gerador `async` (`async def` com `yield`) pode esperar com `await` antes de entregar o item, e o `async for` pede cada item com `await`:

```python
async for item in gerador():   # por baixo:
    ...                        # it = gerador().__aiter__()
                               # item = await it.__anext__()  ← a cada volta
```

Durante o `await`, a função pausa e o [[FastAPI#Muitos clientes ao mesmo tempo|event loop]] roda outra tarefa. Exemplo com duas leituras ao mesmo tempo, A e B, e um item a cada 1 s:

```python
import asyncio
import time


async def contar_devagar(nome):
    for n in [1, 2, 3]:
        await asyncio.sleep(1)    # finge esperar a rede
        yield f"{nome}{n}"


async def ler(nome):
    async for item in contar_devagar(nome):
        print(f"{time.time() - t0:.0f}s  {item}")


async def main():
    await asyncio.gather(ler("A"), ler("B"))   # as duas ao mesmo tempo

t0 = time.time()
asyncio.run(main())
print(f"total: {time.time() - t0:.0f}s")
```

```
1s  A1
1s  B1
2s  A2
2s  B2
3s  A3
3s  B3
total: 3s
```

Seis itens de 1 s levaram 3 s: enquanto A espera, B anda. Trocando o `await asyncio.sleep(1)` por `time.sleep(1)`, a espera trava o loop inteiro:

```
1s  A1
2s  A2
3s  A3
4s  B1
5s  B2
6s  B3
total: 6s
```

> [!example] Uso
> O `answer` do chat entrega cada pedaço da resposta do modelo com `yield`, dentro de um `async for` sobre o stream ([[Caminho de uma pergunta|caminho de uma pergunta]]).

> [!warning] Erros comuns
> - Esperar que `gerador()` rode o corpo: sem `for` ou `next()`, nada acontece.
> - `time.sleep` (ou outra espera sem `await`) dentro de um gerador `async`: trava todas as tarefas, não só a dele.

## Fontes

- `yield` e geradores: https://docs.python.org/3/reference/expressions.html#yield-expressions
- `async for`: https://docs.python.org/3/reference/compound_stmts.html#the-async-for-statement
- geradores `async`: PEP 525, https://peps.python.org/pep-0525/
- saídas conferidas em 2026-11-01 com Python 3.14.8.
