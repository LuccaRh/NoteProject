---
tags: [noteproject, prova, dados]
---
# Questões de banco de dados

O [[Postgres]] do `ichiro`: schema, conexões e a tabela de notas ([[Issues 12 e 13 — Postgres com migrations e .env|#12]], [[Issue 46 — Expose the notes API on the server|#46]]).

## 1. A imagem `postgres` cria a tabela `notes` na primeira vez que sobe?

> [!note]- Resposta
> Não. Ela só cria o usuário e o banco, e só com a pasta de dados vazia. A tabela vem da [[Migration|migration]] ([[Postgres]]).

## 2. O que é uma migration, e o que fazem `upgrade` e `downgrade`?

> [!note]- Resposta
> Um arquivo versionado que muda o schema. As revisões do Alembic se encadeiam como commits; `upgrade` aplica, `downgrade` reverte, e aplicadas em ordem levam qualquer banco ao schema atual ([[Migration]]).

## 3. Como o Alembic sabe em qual banco aplicar?

> [!note]- Resposta
> O `migrations/env.py` lê a `DATABASE_URL`, que vem do `.env` pelo `env_file` do compose. A API cria a engine com a mesma URL ([[API de notas]]).

## 4. Para que serve o pool de conexões da engine do [[SQLAlchemy]]?

> [!note]- Resposta
> Abrir conexão com o Postgres custa (TCP, autenticação). A engine guarda conexões abertas e empresta uma por pedido, que volta ao pool no fim ([[SQLAlchemy]]).

## 5. Apagar uma pasta apaga as notas de dentro. Por que isso precisa de uma [[Transação|transação]]?

> [!note]- Resposta
> As duas coisas só valem juntas. Dentro de `BEGIN`…`COMMIT`, ou tudo é gravado de uma vez, ou um erro no meio faz `ROLLBACK` e nada muda ([[Transação]]).

## 6. Como uma tabela plana guarda pastas dentro de pastas?

> [!note]- Resposta
> Cada linha aponta para o pai (`parent_id`, lista de adjacência), e a pasta é uma nota com `is_folder`. Os filhos de uma pasta são `WHERE parent_id = X` ([[Árvore no banco]], [[Pastas, campos e views]]).

## 7. `PATCH /notes/5` com `parent_id = 5`, sendo 5 uma pasta. Qual a resposta, e por quê?

> [!note]- Resposta
> 422: uma pasta não pode ficar dentro dela mesma. O mesmo vale para pai que não existe ou não é pasta ([[Issue 46 — Expose the notes API on the server|#46]]).

## 8. Por que o texto da nota fica numa coluna `TEXT` e não num bucket [[S3]]?

> [!note]- Resposta
> Salvar vira um `UPDATE` numa transação, e a busca enxerga o conteúdo. O [[S3]] fica para arquivos grandes ([[Issues 12 e 13 — Postgres com migrations e .env|#12]], [[Marcador no texto, conteúdo fora]]).

## 9. Uma migration cria a coluna `pinned`. Ela aparece no JSON de `GET /notes/{id}`?

> [!note]- Resposta
> Não sozinha. Só aparece se entrar no modelo Pydantic (`schemas/notes.py`) e na lista de colunas da consulta: schema e tabela andam juntos sem ser a mesma coisa ([[API de notas]]).

## 10. Como os testes do `ichiro` deixam o banco limpo entre um teste e outro?

> [!note]- Resposta
> O banco é migrado uma vez por sessão; cada teste roda dentro de uma transação que volta no fim (`rollback`), com um savepoint por pedido ([[Issue 46 — Expose the notes API on the server|#46]]).

## 11. Todos os testes caem com `Connection refused`. Qual a causa mais provável?

> [!note]- Resposta
> O container do Postgres não está de pé: os testes falam com ele por `localhost:5432` ([[Issue 46 — Expose the notes API on the server|#46]], [[Comandos do Docker no dev]]).

## 12. Escreva o comando para abrir o `psql` no banco do compose.

> [!note]- Resposta
> `dc exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'`: o `sh -c` faz as variáveis serem lidas dentro do container, onde o `.env` as pôs ([[Comandos do Docker no dev]]).
