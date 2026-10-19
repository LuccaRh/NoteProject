# Vite dev server for the editor. `make check` runs the type check and the build.

.PHONY: dev check check-web check-tools install

install:
	cd apps/web && npm install

dev:
	cd apps/web && npm run dev

check: check-web

check-web:
	cd apps/web && npx tsc --noEmit && npm run build

# Development workspace tools (ai/tools, ai/kb): tests + lint.
check-tools:
	python3 ai/tools/np.py test && python3 ai/tools/np.py lint
