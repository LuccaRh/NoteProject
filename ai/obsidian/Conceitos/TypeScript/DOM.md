---
tags: [noteproject, conceito, ui]
---
# DOM

O HTML chega ao navegador como texto. Para desenhar a página, o navegador transforma esse texto numa árvore de objetos, um por tag: o DOM (Document Object Model). O JavaScript mexe nessa árvore, e a tela acompanha na hora.

```
<ul id="tree">          →   ul#tree
  <li>Inbox</li>              ├── li  "Inbox"
  <li>Work</li>               └── li  "Work"
</ul>
```

## O que dá para fazer

| Para | Chamada | Devolve |
|---|---|---|
| achar pelo id | `document.getElementById('tree')` | o elemento, ou `null` se não existe |
| achar por seletor CSS | `document.querySelector('.tree li')` | o primeiro que casa, ou `null` |
| criar | `document.createElement('li')` | um elemento solto, ainda fora da página |
| pôr dentro | `pai.append(a, b)` | — (acrescenta no fim) |
| trocar o conteúdo | `pai.replaceChildren(a, b)` | — (apaga os filhos e põe estes; sem argumento, esvazia) |
| texto | `el.textContent = 'oi'` | — (texto puro, nunca vira tag) |
| esconder | `el.hidden = true` | — (o mesmo que o atributo `hidden` no HTML) |
| reagir | `el.addEventListener('click', f)` | — (chama `f` a cada clique; ver [[Callback]]) |

Essas funções são do navegador, não do JavaScript nem do TypeScript: no Python (fora do navegador) não existem.

## No TypeScript

- O TS conhece o DOM pelos tipos em `typescript/lib/lib.dom.d.ts`: cada tag tem o seu (`HTMLInputElement` tem `.value`, `HTMLElement` não).
- `getElementById` devolve `HTMLElement | null`. Com o TS estrito, usar o resultado sem tratar o `null` é erro de compilação; uma função pequena que confere e lança erro com o id evita repetir o `if` a cada elemento.
- `el as HTMLInputElement` é só uma promessa ao compilador: se a tag for outra, o TS não percebe.

> [!warning] Erros comuns
> - `innerHTML` com texto do usuário: um título `<img onerror=...>` vira tag e roda código (XSS). Texto do usuário vai por `textContent`.
> - Procurar o elemento antes de ele existir: um `<script>` no `<head>` sem `type="module"` roda antes do `<body>`, e o `getElementById` volta `null`.

> [!example] No NoteProject
> A lista de notas é um `<ul>` que o front esvazia e preenche de novo com `replaceChildren` a cada mudança ([[Como ler o front]]).

Docs: [MDN — Introduction to the DOM](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Introduction).
