---
tags: [noteproject, conceito, ui]
---
# Arrow function

No JavaScript, função é um valor como outro qualquer: dá para guardar numa variável ou passar a outra função ([[Callback]]). Para essas funções curtas, sem nome, existe a arrow function: parâmetros à esquerda do `=>`, o resultado à direita. É o `lambda` do Python, e vem do JavaScript (o TypeScript só acrescenta os tipos).

| TypeScript | Python |
|---|---|
| `note => note.title` | `lambda note: note.title` |
| `(a, b) => a + b` | `lambda a, b: a + b` |
| `() => load()` | `lambda: load()` |
| `(n: Note): string => n.title` | (com tipos) |

## Com corpo

Entre `{ }` cabem várias linhas, como num `def`; aí o valor só sai com `return`:

```ts
const soma = (a: number, b: number) => {
    const total = a + b
    return total
}
```

Sem `{ }`, o resultado da expressão já é o retorno (`a => a * 2` devolve `a * 2`).

## O `this` de fora

A arrow function não tem `this` próprio: usa o do lugar onde foi escrita. Dentro de um método de classe, `() => this.save()` continua falando do mesmo objeto quando outra parte do código chama a função depois. Uma `function () { this.save() }` comum perderia esse `this`.

> [!warning] Erros comuns
> - Devolver objeto sem parênteses: `x => { a: 1 }` é um corpo com um rótulo, devolve `undefined`. O certo é `x => ({ a: 1 })`.
> - Esquecer o `return` quando há `{ }`: a função devolve `undefined`.

> [!example] No NoteProject
> Os cliques da lista de notas viram arrow functions passadas no `new Tree(...)` ([[Como ler o front]]).

Docs: [MDN — Arrow function expressions](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/Arrow_functions).
