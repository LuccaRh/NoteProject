# NoteProject

A notes app opened in the browser, served by its own server.

Current state: a CodeMirror 6 editor that styles Markdown headings, and the start of the notes
API (only a health check). Notes are not saved yet.

```
apps/
  web/     CodeMirror 6 editor.
  notes/   Notes API (FastAPI). See apps/notes/README.md.
```

## Run

Each service runs in its own terminal. The notes API needs [uv](https://docs.astral.sh/uv/).

| Service | Start | Open in the browser |
|---|---|---|
| web (editor) | `make install` once, then `make dev` | <http://localhost:5173> |
| notes (API) | `cd apps/notes && uv run fastapi dev src/notes/main.py` | <http://localhost:8000/docs> |

The ports come from each tool: 5173 is set in `apps/web/vite.config.ts`, and 8000 is the
default of `fastapi dev`. Both listen on localhost only and reload when a file is saved.

To run everything, start both commands, one per terminal, or run both in containers with
`docker compose -f docker-compose-dev.yml up --build` (same ports, same reload).

### Environment variables

Passwords and connection settings live in a `.env` file at the repo root. Git ignores it, so
each clone creates its own:

```sh
cp .env.example .env    # then replace every value
```

`.env.example` lists the variables the project uses, each with a comment and a placeholder
value. Docker Compose loads `.env` into the `postgres` and `notes` containers (`env_file` in
`docker-compose-dev.yml`):

| Variable | Read by | Meaning |
|---|---|---|
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | `postgres` image | user, password and database created on the first start |
| `DATABASE_URL` | notes API and Alembic | `postgresql+psycopg://<user>:<password>@postgres:5432/<db>`, with the three values above |

The host in `DATABASE_URL` is `postgres`, the service name in the compose file, which only
resolves inside the containers. The `postgres` image reads its three variables only when the `db` volume is
empty; after changing them, recreate the volume with
`docker compose -f docker-compose-dev.yml down -v` (this deletes the data).

### Database migrations

Alembic creates and changes the tables (`apps/notes/migrations/versions/`). On a fresh
database, and after pulling a new migration, apply them inside the `notes` container:

```sh
docker compose -f docker-compose-dev.yml exec notes uv run alembic upgrade head
```

### Trying an API in the browser

Every FastAPI service serves its own interactive docs at `/docs` (Swagger UI), built from the
code:

1. Open `http://localhost:<port>/docs`; it lists every route.
2. Click a route, then **Try it out** and **Execute**.
3. The page shows the request it sent (as a `curl` command), the status code and the body.

A `GET` route can also be opened straight in the address bar, e.g.
<http://localhost:8000/health> shows `{"status":"ok"}`.

## Check

```bash
make check     # web: tsc + vite build; notes: ruff, mypy, pytest
```

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
`/commit`, `/escrita`. Agent: `leitor`. Tools in `ai/tools/`: `np.py`, `obsidian_sync.py`,
`hooks_contexto.py`, `foco.py`, `diagrama.py`, `commit_msg.py`, `estilo.py`.
