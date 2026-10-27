---
id: notes/apply-the-code-rules-to-the-old-notes-files
nome: Regras de import e de tipo nos arquivos antigos do notes, sem ignores (issue #57)
areas: [servidor]
---
## Pedido (o que a branch entrega; cada item verificável)
1. `pyproject.toml` do notes com `lines-after-imports = 2` e mypy `strict`, sem `per-file-ignores`.
2. Arquivos antigos (`main.py`, `db.py`, `routers/health.py`, migrations) corrigidos; `make check` passa.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- Versão do serviço (W11) e o escopo desta branch.

## Fora (vira outra branch)
- Rotas `/notes` (#46): branch `notes/expose-the-notes-api-on-the-server`, em cima desta.
- Comentários das três partes (W16) e linhas em branco (W14) nos arquivos antigos.
