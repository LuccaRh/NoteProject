---
id: lonzo/show-what-the-ai-is-doing-while-it-answers
nome: Status da IA, lado do lonzo (issue #129)
areas: [ia]
---
## Pedido (o que a branch entrega; cada item verificável)
1. O `POST /api/chat` manda um evento `tool_use` (`name`, `target`) quando uma ferramenta começa e de novo com o input inteiro.
2. `target` é o que a busca procurou, o último nome do caminho ou o título da nota, sem chamada a mais ao ichiro.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- `services/chat.py`, `services/note_tools.py`, `schemas/notes.py`. Títulos num dicionário do `NoteTools`, que dura uma resposta; desenho combinado na sessão de 2026-11-05.
- A branch sai da `chimchar/render-the-chat-answers`, última da pilha.

## Fora (vira outra branch)
- A linha de status no front: `chimchar/show-what-the-ai-is-doing-while-it-answers`.
- Guardar os status na conversa salva; mostrar quando uma ferramenta falha.
