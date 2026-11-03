---
id: lonzo/let-the-chat-read-and-search-notes
nome: O chat lê e busca as notas do workspace (issue #77)
areas: [ia, servidor]
---
## Pedido (o que a branch entrega; cada item verificável)
1. `IchiroClient.search_notes(query, parent_id)` → `GET /notes/search` do ichiro (#56),
   devolvendo `list[NoteMatch]` (`{id, title}`).
2. Ferramentas do chat em `NoteTools` (`services/note_tools.py`, um conjunto só com as de
   criar da #73), sem trava de pasta (2026-11-02 e 2026-11-03, pedido do Lucca: a IA lê e cria
   em qualquer pasta; `create_note`/`create_folder` ganham `folder_id?`, sem ele a raiz): `search_notes(query, folder_id?)` (`GET /notes/search`; sem
   pasta, todas as notas), `search_titles(text, folder_id?)` (`GET /notes/search-titles`,
   ILIKE: acha pastas e pedaço de palavra), `list_folder(folder_id?)` (`GET /notes?parent_id`; sem pasta, a
   raiz) e `read_note(id)` (`GET /notes/{id}`, título + corpo).
3. `POST /api/chat` responde pelo `tool_runner(stream=True)`, com ou sem `folder_id`: o
   modelo busca, lista e lê até responder; o texto de todas as voltas sai em `text_delta`.
4. Testes com o ichiro e a API falsos; versão do lonzo sobe a minor.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- A rota `/notes/search` está na branch `ichiro/search-notes-with-postgres-full-text-search`
  (#56, sem merge): esta sai da `master`; os testes não dependem dela, a conferência ao vivo sim.
- Feita num worktree (`../NoteProject-lonzo-search`): a pasta principal tem outras sessões.

## Fora (vira outra branch)
- Guardar as voltas de ferramenta (`tool_use`/`tool_result`) no histórico da conversa: hoje
  fica só a pergunta e o texto final.
- Mostrar o `status` na tela do chat (chimchar).
- Editar/apagar pelo chat (#78).
