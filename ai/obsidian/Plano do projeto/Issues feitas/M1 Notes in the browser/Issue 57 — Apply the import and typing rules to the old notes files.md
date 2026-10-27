---
tags: [noteproject, plano, servidor]
---
# #57 Apply the import and typing rules to the old notes files

Issue do [[M1 Notes in the browser]]. O `pyproject.toml` do `notes` liga o ruff isort com `lines-after-imports = 2` e o mypy `strict`, e os arquivos antigos (`main.py`, `db.py`, `routers/health.py`, `migrations/env.py` e a migration `create_notes`) ganham a segunda linha em branco depois dos imports. O `notes` sobe para `0.4.0`. Passou por Python, lint e as notas do vault.

## Python

- ruff isort com `lines-after-imports = 2`: duas linhas em branco entre os imports e o resto, em todo arquivo do serviço, sem exceção por arquivo.
- mypy `strict = true`: todo parâmetro e retorno com tipo; os arquivos antigos já passavam, então só a config mudou.
- Ficou para depois: os comentários das três partes (W16) e as linhas em branco em volta dos blocos (W14) nos arquivos antigos.

## Lint

- Lint é um programa que lê o código sem rodá-lo e aponta o que quebra uma regra: ruff (estilo e erros de Python), mypy (tipos), tsc (TypeScript) e o `ai/np lint` (W01–W16, as regras do workspace) ([[Como usar]]).
- "Regra vira lint": o que dá para conferir por código vai para uma ferramenta, e não fica num pedido escrito para a IA lembrar.

## Notas do vault

- Workspace: saiu do `CLAUDE.md` a exceção que deixava as regras de forma (W14–W16) só para arquivo criado na branch; a branch não mexeu em notas do vault.
