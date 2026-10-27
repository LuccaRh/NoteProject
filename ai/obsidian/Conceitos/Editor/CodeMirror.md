---
tags: [noteproject, conceito, editor]
---
# CodeMirror

Um editor de [[Markdown]] guarda texto puro, mas a tela precisa mostrar heading grande, chip, figura.

- **CodeMirror 6**: editor de texto para a web, montado a partir de extensões. O documento é sempre texto.
- **Decoração**: muda como um trecho aparece, sem mudar o texto. Quatro tipos (`@codemirror/view` 6.43.6, `index.d.ts:331-346`):

| Tipo | Faz | Uso típico |
|---|---|---|
| `mark` | estilo num trecho | negrito, link colorido |
| `line` | estilo na linha inteira | heading com tamanho maior |
| `widget` | insere um elemento na tela | botão, contador |
| `replace` | esconde o trecho e mostra um elemento no lugar | chip no lugar de um marcador, figura no lugar do link |

- O `replace` é o que deixa o texto guardar só um marcador curto e a tela mostrar a coisa.

> [!example] No NoteProject
> Headings usam `line`; os chips de `[!duvida]` vão usar `replace` ([[Front — editor e UI]]).

Doc: [CodeMirror — guia](https://codemirror.net/docs/guide/).
