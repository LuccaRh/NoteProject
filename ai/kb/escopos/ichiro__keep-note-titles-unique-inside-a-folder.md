---
id: ichiro/keep-note-titles-unique-inside-a-folder
nome: Título único dentro de cada pasta (issue #90)
areas: [dados, servidor]
---
## Pedido (o que a branch entrega; cada item verificável)
1. Migration: `UNIQUE NULLS NOT DISTINCT (parent_id, title)` na `notes`
   (`notes_parent_id_title_key`); na raiz (`parent_id` NULL) também vale.
2. `POST /notes` e `PATCH /notes/{id}` (renomear ou mover) com título que já existe na pasta
   → 409 `title already in folder`; o outro `IntegrityError` (pai apagado no meio) segue 422.
3. Testes do 409 (criar, raiz, renomear, mover) e do mesmo título em outra pasta; versão do
   ichiro 0.8.0 → 0.9.0.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- (2026-11-02, pedido do Lucca, escrito pela sessão) Empilhada na #89. Vem do lonzo: o `create`
  das ferramentas confere o título e depois grava (duas chamadas, com corrida); com a
  constraint, o banco garante e o lonzo trata o 409. Base para a nota por caminho (#91): um
  caminho aponta para uma nota só.
- `NULLS NOT DISTINCT` precisa do Postgres 15+ (o compose usa o 18). SQL puro no `op.execute`.
- O 409 sai de `isinstance(error.orig, UniqueViolation)` (psycopg 3.3.6,
  `psycopg/errors.py:1055`): a única outra unique é a PK, que o banco gera.
- `errors/notes.py` mexido: docstrings (W21) num commit próprio.

## Fora (vira outra branch)
- Tratar o 409 no lonzo e no front (hoje o front mostra o erro genérico).
- Banco de teste separado do de dev: os testes rodam no banco de dev (com rollback), e uma
  nota real na raiz com título de teste (`Work`, `Plan`) faria o teste dar 409.
