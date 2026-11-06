# NoteProject

A notes app opened in the browser, served by its own server.

Current state: a CodeMirror 6 editor that styles Markdown headings, and the start of the notes
API (only a health check). Notes are not saved yet.

```
apps/
  chimchar/  CodeMirror 6 editor.
  ichiro/    Notes API (FastAPI). See apps/ichiro/README.md.
  lonzo/     Chat service (FastAPI): sends a question to the Anthropic API and
             streams the answer back as server-sent events.
```

## Run

Docker Compose starts everything: Caddy, the editor, the notes API, the chat service and
Postgres. It needs
the `.env` below. `make check` also needs [uv](https://docs.astral.sh/uv/).

| What | Start | Open in the browser |
|---|---|---|
| everything | `docker compose -f docker-compose-dev.yml up --build` | <https://notes.localhost> |
| editor only, no API | `make install` once, then `make dev` | <http://localhost:5173> |

Caddy (`caddy/Caddyfile`) is the only way in. Each API prefix goes to its own service,
without the `/api` prefix: `/api/notes` to the notes API, `/api/chat` to the chat service;
any other `/api` path is a 404, and everything else goes to the Vite dev server. Both reload when a file is
saved. The editor and the API publish no port of their own; Postgres listens on
`localhost:5432` for the tests. `*.localhost` names resolve to the machine itself.

### Trusting the local certificate

Caddy signs the certificate for `notes.localhost` with its own local CA, kept in the
`caddy_data` volume. Until the system trusts that CA, the browser shows a warning. Copy the
root certificate out of the container and add it once (Arch Linux):

```sh
docker compose -f docker-compose-dev.yml cp \
    caddy:/data/caddy/pki/authorities/local/root.crt caddy-root.crt
sudo trust anchor caddy-root.crt
```

Firefox keeps its own list: import the same file under Settings, Certificates. Deleting the
`caddy_data` volume creates a new CA, which has to be trusted again.

### Environment variables

Passwords and connection settings live in a `.env` file at the repo root. Git ignores it, so
each clone creates its own:

```sh
cp .env.example .env    # then replace every value
```

`.env.example` lists the variables the project uses, each with a comment and a placeholder
value. Docker Compose loads `.env` into the `postgres` container (`env_file` in
`docker-compose-dev.yml`); each service gets only its own variables (`environment`):

| Variable | Read by | Meaning |
|---|---|---|
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | `postgres` image | superuser, its password and the database it connects to |
| `ICHIRO_DB_PASSWORD`, `ICHIRO_MIGRATOR_PASSWORD` | `postgres/init` | passwords of the `ichiro` and `ichiro_migrator` users |
| `ICHIRO_DATABASE_URL` | notes API | `postgresql+psycopg://ichiro:<password>@postgres:5432/ichiro` |
| `ICHIRO_MIGRATION_URL` | notes Alembic | the same database, as `ichiro_migrator`, which owns the tables |
| `LONZO_*`, `NUJABES_*` | `lonzo`, `nujabes`, `postgres/init` | the same four variables for each service |
| `LONZO_SECRET_KEY` | chat service | encrypts the Anthropic key each user saves in the settings; make it with `Fernet.generate_key()` from `cryptography` |

The host in these URLs is `postgres`, the service name in the compose file, which only
resolves inside the containers. `make check` runs the tests on the host, so it swaps the host
for `localhost`. The `postgres` image reads its three variables only when the `db` volume is
empty; after changing them, recreate the volume with
`docker compose -f docker-compose-dev.yml down -v` (this deletes the data).

### Database migrations

Alembic creates and changes the tables (`apps/ichiro/migrations/versions/`). On a fresh
database, and after pulling a new migration, apply them inside the `ichiro` container:

```sh
docker compose -f docker-compose-dev.yml exec ichiro uv run alembic upgrade head
```

### Trying an API in the browser

Every FastAPI service serves its own interactive docs at `/docs` (Swagger UI), built from the
code:

1. Open the service's `/docs` (for now only with a published port: through Caddy the page
   asks for `/openapi.json` without the `/api` prefix); it lists every route.
2. Click a route, then **Try it out** and **Execute**.
3. The page shows the request it sent (as a `curl` command), the status code and the body.

A `GET` route can also be opened straight in the address bar, e.g.
<https://notes.localhost/api/notes> lists the notes.

## Check

```bash
make check     # chimchar: tsc + vite build; ichiro, lonzo: ruff, mypy, pytest
```

The ichiro tests talk to the real database: start Postgres first
(`docker compose -f docker-compose-dev.yml up -d postgres`).

## Next steps

The server: FastAPI with Postgres in Docker Compose, the notes API, then login, TLS and the
deploy to AWS. Folders, fields and views come with the server's schema.

## Development workspace

The repo has a workspace for coding sessions (modeled on `~/Documents/Disciplinas`). Open
the session at the root; `CLAUDE.md` explains the principles. First time in a clone:
`ai/tools/instalar.sh`.

- `ai/kb/areas.yaml`: closed vocabulary of areas; `ai/np contexto <area>` lists only what to read.
- `ai/kb/escopos/<branch>.md`: request / context / out of scope for each branch (`foco.py` hook).
- `ai/kb/libs/`: API cards for the libraries, with the installed version (lint warns when it changes).
- `ai/kb/diagramas/`: diagram sources in YAML (`diagrama.py` → `.drawio` + `.drawio.svg`).
- `ai/obsidian/`: copy of the `Note Project/` vault, kept in sync by `obsidian_sync.py`.

| Command | For |
|---|---|
| `ai/np status` / `contexto <area>` / `areas` | branch state / what to read / the vocabulary |
| `ai/np obsidian` / `duvidas` / `diagrama <spec>` | vault sync / note markers / diagrams |
| `ai/np lint` / `test` / `check` | workspace rules / `ai/tools/` tests / `make check` |

Skills: `/tarefa`, `/aprender`, `/nota`, `/diagrama`, `/duvida`, `/destrinchar`, `/foco`,
`/commit`, `/escrita`, `/lacunas`. Agent: `leitor`. Tools in `ai/tools/`: `np.py`, `obsidian_sync.py`,
`hooks_contexto.py`, `foco.py`, `diagrama.py`, `commit_msg.py`, `estilo.py`.
