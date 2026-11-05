---
tags: [noteproject, conceito, dados]
---
# SQLAlchemy

Uma API que usa um banco servidor, como o [[Postgres]], precisa de uma conexão de rede com ele para cada consulta. Abrir uma conexão nova a cada pedido custa caro (rede, login no banco); o SQLAlchemy, a lib de banco mais usada no Python, guarda conexões abertas e as reaproveita.

| Peça | O que é | Quando existe |
|---|---|---|
| **engine** | objeto que sabe a URL do banco e cuida das conexões | um só, criado quando a API sobe |
| **pool** | conjunto de conexões abertas dentro do engine (5 fixas + até 10 extras, por padrão), um por processo, dividido por todos os pedidos | enquanto o engine vive |
| **conexão** | uma das conexões do pool, emprestada | durante uma consulta ou um pedido |

## Um pedido na API

1. O pedido chega; a rota recebe uma conexão do pool (no [[FastAPI]], por um `Depends`).
2. A rota roda a consulta (`SELECT ... FROM notes`).
3. Transforma as linhas em JSON e responde.
4. A conexão volta ao pool, aberta, para o próximo pedido.

- Consulta escrita em Python (`select(...)`, `insert(...)`, o "Core") ou com classes que viram tabelas (o ORM); as duas usam o mesmo engine.
- Comandos que só valem juntos vão numa [[Transação|transação]]: o `engine.begin()` pega uma conexão e abre a transação de uma vez ([[Transação#Transação no SQLAlchemy|transação no SQLAlchemy]]).

## Por que não uma conexão só

Uma conexão aberta no import e usada por todos os pedidos tira o parâmetro de conexão das funções, mas faz os pedidos dividirem a mesma [[Transação|transação]]:

| Problema | Exemplo |
|---|---|
| Um desfaz o outro | o pedido A grava uma nota; o B dá erro e faz `rollback()`; a nota de A some junto |
| Um grava o outro pela metade | A está entre a checagem e o `INSERT`; B faz `commit()` e grava o meio do trabalho de A |
| Fila de um | o [[Postgres]] roda um comando por vez em cada conexão: 15 pedidos ao mesmo tempo esperam um atrás do outro |
| Threads se atropelam | a `Connection` não é thread-safe; duas threads mandando comandos pelo mesmo fio embaralham as respostas *(geral)* |
| Fio caiu, caiu tudo | se o banco reinicia, a única conexão morre e nenhum pedido fala com ele até alguém reabrir |

Com o pool, cada pedido tem uma conexão só dele enquanto roda: o erro de um fica na conexão dele, e os outros seguem. O que é global é o engine (com o pool dentro); a conexão vive só durante o pedido.

## Quantas conexões bastam

O pool limita as conexões **ao mesmo tempo**, e não os usuários do site. Um pedido segura a conexão só enquanto a rota roda.

| Valor | Padrão | O que acontece no limite |
|---|---|---|
| `pool_size` | 5 | conexões abertas na primeira vez que são precisas e reaproveitadas depois (as mesmas, pedido após pedido) |
| `max_overflow` | 10 | extras, abertas no pico; ao voltar com as 5 fixas já livres, a extra é fechada: 15 no total |
| `pool_timeout` | 30 s | o 16º pedido espera uma conexão livre; passado o prazo, erro |

- Consulta simples leva na casa de milissegundos: 15 conexões × ~2 ms cada ≈ 7 mil consultas por segundo. Mil pessoas com o site aberto quase nunca pedem algo no mesmo milissegundo. *(geral)*
- Mais conexões nem sempre rendem mais: o banco tem poucos núcleos de CPU, e consultas além disso disputam CPU entre si. O Postgres ainda limita o total (`max_connections`, 100 por padrão). *(geral)*
- Para escalar, roda-se **vários processos** da API, cada um com seu pool; quando a soma passa do limite do banco, um PgBouncer na frente reparte poucas conexões reais entre muitos processos. *(geral)*
- Manter a conexão aberta poupa o aperto de mão do [[TCP]] e o login a cada pedido.

Os padrões são da classe `QueuePool` (SQLAlchemy 2.1.6, `sqlalchemy/pool/impl.py:75-77`); a extra que volta com o pool cheio é fechada em `_do_return_conn` (`impl.py:141-148`).

## Quem usa o banco, e quando

```
.env (ICHIRO_DATABASE_URL)
 ├─► Alembic ──(SQLAlchemy)──► cria/altera tabelas   [só quando o schema muda]
 └─► API ──────(SQLAlchemy)──► lê/escreve linhas     [a cada pedido]
```

- O Alembic ([[Migration|migrations]]) muda o schema (o formato: tabelas, colunas) e sai. A API só lê e escreve os dados (as linhas) e conta que as tabelas já existem.
- Os dois usam o SQLAlchemy por baixo e a mesma URL do `.env`, cada um com o seu engine; um não usa a configuração do outro.

> [!example] No NoteProject
> A [[API de notas]] cria o engine com a `ICHIRO_DATABASE_URL`, e cada função de serviço abre uma transação com uma conexão do pool; a rota não recebe conexão.

Docs: [SQLAlchemy — engines e conexões](https://docs.sqlalchemy.org/en/20/core/connections.html), [pool](https://docs.sqlalchemy.org/en/20/core/pooling.html). Postgres: [max_connections](https://www.postgresql.org/docs/current/runtime-config-connection.html). PgBouncer: [pgbouncer.org](https://www.pgbouncer.org/).
