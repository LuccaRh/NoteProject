---
id: wrap-app-code-at-80-columns
nome: Código do app com até 80 colunas (issue a abrir)
areas: [editor, servidor, workspace]
---
## Pedido (o que a branch entrega; cada item verificável)
1. Código de `apps/notes` com até 80 colunas; ruff `E501` com `line-length = 80`.
2. Código de `apps/web` com até 80 colunas; lint W12 (`ai/np lint`) cobre o que o ruff não vê.
3. Versão de cada serviço mexido sobe num commit só dela (`Update <serviço> version to X.Y.Z`).

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- `CLAUDE.md`, skill `/commit`, `ai/tools/np.py` (W11, W12) e a nota `Plano do projeto/Regras de git`.

## Fora (vira outra branch)
- Postgres, migrations e `.env` (#12, #13): branch `add-postgres-with-migrations-to-the-server`, em cima desta.
