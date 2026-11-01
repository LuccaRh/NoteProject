---
tags: [noteproject, prova, infra]
---
# Questões de Docker

Como o `ichiro`, o `chimchar`, o [[Postgres]] e o [[Reverse proxy|Caddy]] rodam no `docker-compose-dev.yml` ([[Issue 11 — Run the server in Docker Compose|#11]], [[Comandos do Docker no dev]]).

## 1. Qual a diferença entre imagem e container?

> [!note]- Resposta
> Imagem é o pacote (o programa e o que ele precisa); container é a imagem rodando. O [[Docker Compose|compose]] descreve vários containers, portas e volumes ([[Container]]).

## 2. O Dockerfile do `ichiro` copia `pyproject.toml` e `uv.lock`, roda `uv sync --no-install-project` e só depois faz `COPY . .`. Por quê?

> [!note]- Resposta
> Cache de camadas: a camada das libs só refaz quando a lista muda. Editar o código muda só o `COPY . .`, e as libs não são reinstaladas ([[Dockerfile]]).

## 3. Por que o `.dockerignore` tira a `.venv` do host?

> [!note]- Resposta
> A `.venv` foi montada para o host (binários para o sistema dele, glibc × musl). A imagem recebe a lista de libs e monta a própria ([[Issue 11 — Run the server in Docker Compose|#11]]).

## 4. O compose monta `./apps/ichiro:/app` e também `/app/.venv` sem nome. O que cada um faz?

> [!note]- Resposta
> O bind mount cobre o `/app` da imagem com o código do host, para recarregar ao salvar. Isso também esconderia a `.venv` da imagem; o volume anônimo em `/app/.venv` abre o buraco que a devolve ([[Volume do Docker]]).

## 5. Uma lib nova entra no `pyproject.toml`. Por que `up --build` não basta e é preciso `up --build -V`?

> [!note]- Resposta
> O volume anônimo antigo, já cheio com as libs velhas, cobriria a `.venv` da imagem nova. O `-V` recria os volumes anônimos ([[Volume do Docker]], [[Comandos do Docker no dev]]).

## 6. Depois de `docker compose down`, as notas do Postgres continuam? E depois de `down -v`?

> [!note]- Resposta
> Com `down`, sim: o volume nomeado `db` (`noteproject_db`) sobrevive. Com `down -v`, o volume é apagado junto ([[Volume do Docker]], [[Docker Compose]]).

## 7. Verdadeiro ou falso: `EXPOSE 8000` no Dockerfile deixa o host acessar a porta 8000.

> [!note]- Resposta
> Falso. `EXPOSE` só documenta; quem publica é o `ports:` do compose. O `ichiro` hoje nem tem `ports:` ([[Dockerfile]], [[Rede de containers]]).

## 8. O que o `docker stop` manda ao processo, e o que acontece se ele não sair?

> [!note]- Resposta
> `SIGTERM`, que o processo pode tratar para fechar com calma; passado o prazo, `SIGKILL`, que não dá para tratar ([[Sinal do Linux]]).

## 9. Escreva o comando que aplica as migrations no banco do compose.

> [!note]- Resposta
> `dc exec ichiro uv run alembic upgrade head` (com o alias `dc` do `-f docker-compose-dev.yml`). Roda dentro do container porque, fora da rede do compose, o host `postgres` não resolve ([[Comandos do Docker no dev]], [[API de notas]]).

## 10. O `docker-entrypoint.sh` da imagem do Postgres roda sem `.sh` ter significado nenhum para o Linux. O que decide se um arquivo executa?

> [!note]- Resposta
> A permissão `x` e o formato: binário ELF ou texto começando por `#!`. O nome não importa ([[Executar um arquivo no Linux]]).

## 11. Por que o `chimchar` e o `ichiro` deixaram de publicar porta depois da #16?

> [!note]- Resposta
> Todo pedido entra pelo [[Reverse proxy|Caddy]] (443), que chega nos dois pela rede do compose. Porta publicada a mais é porta exposta a mais ([[Rede de containers]], [[Rede do servidor]]).
