---
id: chimchar/show-what-the-ai-is-doing-while-it-answers
nome: Status da IA, lado do chimchar (issue #129)
areas: [ui, cliente-api]
---
## Pedido (o que a branch entrega; cada item verificável)
1. Enquanto a IA responde, uma linha embaixo da resposta diz o que ela faz: `Searching "caddy"`, `Reading "Caddy"`.
2. A linha some quando volta o texto e no fim da resposta, mesmo se ela for cancelada.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- `chat/api.ts`, `chat/chat.ts`, `style.css`. O `cliente-api` é do usuário, mas ele pediu a tarefa pronta.
- A branch sai da `lonzo/show-what-the-ai-is-doing-while-it-answers`, que manda o evento `tool_use`.

## Fora (vira outra branch)
- Guardar os status na conversa salva; mostrar quando uma ferramenta falha.
