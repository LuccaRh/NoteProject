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
