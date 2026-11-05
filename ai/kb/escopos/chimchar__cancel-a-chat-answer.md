---
id: chimchar/cancel-a-chat-answer
nome: Cancelar uma resposta do chat (issue #127)
areas: [ui, cliente-api]
---
## Pedido (o que a branch entrega; cada item verificável)
1. O botão Send vira Cancel enquanto a IA responde, e clicar cancela o pedido.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- `chat/api.ts`, `chat/chat.ts`, `style.css`. O lonzo não muda: a conexão fechada já cancela o
  stream, conferido com uma API falsa, direto e pelo Caddy.

## Fora (vira outra branch)
- Salvar o pedido cancelado ou a resposta parcial.
- Traceback do tool runner ao desligar o lonzo depois de um cancelamento.
