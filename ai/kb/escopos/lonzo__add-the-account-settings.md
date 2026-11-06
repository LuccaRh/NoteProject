---
id: lonzo/add-the-account-settings
nome: Configurações da conta, parte do lonzo (issue #146)
areas: [ia]
---
## Pedido
1. Tabela `settings` no banco `lonzo`, uma linha por usuário, sob policy.
2. `GET`/`PUT /chat/settings`, `GET /chat/settings/models`, `DELETE /chat/settings/key`.
3. A chave vai cifrada (Fernet, `LONZO_SECRET_KEY`) e nunca volta ao front.
4. Chave, modelo e max tokens salvos valem no chat e ao criar workspace.
5. `tools_max_turns` (padrão 20, chat e workspace) por usuário; a criação de workspace passa a usar o `max_tokens` da pessoa.
6. `thinking` por usuário (`adaptive`, `between_tools`, `disabled`; padrão `disabled`): `/models` diz o que cada modelo aceita, vindo de `capabilities.thinking.types` da API.
7. Sem linha salva, valem os padrões. Sem chave da pessoa não há chamada ao modelo: cada usuário tem a sua, e o serviço não tem chave.

## Contexto
- `clients/anthropic.py`, `services/chat.py`, `services/workspaces.py`, compose, Makefile, CI.

## Fora
- Trocar `LONZO_SECRET_KEY` com chaves salvas (hoje invalidaria todas).
