.PHONY: dev check check-chimchar check-tools install check-notes

# Local secrets (DATABASE_URL); in CI they come from the job env
-include .env

install:
	cd apps/chimchar && npm install

dev:
	cd apps/chimchar && npm run dev

check: check-chimchar check-notes

check-chimchar:
	cd apps/chimchar && npx tsc --noEmit && npm run build

# Tests run on the host: reach the compose Postgres through localhost
TEST_DATABASE_URL = $(subst @postgres:,@localhost:,$(DATABASE_URL))

check-notes:
	cd apps/notes && uv run ruff check && uv run mypy src tests \
		&& DATABASE_URL='$(TEST_DATABASE_URL)' uv run pytest

# Development workspace tools (ai/tools, ai/kb): tests + lint.
check-tools:
	python3 ai/tools/np.py test && python3 ai/tools/np.py lint
