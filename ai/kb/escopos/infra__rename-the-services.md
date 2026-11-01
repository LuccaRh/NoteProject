---
id: infra/rename-the-services
nome: Renomear os serviços web → chimchar e notes → ichiro (issue #80)
areas: [infra]
---
## Pedido (o que a branch entrega; cada item verificável)
1. `apps/web` → `apps/chimchar` e `apps/notes` → `apps/ichiro` (pacote Python `src/ichiro`), com os nomes no compose, no Caddyfile, no Makefile, no CI e nos manifestos.
2. `make check` passa; `https://notes.localhost` serve o front e `/api/health` pelos serviços novos.
3. Workspace e vault (estado e plano) com os nomes novos; o serviço de IA planejado vira `lonzo`.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- Exceção ao "um serviço por branch" (W13): o rename não se divide sem deixar o compose com nomes misturados.

## Fora (vira outra branch)
- Domínio: tabela `notes`, rotas `/notes`, `src/notes/api.ts` do front, `notes.localhost`.
- Histórico: escopos de branches antigas, páginas de issues feitas, commits já mergeados.
