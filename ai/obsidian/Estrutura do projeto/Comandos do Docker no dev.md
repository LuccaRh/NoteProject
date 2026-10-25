---
tags: [noteproject, infra]
---
# Comandos do Docker no dev

O dev do NoteProject roda no [[Container e Docker Compose|Docker Compose]], com três serviços no `docker-compose-dev.yml`: `web` (Vite), `notes` ([[API de notas]]) e `postgres` ([[Postgres e migrations]]). Todo comando passa pelo mesmo `-f`, então há um alias no `~/.bashrc`:

```bash
alias dc='docker compose -f docker-compose-dev.yml'
```

Os comandos abaixo rodam da raiz do repo, onde o arquivo está.

## Subir, parar, apagar

| Comando | Faz |
|---|---|
| `dc up -d` | sobe tudo em segundo plano (cria o que falta, recria o que mudou no compose ou no `.env`) |
| `dc up -d --build notes` | refaz a imagem do `notes` e recria o container; depois de `uv add` ou de mudar o `Dockerfile.dev` |
| `dc up -d --force-recreate notes` | recria o container sem refazer a imagem; para ler o `.env` de novo |
| `dc restart notes` | reinicia o processo no mesmo container; **não** lê o `.env` de novo |
| `dc stop` | para os containers, sem apagar |
| `dc down` | para e apaga containers e rede; o volume do banco fica |
| `dc down -v` | idem e **apaga os volumes**: o banco volta vazio |

## Ver o que está rodando

| Comando                      | Faz                                                           |
| ---------------------------- | ------------------------------------------------------------- |
| `dc ps`                      | serviços, estado e portas                                     |
| `dc logs -f notes`           | log do `notes`, seguindo (`Ctrl+C` sai, o container continua) |
| `dc logs --tail=50 postgres` | as últimas 50 linhas do banco                                 |
| `docker volume ls`           | os volumes; o do banco é `noteproject_db`                     |

## Postgres

| Comando                                                                        | Faz                                                                          |
| ------------------------------------------------------------------------------ | ---------------------------------------------------------------------------- |
| `dc exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'`          | abre o psql com usuário e banco do `.env` (as variáveis são as do container) |
| `dc exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "\dt"'` | roda um comando só e sai                                                     |
| `dc exec postgres bash`                                                        | shell dentro do container                                                    |

Dentro do psql: `\dt` (tabelas), `\d notes` (colunas), `SELECT * FROM notes;`, `\q` (sai). Detalhes em [[Postgres e migrations]], "Ver o banco: psql".

## Migrations no `notes`

O [[Migrations com Alembic|Alembic]] conecta pelo nome `postgres`, que só resolve na rede do compose ([[IP, porta e rede de containers]]): o que toca no banco roda dentro do container `notes`.

| Comando | Faz | Toca no banco? |
|---|---|---|
| `dc exec notes uv run alembic upgrade head` | aplica as migrations que faltam | sim |
| `dc exec notes uv run alembic downgrade -1` | reverte a última | sim |
| `dc exec notes uv run alembic current` | qual migration o banco está | sim |
| `dc exec notes uv run alembic history` | a lista das migrations | não |
| `dc exec notes uv run alembic revision -m "<mensagem>"` | cria o arquivo da migration nova | não |

- O `revision` não roda o `env.py` (`revision_environment` desligado no `alembic.ini`), então também funciona no host, de `apps/notes`: `uv run alembic revision -m "..."`. Criado no container, o arquivo aparece no host igual, pelo bind mount de `apps/notes`.
- Container novo sem a `DATABASE_URL` → `KeyError: 'DATABASE_URL'`: o container é de antes da variável; `dc up -d --force-recreate notes`.

> [!warning] Erros comuns
> - `exec notes ...` sem o `dc` na frente: o `bash` usa o `exec` dele e responde `exec: notes: not found`.
> - `dc exec` com o container parado: falha; antes, `dc up -d`.
> - `dc down -v` para "limpar": apaga o banco junto.
