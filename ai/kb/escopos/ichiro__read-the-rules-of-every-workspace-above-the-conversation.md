---
id: ichiro/read-the-rules-of-every-workspace-above-the-conversation
nome: Regras de todos os workspaces acima da conversa, lado ichiro (issue #191)
areas: [dados, servidor]
---
## Pedido (o que a branch entrega; cada item verificável)
1. `GET /notes/{note_id}/above?path=a/b`: a nota no caminho `a/b` dentro de cada pasta
   acima de `note_id` (a raiz inclusa, `note_id` fora), da raiz para baixo; 404 quando
   `note_id` não existe, lista vazia quando nenhuma pasta tem o caminho.
2. Uma consulta só (`WITH RECURSIVE`): sobe pelo `parent_id` e desce o caminho em cada nível.
3. Testes da rota: ordem da raiz para baixo, pasta sem o caminho fica de fora, 404.
4. ichiro 0.19.0.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- O `ichiro` não sabe de `.workspace` nem de `CLAUDE.md`: o caminho vem do `lonzo`.
- O dono vem da policy `notes_owner` (RLS); a consulta não filtra `owner_id`.
- `[docs]`: página `Plano do projeto/Melhorias possíveis` (pedida na mesma conversa).

## Fora (vira outra branch)
- Usar a rota no `lonzo` (`CLAUDE.md` das pastas acima no contexto da pergunta):
  `lonzo/read-the-rules-of-every-workspace-above-the-conversation`, em cima desta.
- Foto das regras na criação da conversa e data fora do bloco das regras
  (`Melhorias possíveis`, itens 2 e 3).
