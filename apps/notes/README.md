# notes

The notes API for the browser (FastAPI). For now it only has `GET /health`; the notes routes and
Postgres come next.

## Run

From `apps/notes`:

```bash
uv sync                                  # create .venv and install dependencies
uv run fastapi dev src/notes/main.py     # http://127.0.0.1:8000, reloads on save
```

- <http://localhost:8000/health> returns `{"status":"ok"}`.
- <http://localhost:8000/docs> lists the routes.

`fastapi dev` only listens on 127.0.0.1, so other machines can't reach it.

## Check

```bash
uv run ruff check && uv run mypy src && uv run pytest
```

`make check-notes` at the repo root runs the same thing, and `make check` includes it.

## Layout

```
src/notes/    the package; uv installs it into .venv, so imports start with `notes.`
tests/        pytest, with FastAPI's TestClient (no server needed)
```
