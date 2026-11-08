---
id: lonzo/read-the-skills-of-every-workspace-above-the-conversation
nome: Skills de todos os workspaces acima da conversa (issue #192)
areas: [ia]
---
## Pedido (o que a branch entrega; cada item verificável)
1. O bloco `# Skills` da pergunta traz as skills do `.workspace/skills` de cada pasta acima da
   conversa, da raiz para baixo, com as da pasta mais próxima por último, num bloco só.
2. Pasta sem `.workspace/` também recebe as skills de cima.
3. Teste do chat: ordem raiz → pasta, e as skills da própria pasta uma vez só.
4. lonzo 0.17.0.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- Em cima da `lonzo/read-the-rules-of-every-workspace-above-the-conversation` (#191).
- Usa `list_notes_above(path=".workspace/skills")`; só o corpo fica fora da lista, como hoje.

## Fora (vira outra branch)
- Menu `/` e aba Skills: mostram só as skills do workspace (2026-11-08).
- Duas skills de mesmo título em níveis diferentes: as duas entram na lista.
