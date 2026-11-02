---
id: ichiro/split-ichiro-into-routers-and-services
nome: Ichiro em camadas, routers → services (issue #98)
areas: [servidor]
---
## Pedido (o que a branch entrega; cada item verificável)
1. As checagens de pasta saem de `routers/notes.py` para `services/notes.py` (`list_notes`, `list_tree`, `find_by_path`, `find_note`, `create_note`, `update_note`,
   `remove_note`); cada rota chama **um** service e devolve. O `/health` também
   (`services/health.py`).
2. Erros do domínio viram exceções em `ichiro/errors.py` (no lugar de `errors/notes.py`, que
   devolvia `HTTPException`), respondidas com o status pelo `handlers.py` (tabela erro → status, um
   handler só, ligado no `main.py` por `add_handlers`); o `detail` e o status de cada erro não mudam (os testes antigos passam sem mexer).
3. O SQL sai dos routers direto para `repositories/notes.py` e `repositories/health.py`: uma função
   por consulta, devolvendo o modelo de `schemas/` ou `None`, sem regra; o `IntegrityError` sai
   como `TitleTaken`/`ParentNotFound`. Os services ficam com as checagens (`check_parent`,
   path vazio, `NoteNotFound`) e não usam `text()`. O W22 barra router que importa repository.
4. Docstring em toda função do `src/` (W21); versão 0.11.0 → 0.12.0.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- (2026-11-02, pedido do Lucca) Escrita pela sessão, revisão dele; a #73 já entrou na
  `master` (PR #99) e a branch saiu dela.
- Sem `clients/`: o ichiro não chama outra API; embaixo do service está o banco, em
  `repositories/` (pedido do Lucca, 2026-11-02; SQL com `text()`, sem ORM), e o `conn`
  segue como parâmetro (muda a cada pedido).

## Fora (vira outra branch)
- `root_path` para o `/docs` atrás do `/api`.
- Comentário em cima das fixtures do `tests/conftest.py` e o W20 em `tests/test_notes.py`.
