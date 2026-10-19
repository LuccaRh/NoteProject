# NoteProject

A notes app opened in the browser, served by its own server.

Current state: a CodeMirror 6 editor that styles Markdown headings. Notes are not saved yet;
the server (FastAPI + Postgres) is the next step.

```
apps/
  web/     CodeMirror 6 editor.
```

## Run

```bash
make install   # npm install
make dev       # Vite on :5173
```

Open <http://localhost:5173>.

Or with containers: `docker compose up --build` (ports bound to localhost only).

## Check

```bash
make check     # tsc + vite build
```

## Next steps

The server: FastAPI with Postgres in Docker Compose, the notes API, then login, TLS and the
deploy to AWS. Folders, fields and views come with the server's schema.
