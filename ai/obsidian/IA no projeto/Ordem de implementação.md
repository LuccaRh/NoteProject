---
tags: [noteproject, ia, plano]
---
# Ordem de implementação

As partes sem IA vêm antes: elas já servem sozinhas e são o que a IA usa depois. Cada item é uma branch e uma issue do [[Roadmap]]: os itens sem IA na milestone Editor (o item 1 é a #5), os com IA na milestone AI in the app, depois da v1 ([[Objetivo do app]]).

| # | Item | IA? | Página |
|---|---|---|---|
| 1 | chips para `[!duvida]` e `[!fix]` (`decorations/replace.ts`): fecha a branch atual | não | [[Marcar dúvida]] |
| 2 | `Ctrl+D` + tabela `pedidos` no [[Postgres e migrations\|Postgres]] do servidor (`apps/notes`) | não | [[Marcar dúvida]] |
| 3 | operação por âncora + sugestão com `Tab`/`Esc` | não | [[Edição por âncora]] |
| 4 | moldes de bloco + menu `/` | não | [[Blocos padronizados]] |
| 5 | worker da fila em `apps/worker`, no servidor ([[Navegador]]): `claude_cli` (só o dono), depois `anthropic` e `ollama` | sim | [[Fila de pedidos]] |
| 6 | servidor [[MCP]] com 4 ferramentas, para agente de fora; testar no es728 | sim | [[MCP — a IA como cliente do daemon]] |
| 7 | classificação de tema | sim | [[Classificar a nota pelo tema]] |
| 8 | figuras: Mermaid (só no front) → `diagrama.py` → scripts | parte | [[Figuras geradas]] |

- O item 3 dá para testar com uma operação escrita à mão, antes de existir IA.
- Depois do item 5 já dá para trocar o Obsidian pelo app em uma matéria e comparar o gasto ([[Gastar poucos tokens#Medir, não supor]]).
