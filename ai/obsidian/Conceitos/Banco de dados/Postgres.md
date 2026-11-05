---
tags: [noteproject, conceito, servidor]
---
# Postgres

No dispositivo, um arquivo [[SQLite]] basta: só um programa escreve. Num servidor, vários clientes escrevem ao mesmo tempo, e o banco tem de rodar como serviço e ser copiado com segurança.

- **Postgres**: banco relacional que roda como servidor; os clientes conectam pela rede.
- **Schema**: o formato do banco (tabelas, colunas, tipos, regras); os dados são as linhas guardadas nele. Mudar o schema de um banco com dados é o papel da [[Migration|migration]].

| | [[SQLite]] | Postgres |
|---|---|---|
| roda como | biblioteca, um arquivo | serviço, conexões pela rede |
| escritas ao mesmo tempo | uma por vez | muitas |
| bom para | dado de um dispositivo | dado compartilhado num servidor |

- Num [[Container|container]], o dado fica num [[Volume do Docker|volume]], para sobreviver ao container; a cópia fora da máquina é o [[Backup|backup]].
- O protocolo é próprio, na porta 5432, por cima do [[TCP]]; não é HTTP.

## Postgres num container

A imagem oficial `postgres` traz um script de entrada (`docker-entrypoint.sh`) que roda a cada subida do [[Container|container]]. Com a pasta de dados vazia, ele roda o `initdb` e cria o superusuário e o banco a partir de variáveis de ambiente; com a pasta já preenchida, só liga o Postgres.

| Variável | Para quê | Sem ela |
|---|---|---|
| `POSTGRES_PASSWORD` | senha do superusuário | o container não sobe (é a única obrigatória) |
| `POSTGRES_USER` | nome do superusuário, criado com um banco de mesmo nome | `postgres` |
| `POSTGRES_DB` | nome do banco criado na primeira subida | o de `POSTGRES_USER` |

- Os outros [[Usuários do banco|usuários]] e bancos saem de scripts em `/docker-entrypoint-initdb.d`, que rodam só nessa primeira subida.
- As variáveis só valem com a pasta vazia: trocar a senha depois não muda o banco. Saída: `ALTER USER` no `psql`, ou apagar o volume e perder os dados.
- Do 18 em diante, os dados ficam em `/var/lib/postgresql/18/docker` e o volume da imagem é `/var/lib/postgresql`; até o 17, `/var/lib/postgresql/data`. O volume montado no caminho antigo deixa os dados fora dele.

## Ver o banco: psql

O `psql` é o terminal do Postgres: manda SQL ao banco e mostra a resposta. Vem dentro da imagem `postgres`, então roda dentro do container, sem instalar nada no host: `docker compose exec postgres psql -U <usuário> -d <banco>` ([[Docker Compose#Rodar um comando no container: exec|exec]]).

| Comando | Mostra / faz |
|---|---|
| `\dt` | as tabelas do banco |
| `\d <tabela>` | as colunas da tabela e os tipos (o schema dela) |
| `SELECT * FROM <tabela>;` | as linhas (os dados) |
| `\r` | descarta o comando que ficou pela metade |
| `\q` | sai |

- Comando com `\` é do psql e não leva `;`. SQL só vai ao banco quando acha o `;`: até lá, cada Enter acrescenta uma linha ao mesmo comando, e o prompt muda de `banco=#` para `banco-#`.
- No `\dt`, as tabelas aparecem no schema `public`: no Postgres, "schema" também é o nome de uma pasta de tabelas dentro do banco, outro sentido da palavra.

Doc da imagem: [postgres no Docker Hub](https://hub.docker.com/_/postgres) (lida em 2026-10-22, versão atual 18.6).

> [!example] No NoteProject
> O servidor de sync guarda `users` e `notes` num Postgres ([[Back — daemon e servidor]]).

Doc: [PostgreSQL](https://www.postgresql.org/docs/current/tutorial-arch.html).
