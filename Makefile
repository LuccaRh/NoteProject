.PHONY: dev check check-chimchar check-tools install check-ichiro check-lonzo \
	check-nujabes

# Local secrets (database URLs); in CI they come from the job env
-include .env
export LONZO_SECRET_KEY

install:
	cd apps/chimchar && npm install

dev:
	cd apps/chimchar && npm run dev

check: check-chimchar check-ichiro check-lonzo check-nujabes

check-chimchar:
	cd apps/chimchar && npx tsc --noEmit && npm run build

# Tests run on the host: reach the compose Postgres through localhost
TEST_ICHIRO_MIGRATION_URL = \
	$(subst @postgres:,@localhost:,$(ICHIRO_MIGRATION_URL))
TEST_ICHIRO_DATABASE_URL = \
	$(subst @postgres:,@localhost:,$(ICHIRO_DATABASE_URL))
TEST_LONZO_DATABASE_URL = \
	$(subst @postgres:,@localhost:,$(LONZO_DATABASE_URL))
TEST_LONZO_MIGRATION_URL = \
	$(subst @postgres:,@localhost:,$(LONZO_MIGRATION_URL))
TEST_NUJABES_DATABASE_URL = \
	$(subst @postgres:,@localhost:,$(NUJABES_DATABASE_URL))
TEST_NUJABES_MIGRATION_URL = \
	$(subst @postgres:,@localhost:,$(NUJABES_MIGRATION_URL))

check-ichiro:
	cd apps/ichiro && uv run ruff check && uv run mypy src tests \
		&& ICHIRO_MIGRATION_URL='$(TEST_ICHIRO_MIGRATION_URL)' \
		ICHIRO_DATABASE_URL='$(TEST_ICHIRO_DATABASE_URL)' uv run pytest

check-lonzo:
	cd apps/lonzo && uv run ruff check && uv run mypy src tests \
		&& LONZO_MIGRATION_URL='$(TEST_LONZO_MIGRATION_URL)' \
		LONZO_DATABASE_URL='$(TEST_LONZO_DATABASE_URL)' uv run pytest

check-nujabes:
	cd apps/nujabes && uv run ruff check && uv run mypy src tests \
		&& NUJABES_MIGRATION_URL='$(TEST_NUJABES_MIGRATION_URL)' \
		NUJABES_DATABASE_URL='$(TEST_NUJABES_DATABASE_URL)' uv run pytest

# Development workspace tools (ai/tools, ai/kb): tests + lint.
check-tools:
	python3 ai/tools/np.py test && python3 ai/tools/np.py lint
