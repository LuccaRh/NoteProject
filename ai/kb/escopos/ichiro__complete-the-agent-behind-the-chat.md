---
id: ichiro/complete-the-agent-behind-the-chat
nome: Agente do chat, lado do ichiro (issue #139)
areas: [ia]
---
## Pedido (o que a branch entrega; cada item verificável)
1. `GET /notes/{id}/path` devolve o caminho de títulos desde a raiz, e 404 para uma nota que não existe.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- O lonzo usa essa rota para dizer ao modelo em que pasta a conversa está.
- `repositories/notes.py`, `services/notes.py`, `routers/notes.py`.

## Fora (vira outra branch)
- O uso no lonzo: `lonzo/complete-the-agent-behind-the-chat`.
- Esconder as mensagens de ferramenta no chat: `chimchar/complete-the-agent-behind-the-chat`.
