---
tags: [noteproject, conceito, infra]
---
# Container e Docker Compose

Um serviço só roda numa máquina que tenha a versão certa da linguagem, das libs e do sistema. Instalar isso à mão em cada máquina quebra fácil e não se repete igual.

- **Imagem**: pacote com o programa e tudo de que ele precisa, feito a partir de um `Dockerfile`.
- **Container**: a imagem rodando, isolada das outras e da máquina.
- **Docker Compose**: um arquivo (`docker-compose.yml`) que descreve vários containers, portas, volumes e redes; `docker compose up` sobe todos.

| No compose | Para quê |
|---|---|
| `services` | um container por serviço (api, banco como o [[Postgres e migrations\|Postgres]], [[Reverse proxy\|proxy]]) |
| `volumes` | dado que sobrevive ao container (o banco) |
| `restart: unless-stopped` | volta sozinho depois de cair ou de a máquina reiniciar |
| `healthcheck` | o compose sabe se o serviço responde ([[Observabilidade]]) |

- Em desenvolvimento, o código costuma ser montado no container para recarregar a cada mudança; em produção, a imagem já vem pronta de um registry ([[CI e CD]]).

> [!example] No NoteProject
> Hoje o compose sobe o Vite; o servidor e o [[Postgres e migrations|Postgres]] entram em M0, e em produção, o mesmo jeito numa [[EC2]] ([[Infra — deploy e operação]]).

Doc: [Docker Compose](https://docs.docker.com/compose/).
