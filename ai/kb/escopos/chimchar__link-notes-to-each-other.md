---
id: chimchar/link-notes-to-each-other
nome: Links entre notas no editor (issue #149)
areas: [editor, ui]
---
## Pedido
1. Digitar `[[` no editor lista as notas da pessoa, sem pastas, filtrando pelo que se digita depois.
2. Escolher uma nota grava `[Título](note:<uuid>)` no lugar do `[[`.
3. Clicar no link abre a nota numa aba.
4. Link de nota que não abre (apagada, ou de outro owner) avisa no status da página.

## Contexto
- `notes/links.ts` (novo), `editor.ts`, `notes/page.ts`, `notes/search.ts`, `decorations/preview.ts`, `main.ts`, `style.css`.
- Só com rotas e funções de `notes/api.ts` que já existem; o owner é garantido pela policy do banco.
- `@codemirror/autocomplete` já vem pelo `codemirror`; passa a dependência direta.

## Fora
- Backlinks e aviso ao apagar nota com links (tabela `note_links`, mudança de modelo de dados).
- Título do link acompanhar a renomeação da nota.
- Link para um ponto da página (item 18 de `Prioridade das features`).
- Link dentro do chat (`chat/markdown.ts`) e a IA escrever links.
- Abrir link externo (`https:`) ao clicar.
