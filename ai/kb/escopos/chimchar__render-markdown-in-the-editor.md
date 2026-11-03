---
id: chimchar/render-markdown-in-the-editor
nome: Editor mostra o Markdown renderizado (live preview) (issue #117)
areas: [editor]
---
## Pedido (o que a branch entrega; cada item verificável)
1. Títulos `#`–`######` em tamanho de título, com o `#` escondido fora da linha do cursor.
2. Tabela GFM vira tabela de verdade fora do cursor; clicar nela volta ao texto.
3. Bloco de código (```` ``` ````) em caixa monoespaçada, com cor da linguagem e as cercas
   escondidas fora do cursor; código inline com fundo e sem as crases.
4. Negrito, itálico, riscado, link, citação, lista e linha horizontal sem as marcas fora do
   cursor.
5. Conferido no navegador com a nota "Arrow function" (print do Lucca).

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- Pedido pelo Lucca a partir de um print do editor mostrando o Markdown cru; branch em cima
  da `chimchar/keep-host-files-out-of-the-build-context` (#51).
- `markdown({base: markdownLanguage})` liga o GFM (tabela, riscado); `codeLanguages` vem do
  `@codemirror/language-data`, que já é dependência.
- Tabela é bloco que cobre várias linhas: precisa de `StateField`, não `ViewPlugin`
  (card `codemirror-view`, d.ts:1310–1314).

## Fora (vira outra branch)
- Checkbox de tarefa (`- [ ]`) clicável, figuras Mermaid (#37), chips (#5), imagens.
- Editar a tabela dentro do widget.
