---
tags: [noteproject, conceito, servidor]
---
# Postgres e migrations

No dispositivo, um arquivo [[SQLite e FTS5|SQLite]] basta: só um programa escreve. Num servidor, vários clientes escrevem ao mesmo tempo, e o banco tem de rodar como serviço e ser copiado com segurança.

- **Postgres**: banco relacional que roda como servidor; os clientes conectam pela rede.
- **Migration**: arquivo numerado que muda o schema (cria tabela, adiciona coluna). Aplicadas em ordem, levam qualquer banco, vazio ou antigo, ao schema atual.

| | [[SQLite e FTS5\|SQLite]] | Postgres |
|---|---|---|
| roda como | biblioteca, um arquivo | serviço, conexões pela rede |
| escritas ao mesmo tempo | uma por vez | muitas |
| bom para | dado de um dispositivo | dado compartilhado num servidor |

- Migration porque um banco com dados não pode ser apagado e recriado a cada mudança de schema.
- Num [[Container e Docker Compose|container]], o dado fica num volume, para sobreviver ao container; a cópia fora da máquina é o [[Backup e restore|backup]].

> [!example] No NoteProject
> O servidor de sync guarda `users` e `notes` num Postgres ([[Back — daemon e servidor]]).

Doc: [PostgreSQL](https://www.postgresql.org/docs/current/tutorial-arch.html).
