---
tags: [noteproject, conceito, servidor]
---
# ContextVar

Um servidor atende vários pedidos ao mesmo tempo, e funções distantes do mesmo pedido precisam do mesmo dado, como o id de quem pediu. Passar o dado por parâmetro obriga todas as funções do caminho a recebê-lo. Uma global comum mistura os pedidos. A `ContextVar`, da biblioteca padrão do Python (módulo `contextvars`), é visível de qualquer função, como uma global, e tem um valor por pedido.

## Por que uma global comum não serve

Entre o momento de guardar e o de ler, outro pedido pode rodar e sobrescrever o valor:

```python
usuario = ""

async def rota(nome):
    global usuario
    usuario = nome
    await asyncio.sleep(1)      # aqui outro pedido roda
    print(nome, "vê", usuario)
```

Com a Ana chamando e, meio segundo depois, a Bia:

```
ana vê bia
bia vê bia
```

O `nome` sobrevive à pausa porque é local da chamada. O `usuario` é um só, e o último a escrever vence. Em um teste com 1000 pedidos simultâneos em uma [[FastAPI|rota FastAPI]] com global comum, 999 leram o id de outra pessoa.

## O modelo

O `.set()` parece guardar o valor dentro da variável, mas guarda fora dela. A `ContextVar` não tem o valor: lê e escreve em um lugar que depende de qual pedido está rodando.

```python
context = {}          # um lugar só, com o id de cada pedido
request_atual = None  # o Python mantém isso; não aparece no código


class current_user:

    def set(id):
        context[request_atual] = id

    def get():
        return context[request_atual]
```

## Dois pedidos ao mesmo tempo

As linhas `request_atual = ...` acontecem sozinhas. No código só existem as linhas `set` e `get`, sem nenhum `request`:

```python
# Ana entra
request_atual = "ana"
current_user.set(id_ana)   # context = {"ana": id_ana}

# Bia entra
request_atual = "bia"
current_user.set(id_bia)   # context = {"ana": id_ana, "bia": id_bia}

# volta a Ana
request_atual = "ana"
current_user.get()         # context["ana"] → id_ana

# volta a Bia
request_atual = "bia"
current_user.get()         # context["bia"] → id_bia
```

O segundo `set` não apaga o primeiro. O `get` também não pega o último valor: o resultado depende só de qual pedido está rodando a linha. A frase "meu nome" funciona assim: as palavras são as mesmas, e a resposta muda conforme quem fala.

## O que existe de verdade

O Python não conhece pedidos. Ele conhece tasks e contextos, e o servidor cria uma task por pedido.

| No modelo | No Python |
|---|---|
| `context`, um dicionário só | um objeto `Context` por task, com os valores de cada `ContextVar` |
| `request_atual` | o contexto atual, um por thread |
| a chave é o pedido | a chave é a própria `ContextVar`, dentro do `Context` do pedido |

```
current_user                 um objeto, só com name e default

Task A ──▶ Context A         { current_user: "ana" }
Task B ──▶ Context B         { current_user: "bia" }
```

Com o `Context` no lugar do dicionário único, `set` e `get` ficam assim:

```python
class ContextVar:
    name: str
    default: object

    def set(self, value):
        contexto_atual[self] = value

    def get(self):
        return contexto_atual.get(self, self.default)
```

Quando nada foi guardado naquele `Context`, o `get` devolve o `default`.

## Quem liga o contexto: `context.run`

O `context.run(funcao)` liga o contexto, roda a função e desliga. Tudo o que a função chamar enxerga esse contexto, em qualquer profundidade:

```python
def read_user(user_id):
    current_user.set(user_id)

def set_user():
    print("set_user leu:", current_user.get())

def rota():
    set_user()

context_ana = Context()
context_bia = Context()

context_ana.run(read_user, "ana")
context_bia.run(read_user, "bia")

context_ana.run(rota)
context_bia.run(rota)
context_ana.run(rota)
```

```
set_user leu: ana
set_user leu: bia
set_user leu: ana
```

Nenhuma função recebeu o pedido nem o usuário. No servidor, o event loop faz esse `run` para cada trecho de uma task, e a troca acontece sozinha a cada `await`.

## Cópia do contexto

Uma task nova ou uma thread do pool recebe uma cópia do `Context` de quem a criou, com os valores daquele instante. Assim o valor desce para o código chamado depois, mas um `set` feito no filho não volta para o pai:

```python
def filho():
    print("filho leu:", current_user.get())
    current_user.set("bia")
    print("filho mudou para:", current_user.get())

current_user.set("ana")
copia = copy_context()
copia.run(filho)
print("pai continua:", current_user.get())
```

```
filho leu: ana
filho mudou para: bia
pai continua: ana
```

## A declaração

```python
current_user: ContextVar[UUID | None] = ContextVar("current_user", default=None)
```

| Parte | Para que serve |
|---|---|
| `: ContextVar[UUID \| None]` | anotação para o mypy: a chave guarda `UUID` ou `None`; sem ela, o `default=None` faz o mypy aceitar só `None` |
| `"current_user"` | rótulo para depuração; a busca usa o objeto, não esse texto |
| `default=None` | o que o `.get()` devolve sem um `.set()` naquele contexto |

A linha roda uma vez, no [[Módulo Python|import do módulo]], e cria um objeto só para todos os pedidos.

> [!warning] Erros comuns
> - Achar que o `get` devolve o último `set`: ele lê o contexto atual, por mais pedidos que tenham chegado depois.
> - Guardar o valor em um atributo próprio (`self.valor = value`): volta o problema da global comum.
> - Criar uma `threading.Thread` na mão: ela não recebe a cópia, e o `get` devolve o `default`.

> [!example] Exemplo de uso
> O [[Login no navegador]] guarda o id de quem pediu em uma `ContextVar` antes da rota e lê esse id ao abrir a [[Transação|transação]].

## Fontes

- [contextvars, documentação do Python](https://docs.python.org/3/library/contextvars.html)
- saídas conferidas em 2026-11-05 com Python 3.14.8.
