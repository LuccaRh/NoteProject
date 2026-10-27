---
tags: [noteproject, conceito, infra]
---
# Backup

Disco quebra, um comando apaga a tabela errada, a máquina é recriada. Se a única cópia está na própria máquina, some junto.

- **Backup**: cópia dos dados **fora** da máquina, feita sozinha e com frequência.
- **Restore**: voltar a cópia num banco vazio. Backup nunca restaurado não está provado.

| O quê | Como | Para onde |
|---|---|---|
| banco [[Postgres]] | `pg_dump` por cron | um bucket [[S3]] |
| arquivos grandes | já guardados num [[S3]] | — |

- `pg_dump` gera um arquivo que recria o banco; `pg_restore` (ou `psql`) o aplica.

> [!example] No NoteProject
> Cópia diária do Postgres no S3, com um restore feito antes de fechar a M2 ([[Infra — deploy e operação]]).

Doc: [pg_dump](https://www.postgresql.org/docs/current/app-pgdump.html).
