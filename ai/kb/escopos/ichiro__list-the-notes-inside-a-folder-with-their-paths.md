---
id: ichiro/list-the-notes-inside-a-folder-with-their-paths
nome: Árvore de uma pasta com os caminhos (issue #92)
areas: [dados, servidor]
---
## Pedido (o que a branch entrega; cada item verificável)
1. `GET /notes/tree?parent_id=X` devolve tudo dentro de `X` (a raiz sem `parent_id`), em
   qualquer nível, como `[{id, path, is_folder}]`, sem o `body`, na ordem de uma árvore de
   arquivos; `X` que não existe → 404.
2. Testes (pasta com subpasta, raiz, pasta vazia, pasta que falta); versão do ichiro
   0.10.0 → 0.11.0.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- (2026-11-02, pedido do Lucca, escrito pela sessão) Empilhada na #91. Para o lonzo: na #77 o
  modelo vê o workspace como lista de caminhos numa chamada; o `workspace_rules` cai de 4
  chamadas para 2.
- Query param (`?parent_id=`) e não `/notes/{id}/tree`: assim vale também para a raiz, como o
  `GET /notes` e o `by-path`.
- `WITH RECURSIVE` que desce guardando `names text[]`; o `path` é `array_to_string(names,
  '/')`, e a ordem é por `names` (array compara nome a nome, então `Plans/Week` vem antes de
  `Zebra`; ordenar pelo texto deixaria a colação mexer na `/`).
- `schemas/notes.py` mexido: docstrings (W21) num commit próprio.

## Fora (vira outra branch)
- Limite de profundidade ou paginação para pasta enorme.
- Pastas antes das notas dentro de cada nível (hoje é só a ordem dos títulos).
