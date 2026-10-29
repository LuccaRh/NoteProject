---
tags: [noteproject, conceito, ui]
---
# Callback

Uma peça que avisa um acontecimento (um clique, uma resposta) nem sempre sabe o que fazer com ele. A saída é receber de fora uma função e chamá-la quando o acontecimento vier: o callback. Quem cria a peça decide o que acontece; a peça só avisa.

```ts
button.addEventListener('click', () => save())   // o navegador chama save a cada clique
```

O Python faz o mesmo: `sorted(notas, key=lambda n: n.title)` passa uma função que o `sorted` chama para cada item.

## Vários callbacks num objeto

Quando a peça avisa várias coisas, os callbacks vão juntos num objeto, com um `type` que diz o formato (como um `TypedDict`):

```ts
type Handlers = {
    open: (note: Note) => void
    remove: (note: Note) => void
}

const tree = new Tree(list, {
    open: note => page.open(note.id),
    remove: note => remove(note),
})
```

- A peça guarda o objeto e chama `this.handlers.open(note)` no clique.
- Se faltar um campo, o `tsc` dá erro antes de rodar.
- A peça não conhece quem recebe o aviso: dá para trocar o que acontece sem mexer nela, e quem liga as peças fica num lugar só.

> [!warning] Erros comuns
> - Chamar em vez de passar: `addEventListener('click', save())` roda `save` uma vez, na hora, e passa o resultado. O certo é `save` ou `() => save()`.
> [!example] No NoteProject
> A lista de notas avisa abrir, renomear e apagar por `Handlers`; o `main.ts` decide o que cada um faz ([[Como ler o front]]).

Docs: [MDN — Callback function](https://developer.mozilla.org/en-US/docs/Glossary/Callback_function).
