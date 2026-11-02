---
id: ichiro/filter-notes-by-title
nome: Filtro de título no GET /notes (issue #89)
areas: [servidor, dados]
---
## Pedido (o que a branch entrega; cada item verificável)
1. `GET /notes?parent_id=X&title=Y` devolve só as notas de título `Y` dentro de `X` (a raiz
   sem `parent_id`); sem `title`, a lista de sempre.
2. Testes do filtro (com e sem nota do título); versão do ichiro 0.7.0 → 0.8.0.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- (2026-11-02, pedido do Lucca, escrito pela sessão) Vem do lonzo: `find`, `find_workspace` e
  `has_rules` listam a pasta inteira para achar um nome; com o filtro, uma chamada só.
- O `notes.py` mexido passa às regras W19/W21: docstring nas rotas, argumentos com nome
  (inclusive no helper `create` dos testes), em commits próprios antes do filtro.

## Fora (vira outra branch)
- Título único por pasta (#90), nota por caminho (#91), subárvore com caminhos (#92): branches
  empilhadas em cima desta.
- Usar o filtro no lonzo: branch do `lonzo`, depois do merge.
