---
id: lonzo/add-a-lonzo-migrator-user
nome: Usuário migrator do lonzo (sem issue, pedido na sessão)
areas: [dados, infra]
---
## Pedido (o que a branch entrega; cada item verificável)
1. `lonzo_migrator` é dono do banco e das tabelas e roda o Alembic (`LONZO_MIGRATION_URL`).
2. O usuário `lonzo` só lê e escreve linhas.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
Sai da branch anterior da pilha do migrator; um serviço por branch.

## Fora (vira outra branch)
- Tirar a URL de migration do container da app (depende do deploy).
