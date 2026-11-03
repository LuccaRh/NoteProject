---
id: ichiro/open-the-transaction-in-the-service
nome: Transação aberta no service do ichiro (issue #108)
areas: [servidor, dados]
---
## Pedido (o que a branch entrega; cada item verificável)
1. `db.py` troca o `get_conn` (dependência do FastAPI) por um `transaction()`: context
   manager que pega uma conexão do pool do `engine` global e abre a transação.
2. Routers sem `conn` nem `Depends(get_conn)`: cada rota chama o service só com os dados
   do pedido.
3. Cada service público abre `with transaction() as conn:` e passa `conn` aos
   repositories, que continuam recebendo `conn`; as consultas de um service seguem na
   mesma transação (checagem do pai + `INSERT`/`UPDATE`).
4. Service que chamava outro service (`find_note` dentro de `list_tree` etc.) não abre
   uma segunda transação.
5. Testes passando contra o Postgres (`make check`), com o savepoint por teste mantido;
   versão 0.14.0 → 0.15.0.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- Modelo: `apps/lonzo/src/lonzo/db.py` e `services/conversations.py:32`.
- A branch sai da `ichiro/search-notes-by-title` (#107), que está em cima da #56: rebase
  na `master` depois do merge das duas.

## Fora (vira outra branch)
- Async no ichiro (`create_async_engine`), como o lonzo.
