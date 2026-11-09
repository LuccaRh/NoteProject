---
id: chimchar/list-every-folder-in-the-workspace-dialog
nome: Todas as pastas no pop-up Create workspace, travando as que já têm workspace (issue #230)
areas: [ui]
---
## Pedido (o que a branch entrega; cada item verificável)
1. O seletor Folder do pop-up lista todas as pastas, em qualquer profundidade (vem do
   `listTree()`, não das pastas já abertas na árvore), menos as de dentro de `.workspace`.
2. Pasta que já tem `.workspace` aparece desabilitada, marcada `(workspace)`; não dá para
   escolher. Pasta dentro de um workspace (sem `.workspace` própria) pode.
3. chimchar 0.34.0 (commit só da versão).

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- Em cima da `lonzo/stream-the-workspace-creation` (#229).
- `listTree()` já existe (`notes/api.ts`); o pop-up só passa a usá-lo.

## Fora (vira outra branch)
- Trava no lonzo: o `create_workspace` reaproveita a `.workspace` de uma tentativa que falhou
  no meio (teste `test_workspace_reuses_the_folders_already_there`); travar lá quebra isso.
