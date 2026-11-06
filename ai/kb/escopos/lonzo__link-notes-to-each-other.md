---
id: lonzo/link-notes-to-each-other
nome: A IA escreve links e formatos que o editor mostra (issue #149)
areas: [ia]
---
## Pedido
1. O `base_rules.md` ensina a IA a ligar notas com `[palavra](note:<id>)`, com o id vindo das ferramentas.
2. O `base_rules.md` lista todos os formatos de Markdown que o editor mostra e os que ficam como texto cru.

## Contexto
- Só o prompt muda; o código do lonzo fica igual.
- Lista conferida em `apps/chimchar/src/decorations/preview.ts`.
- As notas com `[[Título|palavra]]` foram corrigidas direto no banco local, sem commit.

## Fora
- Link clicável na resposta do chat: o DOMPurify tira o `href` de `note:` (chimchar).
- Link dentro de célula de tabela e link para site no editor (chimchar).
- Fórmula renderizada na nota (chimchar).
