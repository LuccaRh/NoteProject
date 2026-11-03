---
id: ichiro/search-notes-by-title
nome: Busca de notas e pastas pelo título (issue #107)
areas: [servidor, dados]
---
## Pedido (o que a branch entrega; cada item verificável)
1. `GET /notes/search-titles?q=...` devolve notas e pastas cujo título contém o texto,
   mesmo no meio da palavra, como `[{id, title, is_folder}]`, em ordem de título;
   `parent_id` opcional busca só dentro da pasta, em qualquer profundidade (404 se não
   existe); `q` vazio → 422.
2. `ILIKE` no título, sem índice nem migration; `%` e `_` do texto valem como letra.
3. O filtro por pasta é o mesmo da `GET /notes/search` (trecho de SQL escrito uma vez).
4. Testes passando contra o Postgres (`make check`); versão 0.13.0 → 0.14.0.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- A branch sai da `ichiro/search-notes-with-postgres-full-text-search` (#56) e vai para
  cima da `master` quando ela for mergeada.

## Fora (vira outra branch)
- Campo de busca no front (chimchar).
