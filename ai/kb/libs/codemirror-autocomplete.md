---
pacote: "@codemirror/autocomplete"
versao: 6.20.4
fonte: apps/chimchar/node_modules/@codemirror/autocomplete/dist/index.d.ts
areas: [editor]
---
# @codemirror/autocomplete — lista depois de `[[`

Card destilado dos tipos instalados (fonte acima, linhas citadas). Uso: `notes/links.ts`.

| API | Faz | d.ts |
|---|---|---|
| `autocompletion(config)` | liga a lista no editor | 610 |
| `override` | só estas fontes; sem ele, o `markdown()` também completaria tags HTML | 360 |
| `icons: false` | tira o ícone de cada opção | 399 |
| `Completion.apply` | string, ou função `(view, completion, from, to)` que faz a edição | 48 |
| `CompletionResult.from` | início do texto usado para filtrar | 247 |
| `validFor` | enquanto casar, filtra a mesma lista sem chamar a fonte de novo | 268 |
| `insertCompletionText` | monta a troca de `from..to` pelo texto | 323 |
| `pickedCompletion` | anotação do transaction de uma opção escolhida; o `apply` em função a repõe | 317 |

O `from` do resultado fica depois do `[[`, para filtrar só o que veio depois; por isso o `apply` volta dois caracteres.
