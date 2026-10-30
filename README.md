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

Docker Compose starts everything: Caddy, the editor, the notes API and Postgres. It needs
the `.env` below. `make check` also needs [uv](https://docs.astral.sh/uv/).

| What | Start | Open in the browser |
|---|---|---|
| everything | `docker compose -f docker-compose-dev.yml up --build` | <https://notes.localhost> |
| editor only, no API | `make install` once, then `make dev` | <http://localhost:5173> |

Caddy (`caddy/Caddyfile`) is the only way in: `/api/*` goes to the notes API without the
`/api` prefix, and everything else goes to the Vite dev server. Both reload when a file is
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
value. Docker Compose loads `.env` into the `postgres` and `notes` containers (`env_file` in
`docker-compose-dev.yml`):

| Variable | Read by | Meaning |
|---|---|---|
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | `postgres` image | user, password and database created on the first start |
| `DATABASE_URL` | notes API and Alembic | `postgresql+psycopg://<user>:<password>@postgres:5432/<db>`, with the three values above |

The host in `DATABASE_URL` is `postgres`, the service name in the compose file, which only
resolves inside the containers. `make check` runs the tests on the host, so it swaps the host
for `localhost`. The `postgres` image reads its three variables only when the `db` volume is
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

1. Open the service's `/docs` (for now only with a published port: through Caddy the page
   asks for `/openapi.json` without the `/api` prefix); it lists every route.
2. Click a route, then **Try it out** and **Execute**.
3. The page shows the request it sent (as a `curl` command), the status code and the body.

A `GET` route can also be opened straight in the address bar, e.g.
<https://notes.localhost/api/health> shows `{"status":"ok"}`.

## Check

```bash
make check     # web: tsc + vite build; notes: ruff, mypy, pytest
```

The notes tests talk to the real database: start Postgres first
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
