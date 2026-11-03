---
id: lonzo/let-the-chat-create-edit-and-delete-notes
nome: O chat cria, edita e apaga notas em qualquer pasta (issue #78)
areas: [ia, servidor]
---
## Pedido (o que a branch entrega; cada item verificável)
1. No `NoteTools` (`services/note_tools.py`, o conjunto único da #77, sem trava de pasta:
   2026-11-03, a IA mexe onde quiser): `edit_note(note_id, old_text, new_text)` (o trecho tem de
   aparecer uma vez só; senão erro pedindo mais texto) e `delete_note(note_id)` (pasta vai com
   tudo dentro); o chat recebe as duas.
2. `IchiroClient.update_note` (PATCH) e `delete_note` (DELETE).
3. Testes com o ichiro falso (PATCH/DELETE no fake); lonzo 0.7.0.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- Sai da `lonzo/let-the-chat-read-and-search-notes` (#77, sem push): rebase na `master` depois
  do merge dela.
- Conferido ao vivo no container do lonzo contra o ichiro do compose (sem o Claude).

## Fora (vira outra branch)
- ichiro: o commit do `get_conn` roda depois da resposta (`Depends` sem `scope="function"`), então
  ler logo depois de apagar às vezes ainda acha a nota (3 de 5 vezes ao vivo).
- Edição como sugestão (#32); guardar as voltas de ferramenta no histórico.
