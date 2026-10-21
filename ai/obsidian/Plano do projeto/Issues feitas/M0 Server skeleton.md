---
tags: [noteproject, plano, servidor, infra]
---
# M0 Server skeleton

Etapa do [[Roadmap]] que põe a [[API de notas]] de pé no PC: projeto Python, [[Container e Docker Compose|compose]], [[Postgres e migrations|Postgres]] e `.env`, sem custo. Cada issue abaixo diz o que entregou e o que ficou aprendido, com link para a página que explica.

| Issue | Estado |
|---|---|
| #4 Track the development workspace in git | ✅ fechada |
| #10 Scaffold the server with a health endpoint | ✅ fechada (PR #50) |
| #11 Run the server in Docker Compose | ⏳ branch `add-note-service-to-docker-compose` |
| #12 Postgres com migrations · #13 `.env` · #51 contexto do build do web | ⏳ abertas |

## #4 Track the development workspace in git ✅

Põe `CLAUDE.md`, `.claude/` e `ai/` no git, em commits próprios, separados do código do app.

- Commit atômico: uma mudança por commit, e cada um passa no `make check` ([[Regras de git]]).
- Conserto de commit ainda não enviado vai por `fixup!` + rebase no original, não por commit novo ([[Git rebase]]).
- A tag no título (`[docs]`, `[ai-workspace]`) separa o que é do workspace do que é do app.
- Arquivo gerado (`ai/build/`) fica fora do git: o que se recria a partir do código não se versiona.

## #10 Scaffold the server with a health endpoint ✅

Cria `apps/notes`: projeto uv (Python 3.14) com [[FastAPI]], `GET /health` devolvendo 200 `{"status":"ok"}`, teste com `TestClient`, alvo `make check-notes` (ruff, mypy, pytest) no `make check` e job `notes` no [[CI e CD|CI]].

- WSGI × ASGI: o uvicorn abre a porta e chama a app; o Starlette acha a rota; o [[FastAPI]] valida pela type hint (erro vira 422 sem a função rodar).
- Concorrência: no Django clássico, um pedido por worker; no FastAPI com `await`, centenas de esperas de I/O num processo só.
- `async def` roda no event loop; `def` vai para uma thread do pool. Chamada bloqueante dentro de `async def` trava o processo inteiro; na dúvida, `def`.
- O `import` não aceita caminho: procura o primeiro nome no primeiro nível de cada pasta do `sys.path`, e a primeira que tiver vence ([[Python — módulo, package e venv|módulo, package e venv]]).
- venv = um Python com `site-packages` próprio; o `uv sync` instala nele o que o `uv.lock` fixa.
- Package é o formato; biblioteca é package feito para outros importarem; serviço é programa que roda e ninguém importa.
- Estrutura `src/` em vez de plana: o serviço é instalado no `.venv` (um `notes.pth` aponta para `src/`), e todo import começa por `notes.` ([[API de notas]]).
- `fastapi dev` escuta em `127.0.0.1` (só a própria máquina) e recarrega; `fastapi run` escuta em `0.0.0.0` e não recarrega.
- Quebrar o teste de propósito (esperar 201) e ver o `make check` falhar prova que o alvo está ligado.

## #11 Run the server in Docker Compose ⏳

Imagem de desenvolvimento da API (`apps/notes/Dockerfile.dev`, Python 3.14 + uv) e serviço `notes` no `docker-compose-dev.yml`, publicado em `127.0.0.1:8000` e recarregando ao salvar.

- Imagem é o pacote; container é a imagem rodando; o compose descreve vários containers, portas e volumes ([[Container e Docker Compose]]).
- Camadas e cache: copiar `pyproject.toml` + `uv.lock` e rodar `uv sync --no-install-project` antes do `COPY . .`, para editar o código não reinstalar as libs ([[Dockerfile e camadas]]).
- A imagem recebe a lista de libs, não a pasta: a `.venv` do host foi feita para o host (binário glibc × musl), e o `.dockerignore` a tira do contexto.
- `EXPOSE` só documenta; quem publica a porta é o `ports:`.
- Volume monta por cima do que a imagem tem no caminho: o bind mount `./apps/notes:/app` cobre o `/app`, e o volume anônimo `/app/.venv` abre o buraco que devolve as libs da imagem.
- Lib nova pede `up --build -V`: o volume anônimo antigo, já cheio, cobriria a imagem nova.
- Recriar o container apaga o que não está em volume; `docker stop` manda `SIGTERM` e, passado o prazo, `SIGKILL`.
- Uma máquina está em várias redes ao mesmo tempo (loopback, wi-fi, Docker); `0.0.0.0` = todos os IPs dela, e dentro do container `localhost` é o próprio container ([[IP, porta e rede de containers]]).
- `127.0.0.1:8000:8000` publica a porta só no loopback do host: outra máquina do wi-fi não chega.
- Desenvolvimento e produção usam o mesmo Dockerfile com compose diferente; daí o nome `docker-compose-dev.yml`.
