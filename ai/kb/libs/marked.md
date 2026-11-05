---
pacote: marked
versao: 18.1.3
fonte: apps/chimchar/node_modules/marked/lib/marked.d.ts
areas: [ui]
---
# marked — Markdown em HTML nas respostas do chat

Card destilado do código instalado (fonte acima). Uso em `apps/chimchar/src/chat/markdown.ts`.

- `new Marked(...MarkedExtension)`: instância própria, com `breaks`, em vez de mexer no global.
- `parse(src, { async: false })` devolve `string`, não `Promise` (linha 756 do d.ts).
- Extensão inline (`TokenizerExtension & RendererExtension`, linhas 427–442): `start` diz onde
  cortar o texto e `tokenizer` lê no começo do que sobrou. Dentro de `` `código` `` não roda.
- marked não sanitiza: a saída passa pelo DOMPurify antes de ir para o `innerHTML`.
