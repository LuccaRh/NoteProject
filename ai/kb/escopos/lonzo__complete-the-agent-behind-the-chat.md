---
id: lonzo/complete-the-agent-behind-the-chat
nome: Agente do chat, lado do lonzo (issue #139)
areas: [ia]
---
## Pedido (o que a branch entrega; cada item verificável)
1. Toda pergunta leva `base_rules.md`, a data e a pasta atual.
2. `create_note` e `create_folder` exigem caminho inteiro começando em `/`, e recusam primeiro nome desconhecido.
3. A lista de skills do workspace sai por código em toda pergunta, sem o corpo.
4. O histórico guarda `tool_use` e `tool_result`.
5. Bloco fixo e pacote marcados para o cache, com `usage.cached_tokens` no evento final.
6. `create_note` devolve o id da nota, e turno vazio não entra no histórico.
7. `create_workspace.md` trata `kb/` como contexto condensado mais índice.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- `services/chat.py`, `services/workspaces.py`, `services/note_tools.py`, `services/conversations.py`, `clients/`, prompts `.md`.
- Conversas antigas seguem válidas: mensagens de texto são aceitas como antes.

## Fora (vira outra branch)
- Hooks do workspace e comando `/` para skill.
- Cortar `tool_result` grande no histórico.
