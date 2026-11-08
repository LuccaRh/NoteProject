---
id: lonzo/read-the-rules-of-every-workspace-above-the-conversation
nome: Regras de todos os workspaces acima da conversa, lado lonzo (issue #191)
areas: [ia]
---
## Pedido (o que a branch entrega; cada item verificável)
1. `IchiroClient.list_notes_above` chama `GET /notes/{id}/above` do `ichiro` (lista vazia no 404).
2. `workspace_rules` põe o `.workspace/CLAUDE.md` de cada pasta acima da conversa, da raiz
   para baixo, antes das notas do `.workspace/` da própria pasta; pasta sem `.workspace/`
   também recebe as regras de cima.
3. Teste do chat: ordem raiz → pasta, e o `CLAUDE.md` da própria pasta uma vez só.
4. lonzo 0.16.0.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- Em cima da `ichiro/read-the-rules-of-every-workspace-above-the-conversation` (a rota).
- Das pastas acima entra só o `CLAUDE.md`; notas e skills só da pasta da conversa.
- O fake do `ichiro` (`tests/fakes.py`) ganha a rota, senão os testes de chat com pasta quebram.

## Fora (vira outra branch)
- Foto das regras na criação da conversa e data fora do bloco das regras
  (`Melhorias possíveis`, itens 2 e 3).
- Dizer ao modelo de qual pasta vem cada `CLAUDE.md` (hoje todos têm o título `# CLAUDE.md`).
