---
tags: [noteproject, dados, auth]
---
# Isolamento por usuário

Com login, cada pessoa só pode ver as próprias notas, conversas e configurações. A escolha foi pôr essa regra no [[Postgres]], com [[Row-Level Security]], em vez de um `WHERE owner_id = ...` em cada consulta ([[RLS ou filtro em cada consulta]]).

## Um banco e dois usuários por serviço

Um Postgres só, um banco por serviço (`ichiro`, `lonzo`, `nujabes`), criados por scripts em `postgres/init/` na primeira subida ([[Bancos dos serviços]]).

| [[Usuários do banco\|Usuário do banco]] | Pode | Usado por |
|---|---|---|
| `<serviço>_migrator` | dono do banco e das tabelas; `BYPASSRLS` | Alembic (`*_MIGRATION_URL`) |
| `<serviço>` | só `SELECT/INSERT/UPDATE/DELETE` (via `ALTER DEFAULT PRIVILEGES`), `NOBYPASSRLS` | o app (`*_DATABASE_URL`) |

- O app nunca é superusuário nem dono: um bug não consegue `DROP TABLE` nem desligar o RLS.
- Senhas entram no script como variáveis do psql (`:'password'`), que o psql cita: sem injeção pelo `.env`.

## Como o RLS sabe quem é o usuário

```sql
CREATE POLICY notes_owner ON notes
  USING      (owner_id = nullif(current_setting('app.user_id', true), '')::uuid)
  WITH CHECK (owner_id = nullif(current_setting('app.user_id', true), '')::uuid);
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE notes FORCE ROW LEVEL SECURITY;
```

1. O Caddy põe o `X-User-Id` no pedido ([[Login e gateway]]); um middleware guarda numa [[ContextVar]].
2. Toda [[Transação|transação]] começa com `SELECT set_config('app.user_id', :id, true)`.
3. O `true` = vale só até o fim da transação. A conexão volta ao pool limpa: o próximo pedido não herda o usuário.
4. Sem usuário, o valor é `''` → `NULL` → nenhuma linha passa.

- `USING` filtra o que se lê, atualiza e apaga; `WITH CHECK` barra gravar linha de outro dono.
- `FORCE` aplica a policy até ao dono da tabela.
- `owner_id` tem default = a mesma expressão: o `INSERT` não muda, o banco preenche o dono.
- Mesmo desenho em `conversations`, `messages`, `settings` e `skills` do `lonzo`. Em `skills`, duas policies: `FOR SELECT` para todo logado (skill publicada) e escrita só do dono.

## A IA também passa pelo RLS

O `lonzo` chama o `ichiro` por HTTP; um hook do cliente `httpx` copia o usuário da `ContextVar` para o `X-User-Id`. A IA então só enxerga as notas de quem perguntou, sem nenhuma checagem no código do `lonzo`.

## Migration que deu dono às notas

A coluna `owner_id` entrou com notas já no banco: a migration exige `alembic -x owner=<id> upgrade head` para atribuir as antigas, depois põe `NOT NULL`, troca a unicidade para `(owner_id, parent_id, title)`, cria a policy e liga o RLS.

## Se perguntarem

- **"Por que RLS e não filtro no código?"** Esquecer um `WHERE` vira vazamento entre usuários; com RLS, o esquecimento devolve zero linhas. Custo: a regra fica menos visível no código e o teste precisa rodar com um usuário sem `BYPASSRLS`.
- **"E com pool de conexões?"** `set_config(..., true)` é local à transação; cada pedido abre a sua, então nada vaza entre pedidos que reusam a conexão.
- **"Um banco por serviço no mesmo Postgres?"** Isolamento lógico e de credenciais com custo zero de operação; separar em instâncias depois não muda o código.
