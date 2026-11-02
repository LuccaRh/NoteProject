---
id: ichiro/search-notes-with-postgres-full-text-search
nome: Busca nas notas com full-text search do Postgres (issue #56)
areas: [servidor, dados]
---
## Pedido (o que a branch entrega; cada item verificável)
1. Migration: índice GIN sobre `to_tsvector('simple', title || ' ' || body)`, sem
   coluna nova na tabela.
2. `GET /notes/search?q=...` (pelo Caddy, `/api/notes/search`) devolve as notas (não
   pastas) cujo título ou corpo tem as palavras, como `[{id, title}]`, em ordem de
   título, sem limite; `parent_id` opcional busca só dentro da pasta, em qualquer
   profundidade (404 se não existe); `q` vazio → 422.
3. Testes da busca passando contra o Postgres (`make check`); versão 0.12.0 → 0.13.0.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- Camadas: `routers/notes.py` → `services/notes.py` → `repositories/notes.py`; modelo
  novo em `schemas/notes.py`.
- Sem ranking (`ts_rank`) nem trecho (`ts_headline`): a busca só lista para escolher, e
  a resposta curta gasta menos tokens da IA (2026-11-02, conversa com o Lucca).

## Fora (vira outra branch)
- Campo de busca no front (chimchar).
- Busca pela IA (#77), filtro por pasta, acento ignorado (`unaccent`).
