---
tags: [noteproject, conceito, ui]
---
# Nullish coalescing

Um valor que pode faltar (`null` ou `undefined`) precisa de um substituto antes de ser usado. O `??` dá esse substituto: `a ?? b` é `a`, salvo quando `a` é `null` ou `undefined`; aí vira `b`. Lê-se "a, senão b".

```ts
const key = parentId ?? 'root'   // null → 'root'; 'abc' → 'abc'
```

Em Python: `key = parent_id if parent_id is not None else 'root'`.

## `??` × `||`

O `||` troca qualquer valor "falso", e não só o que falta. A diferença aparece com `0`, `''` e `false`:

| `a` | `a ?? 'x'` | `a \|\| 'x'` |
|---|---|---|
| `null` | `'x'` | `'x'` |
| `undefined` | `'x'` | `'x'` |
| `''` | `''` | `'x'` |
| `0` | `0` | `'x'` |
| `false` | `false` | `'x'` |

O `||` é o `a or b` do Python. Para "usar o padrão só quando não veio nada", o certo é o `??`.

## Parentes

- `a?.b`: lê `b` só se `a` existe; senão dá `undefined` sem erro (`page.note?.id`).
- `a ??= b`: põe `b` em `a` só se `a` está faltando.
- `lista ?? []`: padrão comum para "se não tem, conta como vazio".

> [!example] No NoteProject
> A pasta raiz chega como `null` da API e vira a chave `'root'` do cache da lista ([[Como ler o front]]).

Docs: [MDN — Nullish coalescing operator](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Nullish_coalescing).
