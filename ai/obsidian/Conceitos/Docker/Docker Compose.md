---
tags: [noteproject, conceito, infra]
---
# Docker Compose

Um sistema tem vários [[Container|containers]] (API, banco, proxy) que precisam subir juntos, com portas, volumes e uma rede em comum. Dar `docker run` com tudo isso à mão para cada um não se repete igual.

- **Docker Compose**: um arquivo (`docker-compose.yml`) que descreve vários containers, portas, volumes e redes; `docker compose up` sobe todos.

| No compose | Para quê |
|---|---|
| `services` | um container por serviço (api, banco como o [[Postgres]], [[Reverse proxy\|proxy]]) |
| `volumes` | dado que sobrevive ao container (o banco): [[Volume do Docker\|volume]] |
| `ports` | publica uma porta do container na máquina ([[Rede de containers]]) |
| `restart: unless-stopped` | volta sozinho depois de cair ou de a máquina reiniciar |
| `healthcheck` | o compose sabe se o serviço responde ([[Observabilidade]]) |

- O compose cria uma rede e põe todos os serviços nela; lá dentro, o nome do serviço é o endereço ([[Rede de containers]]).
- O compose põe o nome do projeto (por padrão, o da pasta) na frente do que cria: o volume `db` vira `noteproject_db`, e outro projeto com um `db` ganha um volume próprio. `docker volume inspect <nome>` mostra onde ele fica no disco (`Mountpoint`). *(geral)*

## Rodar um comando no container: exec

`docker compose exec <serviço> <programa>` roda um programa dentro de um container que já está de pé e liga o terminal a ele; o container não é recriado. *(geral)*

| Exemplo | Faz |
|---|---|
| `docker compose exec postgres bash` | abre um shell no container; `exit` volta |
| `docker compose exec postgres psql -U <usuário> -d <banco>` | abre direto o [[Postgres#Ver o banco: psql\|psql]] |
| `docker compose exec notes uv run alembic upgrade head` | roda as [[Migration\|migrations]] onde o nome do banco resolve |

- O serviço é o nome no arquivo do compose; com `-f`, o mesmo `-f` do `up`.
- Container parado: o `exec` falha. O `docker compose run <serviço> <programa>` cria um container novo só para o comando.
- O programa roda com as variáveis do container (as do `.env`) e na rede do compose, onde os outros serviços são achados pelo nome.

## Variáveis do .env

- `env_file: .env` num serviço: quem lê o arquivo é o `docker compose`, no host. Ao criar o container, cada linha `NOME=valor` vira uma variável de ambiente dele, o mesmo que `docker run -e NOME=valor`. O arquivo não entra no container. *(geral)*
- O mesmo `.env` em dois serviços entrega o mesmo valor aos dois: a senha que cria o usuário no [[Postgres]] é a que a API usa para conectar.
- O container guarda os valores de quando foi criado; mudar o `.env` só vale ao recriá-lo (`up` de novo). *(geral)*
- O `.env` fica fora do git (`.gitignore`), porque tem segredo.

## Desenvolvimento e produção

- A mesma imagem (o mesmo [[Dockerfile]]) serve aos dois; muda o compose.
- Desenvolvimento: monta o código por bind mount ([[Volume do Docker|volume]]) e troca o comando por um que recarrega. Produção: arquivo à parte (`docker-compose.prod.yml`), sem código montado, com a imagem vinda do registry ([[CD]]) e `restart`.
- O código entra pelos dois caminhos: `COPY . .` na imagem e bind mount no dev. No dev, o volume cobre a cópia, que fica redundante ali; a cópia é o que faz a imagem rodar **sozinha** (CI, outra máquina, produção) e o que o instalador precisa para instalar o próprio projeto no build.

| | Dev | Produção |
|---|---|---|
| Imagem | `build:` | `image:` pronta, do registry |
| Comando | um que recarrega (`fastapi dev`) | sem recarga (`fastapi run`) |
| Volume do código | bind mount + buraco da pasta das libs | nenhum: vale o código do `COPY` |
| Volume de dados | — | volume nomeado do banco |
| `ports:` da API | `127.0.0.1:8000:8000`, para testar do host | nenhum: só o [[Reverse proxy\|proxy]] publica (443, e 80 para redirecionar) e chama `api:8000` pela rede do compose |
| `restart:` | — | `unless-stopped` |

- Sem `ports:` na API, o único caminho de fora até ela passa pelo proxy, onde fica o [[TLS]] ([[Rede de containers]]).
- O Compose também junta arquivos: `docker compose -f docker-compose.yml -f docker-compose.prod.yml up` aplica o segundo por cima do primeiro ([Merge Compose files](https://docs.docker.com/compose/how-tos/multiple-compose-files/merge/)).

> [!example] No NoteProject
> Hoje o compose sobe o Vite; o servidor e o [[Postgres]] entram em M0, e em produção, o mesmo jeito numa [[EC2]] ([[Infra — deploy e operação]]).

Doc: [Docker Compose](https://docs.docker.com/compose/).
