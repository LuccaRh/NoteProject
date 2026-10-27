---
id: notes/expose-the-notes-api-on-the-server
nome: Rotas /notes no serviço notes, com Postgres (issue #46)
areas: [servidor, dados]
---
## Pedido (o que a branch entrega; cada item verificável)
1. Rotas `/notes` no `apps/notes`: criar, ler, listar, editar e apagar nota, gravando no Postgres.
2. Testes das rotas contra o Postgres; `make check` passa.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- Notas `Estrutura do projeto/Navegador`, `Estrutura do projeto/API de notas`, `Conceitos/Banco de dados/Postgres`.
- Regra nova de branch por serviço (W13, `CLAUDE.md`, `Regras de git`) e as notas de issues feitas trazidas unstaged.

## Fora (vira outra branch)
- Lado do front da #46 (front novo, do zero: cliente da API, proxy `/api` do Vite, editor criando e editando notas): PR próprio `web/...` na mesma issue, depois do merge deste.
- Busca `/search` com full-text do Postgres (#56).
- Servir o build (#47); pastas, campos e views (#6–#9); login (M2).
