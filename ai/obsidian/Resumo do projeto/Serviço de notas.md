---
tags: [noteproject, dados, servidor]
---
# Serviço de notas

O `ichiro` guarda notas e pastas e responde busca. É a fonte única das notas: o front e a IA passam por ele. Mais detalhe das rotas em [[API de notas]].

## Modelo de dados

Uma tabela só, `notes`, em que pasta e nota são linhas: a [[Árvore no banco|árvore]] é uma lista de adjacência (cada linha aponta para o pai).

| Coluna | Para quê |
|---|---|
| `id uuid` | `uuidv7()` do Postgres 18: ordenado no tempo, bom para [[Índice\|índice]] B-tree |
| `parent_id` | FK para `notes.id`, `ON DELETE CASCADE`: apagar a pasta apaga o que está dentro; `NULL` = raiz |
| `is_folder` | pasta ou nota |
| `title`, `body` | texto; o corpo é Markdown puro |
| `owner_id` | dono; default = usuário do pedido ([[Isolamento por usuário]]) |
| `created_at`, `updated_at` | `timestamptz` |

- Título único por pasta de cada dono: `UNIQUE NULLS NOT DISTINCT (owner_id, parent_id, title)`. O `NULLS NOT DISTINCT` faz a raiz (`parent_id NULL`) também contar, senão dois `NULL` seriam "diferentes".
- Violação de unicidade (`IntegrityError`) sai do repository já como erro do domínio (`TitleTaken` → 409).

## Consultas da árvore

Tudo que anda na árvore é uma CTE `WITH RECURSIVE`, uma ida ao banco em vez de uma consulta por nível:

- `/notes/tree`: a subárvore inteira com o caminho de cada nota.
- `/notes/{id}/path`: sobe até a raiz e monta `a/b/c`.
- `/notes/by-path?path=a/b`: desce título por título.
- `/notes/{id}/above?path=.workspace/CLAUDE.md`: a nota com esse caminho em cada pasta acima, da raiz para baixo; é o que dá à IA as regras de cada workspace acima da conversa ([[Ferramentas e contexto da IA]]).
- Mover para dentro de si mesmo é barrado (`ParentInsideNote`): uma CTE confere se o novo pai é descendente.

## Busca

| Rota | Como | Por quê |
|---|---|---|
| `/notes/search` | [[Busca full-text no Postgres\|full-text]]: `to_tsvector('simple', title \|\| ' ' \|\| body) @@ websearch_to_tsquery('simple', :q)` | índice GIN na mesma expressão; `websearch_to_tsquery` aceita aspas e `-palavra` sem quebrar com entrada de usuário |
| `/notes/search-titles` | `title ILIKE '%' \|\| :q \|\| '%'` com `%` e `_` escapados | achar pelo pedaço do título; a tabela é pequena, sem índice trigram |

- Dicionário `simple` (sem stemming): as notas misturam português e inglês, e o stemming de uma língua erraria na outra. Custo: "nota" não acha "notas".
- As duas aceitam `folder_id`: a CTE limita a busca à subárvore.

## Pedido até o banco

1. Middleware `read_user` lê o `X-User-Id` e guarda numa [[ContextVar]].
2. Router chama um service; o service abre `with transaction() as conn:` ([[Context manager|context manager]] sobre `engine.begin()`).
3. A transação começa com `set_config('app.user_id', ..., true)`; o RLS filtra as linhas.
4. Repository roda SQL com `text()` do [[SQLAlchemy]] Core e devolve modelo Pydantic do `schemas/`.

- Rotas `def` (síncronas): o FastAPI as roda num threadpool; a `ContextVar` é copiada para a thread, então o usuário chega ao `set_user`.
- Pool de conexões do SQLAlchemy global em `db.py`; conexão nunca é global (os pedidos dividiriam a transação).

## Se perguntarem

- **"Por que lista de adjacência e não materialized path / ltree?"** Mover uma pasta muda uma linha só; o custo de ler a árvore fica numa CTE recursiva, barata no tamanho de um vault pessoal.
- **"Por que SQL na mão e não ORM?"** Consultas recursivas e de busca ficam legíveis em SQL; o Core dá o pool, os parâmetros e as transações sem esconder a consulta.
- **"Como evita SQL injection?"** Todo valor vai por parâmetro (`:q`), nunca por f-string; no `ILIKE`, os curingas da entrada também são escapados.
