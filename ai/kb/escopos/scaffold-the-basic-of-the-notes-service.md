---
id: scaffold-the-basic-of-the-notes-service
nome: Esqueleto da API de notas com /health (issue #10)
areas: [servidor]
---
## Pedido (o que a branch entrega; cada item verificável)
1. Estrutura de `apps/notes` escolhida (plana ou `src/`) e registrada em `Estrutura do projeto/API de notas`.
2. Projeto uv em `apps/notes` (Python 3.14) com `fastapi[standard]`; `pytest`, `ruff`, `mypy` como dev.
3. `GET /health` devolve 200 `{"status": "ok"}` (`curl -i localhost:8000/health`).
4. Teste com `TestClient` que confere status e corpo.
5. Alvo no `Makefile` (ruff, mypy, pytest do serviço) chamado pelo `make check`; teste quebrado faz o check falhar.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- `Makefile` (alvo novo e `check`), `.gitignore` (`.venv`, caches), README (como rodar cada serviço no navegador e testar pelo `/docs`).
- CI: job `notes` com uv rodando `make check-notes` (pedido do usuário, 2026-10-20).
- Notas `Conceitos/FastAPI` e `Estrutura do projeto/API de notas`; `ai/kb/areas.yaml` (notas da área `servidor`).

## Fora (vira outra branch)
- Dockerfile e compose (#11); Postgres, migrations, `lifespan` com pool (#12); `.env` (#13).
- Rotas `/notes` e `/search` (#46); servir o build do front (#47); login (`apps/auth`, M2).
- Mudanças no editor (`apps/web`).
