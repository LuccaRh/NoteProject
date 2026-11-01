---
tags: [noteproject, ia, plano]
---
# Ordem de implementação

O primeiro uso da IA no app é o [[Chat com o workspace|chat com o workspace]]: é o que substitui o Claude Code no dia a dia, de qualquer aparelho, e as peças dele (workspace em notas, ferramentas de nota, [[Laço de ferramentas|laço]]) são as que o resto usa depois. Cada item é uma branch e uma issue do [[Roadmap]].

| # | Item | IA? | Issue | Página |
|---|---|---|---|---|
| 1 | serviço `lonzo` com a lib `anthropic`, respondendo com as regras de um `.md` no `system` | sim | #74 | [[Chat com o workspace]] |
| 2 | workspaces: qualquer pasta com `.workspace/`, que o `lonzo` cria preenchendo um esqueleto a partir de um texto breve; as regras dele passam a ir no `system` | sim | #73 (parte da #42) | [[Workspace no app#Como nasce]] |
| 3 | conversas no banco do `lonzo` + tela de chat | sim | #75, #76 | [[Chat com o workspace]] |
| 4 | ferramentas de nota no chat (`search_notes`, `list_folder`, `read_note`, `create_note`, `edit_note`, `delete_note`), presas ao workspace: a IA monta o workspace | sim | #77, #78 | [[Chat com o workspace#Ferramentas]] |
| 5 | operação por âncora + sugestão com `Tab`/`Esc`: a edição da IA vira proposta | não | #32 | [[Edição por âncora]] |
| 6 | scripts do `.workspace/` em [[Sandbox\|sandbox]] | sim | a abrir | [[Workspace no app#Scripts]] |
| 7 | servidor [[MCP]] para agente de fora (o Claude Code no PC) | sim | #34 | [[MCP — a IA como cliente do daemon]] |
| 8 | moldes de bloco + menu `/` | não | #33 | [[Blocos padronizados]] |
| 9 | worker da fila em `apps/worker`, para pedidos em segundo plano | sim | #35 | [[Fila de pedidos]] |
| 10 | classificação de tema | sim | #36 | [[Classificar a nota pelo tema]] |
| 11 | figuras: Mermaid (só no front) → `diagrama.py` → scripts | parte | #37 | [[Figuras geradas]] |

- O item 5 dá para testar com uma operação escrita à mão, antes do chat editar notas.
- Depois do item 4 já dá para trocar o Claude Code pelo chat em uma matéria e comparar o gasto ([[Gastar poucos tokens#Medir, não supor]]).

## Depois, sem data

A [[Marcar dúvida|marcação de dúvida]] (`Ctrl+D`, #31) e os chips de `[!duvida]` e `[!fix]` no editor (#5) saem da fila: o chat cobre a pergunta sobre um trecho, e a marcação à mão deixou de ser usada.
