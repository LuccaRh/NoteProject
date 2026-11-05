---
id: chimchar/clear-the-tree-selection-on-an-empty-click
nome: Clicar no vazio da árvore limpa a seleção (issue #143)
areas: [ui]
---
## Pedido (o que a branch entrega; cada item verificável)
1. Clicar no espaço vazio da árvore limpa a seleção, e o que for criado depois vai para a raiz.
2. A árvore ocupa a altura livre da sidebar, com folga no fim para sempre sobrar espaço vazio.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- `notes/tree.ts` e `style.css`. O `create` do `main.ts` já manda `parent_id: tree.target()`, `null` sem seleção.
- A branch sai da `lonzo/complete-the-agent-behind-the-chat`, a pedido do usuário (2026-11-05).

## Fora (vira outra branch)
- Manter um destaque na nota aberta depois de limpar a seleção.
