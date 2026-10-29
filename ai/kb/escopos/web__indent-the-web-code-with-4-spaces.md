---
id: web/indent-the-web-code-with-4-spaces
nome: Indentação de 4 espaços no código do web (issue #65)
areas: [editor, ui]
---
## Pedido (o que a branch entrega; cada item verificável)
1. `.editorconfig` na raiz: 4 espaços (YAML e JSON do npm com 2, Makefile com tab).
2. `apps/web` (`index.html`, `editor.ts`, `decorations/headings.ts`, `vite.config.ts`) com 4 espaços; `make check` passa.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- Primeira da fila do web: a #64 (proxy) e a #62 (CRUD) saem desta, já no formato.

## Fora (vira outra branch)
- Proxy `/api` (#64) e cliente/lista de notas (#62).
- Mudança de comportamento no editor.
