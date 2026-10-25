---
tags: [noteproject, plano, servidor, infra]
---
# M0 Server skeleton

Etapa do [[Roadmap]] que põe a [[API de notas]] de pé no PC: projeto Python, [[Container e Docker Compose|compose]], [[Postgres e migrations|Postgres]] e `.env`, sem custo. Cada issue abaixo diz o que entregou e o que ficou aprendido, com link para a página que explica.

| Issue | Estado |
|---|---|
| #4 Track the development workspace in git | ✅ fechada |
| #10 Scaffold the server with a health endpoint | ✅ fechada (PR #50) |
| #11 Run the server in Docker Compose | ✅ fechada (PR #52) |
| #12 Postgres com migrations · #13 `.env` | ⏳ branch `add-postgres-with-migrations-to-the-server` |
| #51 contexto do build do web | ⏳ aberta |

## #4 Track the development workspace in git ✅

Põe o workspace de IA (`CLAUDE.md`, `.claude/`, `ai/`) no git, separado do código do app. Passou por git: commit atômico, fixup, tags e arquivo gerado.

### Git

- Commit atômico: uma mudança por commit, e cada um passa no `make check` ([[Regras de git]]).
- Conserto de commit ainda não enviado vai por `fixup!` + rebase no original, não por commit novo.
- A tag no título (`[docs]`, `[ai-workspace]`) separa o que é do workspace do que é do app.
- Arquivo gerado (`ai/build/`) fica fora do git: o que se recria a partir do código não se versiona.

## #10 Scaffold the server with a health endpoint ✅

Cria `apps/notes`, a API com só `GET /health`, testada no `make check` e no [[CI e CD|CI]]. Passou por [[FastAPI]], Python e testes.

### FastAPI

- WSGI × ASGI: o uvicorn abre a porta e chama a app; o Starlette acha a rota; o [[FastAPI]] valida pela type hint (erro vira 422 sem a função rodar).
- Concorrência: no Django clássico, um pedido por worker; no FastAPI com `await`, centenas de esperas de I/O num processo só.
- `async def` roda no event loop; `def` vai para uma thread do pool. Chamada bloqueante dentro de `async def` trava o processo inteiro; na dúvida, `def`.
- `fastapi dev` escuta em `127.0.0.1` (só a própria máquina) e recarrega; `fastapi run` escuta em `0.0.0.0` e não recarrega.

### Python

- O `import` não aceita caminho: procura o primeiro nome no primeiro nível de cada pasta do `sys.path`, e a primeira que tiver vence ([[Python — módulo, package e venv|módulo, package e venv]]).
- venv = um Python com `site-packages` próprio; o `uv sync` instala nele o que o `uv.lock` fixa.
- Package é o formato; biblioteca é package feito para outros importarem; serviço é programa que roda e ninguém importa.
- Estrutura `src/` em vez de plana: o serviço é instalado no `.venv` (um `notes.pth` aponta para `src/`), e todo import começa por `notes.` ([[API de notas]]).

### Testes

- Quebrar o teste de propósito (esperar 201) e ver o `make check` falhar prova que o alvo está ligado.

## #11 Run the server in Docker Compose ✅

Roda a API num container: imagem de desenvolvimento e serviço `notes` no compose, em `127.0.0.1:8000`, recarregando ao salvar. Passou por [[Container e Docker Compose|Docker]] e [[IP, porta e rede de containers|rede]].

### Docker

- Imagem é o pacote; container é a imagem rodando; o compose descreve vários containers, portas e volumes ([[Container e Docker Compose]]).
- Camadas e cache: copiar `pyproject.toml` + `uv.lock` e rodar `uv sync --no-install-project` antes do `COPY . .`, para editar o código não reinstalar as libs ([[Dockerfile e camadas]]).
- A imagem recebe a lista de libs, não a pasta: a `.venv` do host foi feita para o host (binário glibc × musl), e o `.dockerignore` a tira do contexto.
- `EXPOSE` só documenta; quem publica a porta é o `ports:`.
- Volume monta por cima do que a imagem tem no caminho: o bind mount `./apps/notes:/app` cobre o `/app`, e o volume anônimo `/app/.venv` abre o buraco que devolve as libs da imagem.
- Lib nova pede `up --build -V`: o volume anônimo antigo, já cheio, cobriria a imagem nova.
- Recriar o container apaga o que não está em volume; `docker stop` manda `SIGTERM` e, passado o prazo, `SIGKILL`.
- Desenvolvimento e produção usam o mesmo Dockerfile com compose diferente; daí o nome `docker-compose-dev.yml`.

### Rede

- Uma máquina está em várias redes ao mesmo tempo (loopback, wi-fi, Docker); `0.0.0.0` = todos os IPs dela, e dentro do container `localhost` é o próprio container ([[IP, porta e rede de containers]]).
- `127.0.0.1:8000:8000` publica a porta só no loopback do host: outra máquina do wi-fi não chega.

## #12 Postgres com migrations · #13 `.env` ⏳

Põe o banco na [[API de notas]]: Postgres no compose, segredos no `.env`, migration criando a tabela `notes` e a API conectando pela `DATABASE_URL`. Passou por [[Postgres e migrations|Postgres]], Docker, rede e [[TCP e pacotes|TCP]], Linux, Python e as notas do vault.

### Postgres e banco

- O schema é o formato do banco, e a migration é um arquivo versionado que o muda: aplicadas em ordem, levam qualquer banco ao schema atual. A imagem `postgres` só cria usuário e banco com a pasta de dados vazia ([[Postgres e migrations]]).
- O Alembic encadeia as revisões como commits: `upgrade` aplica, `downgrade` reverte, e o `env.py` lê a `DATABASE_URL` ([[Migrations com Alembic]]).
- A engine do SQLAlchemy guarda um pool de conexões abertas e empresta uma por pedido; `engine.begin()` abre a transação ([[SQLAlchemy — engine e conexão]]).
- Pastas dentro de pastas numa tabela plana: cada linha aponta para o pai (`parent_id`, lista de adjacência), e a pasta é uma nota com `is_folder` ([[Árvore no banco]], [[Pastas, campos e views]]).
- Texto da nota fica numa coluna `TEXT` do banco, não num bucket: salvar é um `UPDATE` numa transação e a busca enxerga o conteúdo ([[S3 — armazenamento de objetos]]); a nota é [[Markdown]], texto puro que o editor só decora na tela ([[CodeMirror e decorações]]).

### Docker

- O Docker guarda imagens, containers e volumes numa pasta só por máquina; o volume nomeado `db` vira `noteproject_db` e sobrevive ao `down`, só sai com `down -v` ([[Container e Docker Compose]]).
- `exec` roda um programa no container que já está de pé (`psql`, `alembic upgrade head`); os comandos do dia a dia, com o alias do `-f`, ficam em [[Comandos do Docker no dev]].
- Segredo vai no `.env`, lido pelo compose com `env_file`; a API e o Alembic leem a `DATABASE_URL` dele ([[API de notas]]).

### Rede e TCP

- Dentro do compose o banco é `postgres:5432`, o nome do serviço; do host, `localhost:5432`, publicado só no loopback. O IP vem do DHCP ou é fixo, e cada caixa do desenho é uma rede ([[IP, porta e rede de containers]]).
- A rede só carrega pacotes; a tabela de rotas e o gateway levam cada um à outra rede, e o TCP numera e confirma até virar uma linha de bytes confiável ([[TCP e pacotes]]).

### Linux

- O Linux roda um arquivo pela permissão `x` e pelo formato (ELF ou `#!`), nunca pelo nome: é o que acontece com o `docker-entrypoint.sh` ([[Executar um arquivo no Linux]]).

### Python

- Estrutura `src/`: na plana, o `import` acha o código da pasta atual por acaso; o `uv_build` monta o caminho do package pelas chaves de `[tool.uv.build-backend]` ([[Python — módulo, package e venv]]).

### Notas do vault

- Plano: a [[Entrega de 2026-10-29]] pede notas no navegador e a IA no app antes do login, o que mexeu no [[Roadmap]], no [[00 Mapa — Plano do projeto|mapa do plano]] e nas ideias em [[Features]]. O login virou cookie de sessão (#48) no [[Navegador]] e em [[Back — daemon e servidor]], e o token ficou só para app ([[Token por dispositivo]]); a [[Trilha de infra]] ganhou links para os conceitos de cada etapa.
- Workspace: versão do serviço sobe na branch, num commit só dela ([[Regras de git]]); a skill `/lacunas` e o lint W12 entraram em [[Como usar]]; o [[Esqueleto de tarefas]] pesa o custo de tokens dos subagentes; [[Regras de página]] e [[Regras de resposta]] foram revistas (grafo de links, marcas `[fix]` e `[comment]`).
- Os mapas [[00 Mapa — Conceitos]] e [[00 Mapa — Estrutura do projeto]] ganharam as páginas novas.
