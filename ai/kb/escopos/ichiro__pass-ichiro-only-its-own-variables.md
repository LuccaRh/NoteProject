---
id: ichiro/pass-ichiro-only-its-own-variables
nome: Só as variáveis do ichiro no container dele (issue #145)
areas: [infra]
---
## Pedido
1. O container do `ichiro` recebe só `ICHIRO_DATABASE_URL` e `ICHIRO_MIGRATION_URL`, por `environment:`.

## Contexto
- `docker-compose-dev.yml`, serviço `ichiro`. O `.env` continua igual.

## Fora
- `env_file` do `postgres`: ele precisa das senhas no init; recebe a chave da Anthropic sem usar.
