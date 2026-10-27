---
tags: [noteproject, conceito, dados]
---
# Transação

Um pedido pode mandar ao banco vários comandos que só fazem sentido juntos: apagar uma pasta é apagar as notas de dentro e depois a pasta. Se o segundo falhar, o primeiro não pode ficar valendo. Uma **transação** junta os comandos num bloco de tudo ou nada.

| Comando | O que o banco faz |
|---|---|
| `BEGIN` | abre a transação: o que vier depois fica pendente |
| `COMMIT` | grava tudo de uma vez; outras conexões passam a ver |
| `ROLLBACK` | desfaz tudo desde o `BEGIN`, como se nada tivesse sido mandado |

- Vale no [[Postgres]] e no [[SQLite]]: salvar uma nota inteira ou nada é o que um arquivo solto não dá.

## Transação no SQLAlchemy

O `engine.begin()` do [[SQLAlchemy]] pega uma conexão **e** abre a transação. É um [[Context manager|context manager]] feito com `yield`, com um `with` dentro de outro (SQLAlchemy 2.1.6, `sqlalchemy/engine/base.py:3214-3241`):

```python
@contextlib.contextmanager
def begin(self):
    with self.connect() as conn:     # saída: close → a conexão volta ao pool
        with conn.begin():           # saída: COMMIT sem erro, ROLLBACK com erro
            yield conn
```

![[transacao-por-pedido.drawio.svg]]
*O `with` de dentro fecha primeiro: a transação termina (commit ou rollback) e só depois a conexão volta ao pool.*

- Quem escolhe entre `COMMIT` e `ROLLBACK` é o `__exit__` da transação: `if type_ is None` → `commit()`, senão `rollback()` (`sqlalchemy/engine/util.py:140-159`).
- A conexão volta ao pool **sempre**, com ou sem erro: o `__exit__` da conexão só faz `self.close()` (`base.py:237`). O erro muda apenas o que a transação faz.
- Um `INSERT` seguido de um erro de Python na mesma transação não fica gravado: o erro passa pelo `yield`, e o `ROLLBACK` desfaz o `INSERT`.

Docs: [PostgreSQL — transações](https://www.postgresql.org/docs/current/tutorial-transactions.html), [SQLAlchemy — engines e conexões](https://docs.sqlalchemy.org/en/20/core/connections.html).
