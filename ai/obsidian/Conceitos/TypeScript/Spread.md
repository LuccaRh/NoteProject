---
tags: [noteproject, conceito, ui]
---
# Spread

Às vezes os valores estão numa lista, mas a função quer cada um num argumento separado. O spread `...` desmonta a lista: cada item vira um argumento, seja qual for o tamanho dela. É o `*lista` do Python.

```ts
const rows = [li1, li2, li3]

list.replaceChildren(...rows)   // replaceChildren(li1, li2, li3)
list.replaceChildren(rows)      // replaceChildren([li1, li2, li3]): um argumento só
```

O spread não olha quantos parâmetros a função pede: 10 itens viram 10 argumentos, lista vazia vira nenhum.

## Os lugares do `...`

O mesmo `...` faz o contrário quando está do lado de quem **recebe** (o rest): junta os argumentos soltos numa lista.

| Onde | Nome | TypeScript | Python |
|---|---|---|---|
| na chamada | spread | `f(...lista)` | `f(*lista)` |
| dentro de lista | spread | `[...a, ...b]` | `[*a, *b]` |
| dentro de objeto | spread | `{ ...a, ...b }` | `{**a, **b}` |
| no parâmetro | rest | `function f(...itens)` | `def f(*itens)` |

- Uma função que aceita qualquer quantidade de argumentos foi definida com rest (`replaceChildren(...nodes)`); quem chama com uma lista usa spread.
- No objeto, quem vem depois ganha: `{ ...antigo, ...novo }` fica com o valor de `novo` nas chaves repetidas.

> [!warning] Erros comuns
> - Achar que o spread copia fundo: `{ ...a }` é uma cópia rasa; um objeto dentro de `a` continua o mesmo nas duas.
> - Esquecer o `...` ao passar uma lista para função de rest: o TS acusa o tipo errado (a lista inteira chega como um item).

> [!example] No NoteProject
> A lista de notas é redesenhada com `replaceChildren(...this.rows(null, 0))` ([[Como ler o front]]).

Docs: [MDN — Spread syntax](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Spread_syntax).
