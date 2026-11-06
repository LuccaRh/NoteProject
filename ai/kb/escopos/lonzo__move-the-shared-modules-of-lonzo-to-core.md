---
id: lonzo/move-the-shared-modules-of-lonzo-to-core
nome: Módulos compartilhados do lonzo em core/ (issue #151)
areas: [ia]
---
## Pedido
1. `db`, `connections`, `user`, `lifespan`, `handlers` e `errors` saem da raiz do pacote para `core/`, ao lado do `cipher`.
2. O lint W22 continua pegando router que importa de `core/db` e `core/connections`.

## Contexto
- Só caminhos e imports; nenhum comportamento muda.
- Um commit por módulo.

## Fora
- `ichiro` e `nujabes`, que têm os mesmos módulos na raiz (uma branch por serviço).
- `base_rules.md` e `create_workspace.md` em `prompts/`.
