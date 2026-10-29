---
id: web/list-create-and-edit-notes-in-the-editor
nome: Front do CRUD de notas no editor, pela API (issue #62)
areas: [cliente-api, ui, editor]
---
## Pedido (o que a branch entrega; cada item verificável)
1. Cliente da API (`apps/web/src/notes/api.ts`) chamando as rotas `/notes` pelo proxy `/api` do Vite (`:8000`).
2. Lista de notas no front: abrir, criar, renomear e apagar nota no servidor.
3. A nota aberta no editor salva sozinha; `make check` passa.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- Notas `Estrutura do projeto/Navegador`, `Estrutura do projeto/Front — editor e UI`, `Estrutura do projeto/API de notas`.
- Separar a #46 (só back) da #62 nas notas do plano e tirar do vault e do `CLAUDE.md` a ideia de "trazer de volta" a sidebar; `.sync.json` atrasado da branch anterior.

## Fora (vira outra branch)
- Mudança nas rotas do `apps/notes` (#46 já mergeada): se faltar algo, PR `notes/...` próprio.
- Proxy `/api` do Vite (#64, branch `web/proxy-api-requests-to-the-notes-service`, base desta).
- Busca `/search` (#56); servir o build (#47); pastas, campos e views (#6–#9); login (M2).
