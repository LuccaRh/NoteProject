---
tags: [noteproject, dados]
---
# Usuários do banco

Um programa conectado ao [[Postgres]] pode tudo o que o usuário dele pode. Se um único usuário cria tabelas e também atende os pedidos, uma falha no app (um SQL injection, por exemplo) alcança a estrutura do banco. Separar usuários por função limita esse estrago: é o menor privilégio, cada um com só o que precisa.

## Os três papéis

| Papel | Faz | Superusuário | Dono das tabelas |
|---|---|---|---|
| admin | cria usuários e bancos | sim | não |
| migrator | roda as [[Migration|migrations]] | não | sim |
| app | lê e escreve linhas | não | não |

- **Admin**: o superusuário ignora permissões e [[Row-Level Security]]. Fica só para montar o servidor.
- **Migrator**: muda a estrutura (`CREATE`, `ALTER`, `DROP TABLE`). Conecta só enquanto a migration roda.
- **App**: conecta o tempo todo, com `SELECT`, `INSERT`, `UPDATE` e `DELETE`. Não muda tabela nem desliga o [[Row-Level Security|RLS]].

## Dono da tabela

Quem cria uma tabela vira o dono dela, e só o dono (ou um superusuário) pode alterá-la ou apagá-la. Por isso o dono e quem roda migration são o mesmo usuário.

```sql
-- As the app user
DROP TABLE notes;                              -- error: must be owner
ALTER TABLE notes DISABLE ROW LEVEL SECURITY;  -- error: must be owner
```

O dono de uma tabela escapa do RLS, a menos que ela tenha `FORCE ROW LEVEL SECURITY`. Com `FORCE`, uma migration que altera dados antigos só veria as linhas liberadas pela *policy*; o atributo `BYPASSRLS` no migrator evita isso.

## Permissão das tabelas novas

A app só enxerga uma tabela depois de um `GRANT`. Em vez de repetir o `GRANT` em cada migration, o `ALTER DEFAULT PRIVILEGES` vale para toda tabela futura de um criador:

```sql
ALTER DEFAULT PRIVILEGES FOR ROLE notes_migrator IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO notes_app;
```

Tabela criada antes disso continua sem a permissão e precisa de um `GRANT` próprio.

> [!warning] Erros comuns
> - Deixar a senha do migrator no ambiente da app: quem invade a app lê a senha, e a separação perde o efeito.
> - Rodar migration como superusuário: as tabelas ficam com ele, e um erro na migration alcança o servidor inteiro.

Doc: [Privileges](https://www.postgresql.org/docs/current/ddl-priv.html), [Row Security Policies](https://www.postgresql.org/docs/current/ddl-rowsecurity.html), [ALTER DEFAULT PRIVILEGES](https://www.postgresql.org/docs/current/sql-alterdefaultprivileges.html).
