---
id: infra/indent-the-docker-compose-file-with-4-spaces
nome: Indentação de 4 espaços no compose (issue #69)
areas: [infra]
---
## Pedido (o que a branch entrega; cada item verificável)
1. `docker-compose-dev.yml` com 4 espaços; `docker compose config -q` passa.
2. `.editorconfig`: `docker-compose*.yml` com 4 espaços (o resto do YAML segue com 2).

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- Mesma regra da #65 (web com 4 espaços), agora no compose.

## Fora (vira outra branch)
- YAML do CI (`.github/`) e do workspace (`ai/`), que seguem com 2.
- Mudança de serviço, porta ou volume no compose.
