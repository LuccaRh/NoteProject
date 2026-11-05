---
tags: [noteproject, dados, auth, decisao]
---
# RLS ou filtro em cada consulta

Com o login (#48), cada nota passa a ter dono, e o `ichiro` só pode ler, editar e apagar as notas de quem pediu. Hoje nenhuma tabela tem `owner_id` e nenhuma consulta filtra por usuário. A decisão é onde mora esse filtro: no SQL de cada consulta ou no [[Postgres]], com [[Row-Level Security]].

## Opções

| | [[Row-Level Security\|RLS]] | Filtro em cada consulta |
|---|---|---|
| O que muda no `ichiro` | uma [[Migration\|migration]], o `transaction()` do `db.py` e um middleware | rotas, services e as 12 funções de `repositories/notes.py` |
| Consulta nova | já nasce filtrada | precisa do `WHERE owner_id`; esquecer vaza notas de outro usuário |
| Ler o código | o filtro não aparece no SQL, está na tabela | o filtro está em cada consulta |
| Depurar | nota sumida pode ser a *policy*; no `psql` como superusuário tudo aparece | o que roda é o que está escrito |
| Armadilha | conectar como dono ou superusuário desliga o filtro; o id tem de chegar em toda [[Transação\|transação]] | o esquecimento |
| Banco | só Postgres | qualquer um |

Critério: proteger também as consultas que ainda vão nascer, com pouca mudança no código que existe. O chat (`lonzo`) acumula ferramentas que chamam o `ichiro`, e cada rota nova seria mais um `WHERE` para lembrar.

## Escolha: RLS

```
Caddy ── X-User-Id ──▶ middleware do ichiro ── contextvar
db.transaction() ── set_config('app.user_id', id, true) ──▶ Postgres
                                         policy: owner_id = app.user_id
```

- Migration: coluna `owner_id` nas notas, com `DEFAULT` igual ao usuário do pedido (o `INSERT` fica igual), índice nela, a *policy* e `ENABLE` + `FORCE ROW LEVEL SECURITY`.
- O `ichiro` conecta com um usuário de banco sem `BYPASSRLS` e que não é superusuário.
- Um middleware guarda o id do usuário numa [[ContextVar|contextvar]]; o `transaction()` grava esse id na transação. Rotas, services e consultas não mudam.
- O `lonzo` só repassa o usuário ao `ichiro` em cada chamada: as ferramentas do chat ficam presas às notas dele pelo próprio `ichiro`. As tabelas do `lonzo` (`conversations`) ganham o próprio `owner_id`.
- O filtro escondido se cobre com teste: notas de dois usuários, e cada rota confere que um não vê nem mexe nas do outro.

⏳ Está na branch `ichiro/add-browser-login-with-a-session-cookie` da #48, ainda sem PR nem merge; o usuário chega ao `ichiro` como em [[Login no navegador]]. A contextvar chegar às rotas `def` (que rodam em thread) precisa ser conferida no Starlette.

## A migration

A [[Migration|migration]] `cb9bed2be48a` dá um dono a cada nota e liga o [[Row-Level Security|RLS]]. A expressão abaixo aparece no `DEFAULT` e na *policy*, sempre como texto SQL gravado na tabela; o [[Postgres]] a calcula a cada linha, lendo o `app.user_id` que o `set_user` do `db.py` gravou com `set_config`.

```sql
nullif(current_setting('app.user_id', true), '')::uuid
```

- `current_setting(..., true)`: lê a variável e volta `NULL` se ela não existe, sem erro.
- `nullif(..., '')`: sem usuário, o `db.py` grava `""`, e `''::uuid` daria erro; o `nullif` troca por `NULL`.
- `::uuid`: converte o texto para o tipo do `owner_id`.

Com `NULL`, `owner_id = NULL` nunca é verdadeiro: nenhuma linha passa, e um `INSERT` falha no `NOT NULL`.

Passos do `upgrade()`, na ordem:

| Passo | O que faz | Por quê |
|---|---|---|
| Conferir o dono | lê `-x owner=<id>`; se há notas e não veio dono, para com erro | nota antiga precisa de dono antes de `owner_id` virar obrigatório |
| Criar `owner_id` | coluna `uuid` aceitando `NULL` | as linhas antigas ainda estão sem valor |
| Preencher | passa as notas antigas para o `owner` | tira os `NULL` |
| Fechar a coluna | `NOT NULL`, com `DEFAULT` = usuário do pedido | o `INSERT` dos repositories não muda |
| [[Índice]] | `notes_owner_id_idx` | toda consulta passa a filtrar por `owner_id` |
| Trocar o `UNIQUE` | de `(parent_id, title)` para `(owner_id, parent_id, title)` | dois usuários podem repetir título na mesma pasta |
| Criar a *policy* | `notes_owner`, com `USING` e `WITH CHECK` | `USING` filtra as linhas que a consulta enxerga; `WITH CHECK` barra gravar linha de outro dono |
| `ENABLE` | liga o RLS na tabela | a *policy* só vale com isso |
| `FORCE` | aplica o RLS ao dono da tabela | sem ele, o dono ignoraria a *policy* |
| `GRANT` | dá `SELECT`, `INSERT`, `UPDATE` e `DELETE` ao usuário de banco `ichiro` | o app conecta com esse usuário, que não é superusuário |

## Revisar se...

- Algum processo precisar ler notas de vários usuários na mesma transação (worker, admin, busca global): pede um usuário de banco à parte, com `BYPASSRLS`.
- O `ichiro` deixar o Postgres.
- Depurar a *policy* virar custo frequente.
