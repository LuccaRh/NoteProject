---
id: chimchar/call-a-skill-from-the-chat-with-a-slash-command
nome: Chamar uma skill no chat com / (issue #162)
areas: [ui]
---
## Pedido (o que a branch entrega; cada item verificável)
1. Digitar `/` no começo da pergunta lista as skills do workspace da conversa, filtradas pelo que vem depois.
2. Setas, Enter ou Tab e clique escolhem; Esc fecha; o nome entra na pergunta.
3. Ao enviar, o texto da skill vai junto com o resto da mensagem.
4. A bolha mostra só `/nome` e o resto da mensagem, também ao reabrir a conversa.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- Só front: `listWorkspaceSkills` (`skills/api.ts`) e `getNote` (`notes/api.ts`) já existem, nenhuma chamada nova.
- O texto da skill fica no histórico, então as perguntas seguintes continuam com ele.
- Texto de skill vem de outras pessoas: só `textContent`.

## Fora (vira outra branch)
- `skill_id` e injeção da skill no lonzo.
- Slash commands no editor (`Prioridade das features`, 16).
