---
id: chimchar/search-notes-from-the-web-app
nome: Busca de notas e pastas no front (issue #109)
areas: [ui, editor, cliente-api]
---
## Pedido (o que a branch entrega; cada item verificável)
1. Pop-up de busca (`notes/search.ts`), aberto pelo botão da barra, por `Ctrl+O` ou pela
   lupa de uma pasta na árvore (busca só dentro dela).
2. Modo "Everything": nomes do `GET /notes/tree` na hora, sem acento nem caixa (`fold.ts`),
   e os corpos pelo `GET /notes/search` depois de uma pausa; modo "Titles" (`alt t`): só o
   `GET /notes/search-titles`.
3. Teclas: setas, Enter abre (numa pasta, entra nela), Backspace no campo vazio sobe uma pasta.
4. Nota aberta pela busca marca as palavras no editor (`decorations/found.ts`) e rola até a
   primeira.
5. `tsc` e build passando; versão 0.7.0 → 0.8.0.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- Escrita pelo Lucca no checkout principal, sem commit; a sessão separou em commits.
- A branch sai da `ichiro/search-notes-by-title` (#107, em cima da #56), que tem as rotas de
  busca: rebase na `master` depois do merge delas (o W13 avisa `apps/ichiro` até lá).

## Fora (vira outra branch)
- Busca dentro da nota aberta (`Ctrl+F` do CodeMirror).
