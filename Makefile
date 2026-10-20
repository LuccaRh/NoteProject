.PHONY: dev check check-web check-tools install check-notes

install:
	cd apps/web && npm install

dev:
	cd apps/web && npm run dev

check: check-web check-notes

check-web:
	cd apps/web && npx tsc --noEmit && npm run build

check-notes:
	cd apps/notes && uv run ruff check && uv run mypy src tests \
		&& uv run pytest

# Development workspace tools (ai/tools, ai/kb): tests + lint.
check-tools:
	python3 ai/tools/np.py test && python3 ai/tools/np.py lint
