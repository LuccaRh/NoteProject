---
tags: [noteproject, dados]
---
# Row-Level Security

Num banco com dados de vários usuários na mesma tabela, cada consulta precisa trazer só as linhas de quem pediu. O jeito comum é o app escrever o filtro (`WHERE owner_id = ...`) em todo SQL. Row-Level Security (RLS) leva esse filtro para dentro do [[Postgres]]: a regra fica gravada na tabela e vale para qualquer consulta, escrita hoje ou depois.

## Como funciona

- A regra se chama *policy*: uma condição sobre a linha. O banco junta essa condição a todo `SELECT`, `UPDATE` e `DELETE`, como se fosse um `WHERE` a mais; no `INSERT`, a linha nova que não passa na condição é recusada.
- Linha que não passa na *policy* some para aquela conexão: o `SELECT` não a devolve, e o `UPDATE`/`DELETE` não a acham (0 linhas, sem erro).
- O banco precisa saber quem é o usuário. Como o app conecta sempre com o mesmo usuário de banco, o id vai numa variável da sessão, gravada no começo da [[Transação|transação]] com `SET LOCAL` (ou `set_config(..., true)`), que vale só até o `COMMIT`.
- Essa variável fica só na conexão que a gravou: cada conexão é um processo próprio do [[Postgres]], com memória própria, e as outras não enxergam o valor. Pedidos ao mesmo tempo não se atrapalham quando cada um usa uma conexão só dele durante a [[Transação|transação]], como faz um [[SQLAlchemy|pool]]; dois pedidos dividindo a mesma conexão sobrescreveriam o valor um do outro.

```sql
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE notes FORCE ROW LEVEL SECURITY;

CREATE POLICY own_notes ON notes
    USING (owner_id = current_setting('app.user_id')::uuid);

-- Each transaction says who is asking
BEGIN;
SELECT set_config('app.user_id', '018f4e2a-7b1c-7d3e-9a10-3c5d8e6f1b42', true);
SELECT * FROM notes;          -- only the rows of this user
COMMIT;
```

## Quem passa por cima

| Quem | Vê tudo? |
|---|---|
| superusuário (`postgres`) | sim, sempre |
| dono da tabela | sim, a não ser com `FORCE ROW LEVEL SECURITY` |
| usuário com `BYPASSRLS` | sim |
| outro usuário com `GRANT` na tabela | não: só o que a *policy* deixa |

> [!warning] Erros comuns
> - Testar no `psql` como superusuário e achar que a *policy* não funciona: ele ignora o RLS.
> - Variável não gravada: `current_setting('app.user_id')` dá erro (bom: nada vaza); com `current_setting('app.user_id', true)` volta `NULL` e a consulta devolve 0 linhas.
> - `SET` sem `LOCAL` numa conexão de pool: o id fica na conexão e o próximo pedido que a pegar herda o usuário errado.

## Fonte

- Postgres, "Row Security Policies": https://www.postgresql.org/docs/current/ddl-rowsecurity.html *(de memória; conferir antes de implementar)*

> [!example]
> No NoteProject, o `ichiro` usa RLS para cada pessoa ver só as próprias notas: [[RLS ou filtro em cada consulta]].
