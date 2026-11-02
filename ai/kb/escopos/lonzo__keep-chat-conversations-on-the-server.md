---
id: lonzo/keep-chat-conversations-on-the-server
nome: Conversas do chat guardadas no servidor (issue #75)
areas: [dados, servidor, ia]
---
## Pedido (o que a branch entrega; cada item verificável)
1. Banco `lonzo` no Postgres do compose, com usuário próprio; o lonzo lê só
   `LONZO_DATABASE_URL` (nunca a senha do ichiro). Migrations do Alembic em `apps/lonzo/`.
2. Tabelas (primeira migration):
   - `conversations`: `id uuid` (`uuidv7()`), `folder_id uuid` nulo = raiz, sem FK (a pasta
     mora no ichiro), `title text`, `created_at`, `updated_at`.
   - `messages`: `id uuid` (`uuidv7()`), `conversation_id` FK `ON DELETE CASCADE`, `role text`
     com check `user`/`assistant`, `content jsonb` (lista de blocos da Messages API),
     `created_at`; índice em `(conversation_id, id)`.
3. `POST /api/chat {question, folder_id?, conversation_id?}`: sem `conversation_id`, cria a
   conversa (título = começo da pergunta) e devolve o id no `message_start`; com ele, manda o
   histórico guardado ao modelo antes da pergunta. A pergunta e a resposta inteira são gravadas
   no fim da resposta.
4. `GET /api/chat/conversations?folder_id=` (lista, mais recente primeiro) e
   `GET /api/chat/conversations/{id}` (a conversa com as mensagens); conversa que não existe → 404.
5. Done (da issue): a conversa mantém as mensagens depois de recarregar a página e reiniciar o
   serviço. Testes com Postgres de verdade (como o ichiro) e modelo falso; versão 0.3.0 → 0.4.0.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- `docker-compose-dev.yml` (bloco do lonzo): `LONZO_DATABASE_URL`, `depends_on: postgres`.
- `.env.example`, `Makefile` (`check-lonzo` troca `@postgres:` por `@localhost:`), CI
  (`ci.yml`: Postgres descartável no job; o lonzo usa o banco do superusuário, sem criar usuário).
- (2026-11-02) Título = os 80 primeiros caracteres da pergunta. A conversa nasce antes da
  resposta (o id vai no `message_start`); erro da API no meio → nada gravado daquela troca.
  Com `conversation_id`, as regras são as do workspace da conversa (o `folder_id` do pedido
  não vale).
- Testes: o dev DB é compartilhado → cada teste apaga as conversas que criou (`conftest.py`).
- Conferido (2026-11-02) pelo Caddy: segunda pergunta lembra a primeira; depois de
  `restart lonzo`, `GET /api/chat/conversations/{id}` traz as 4 mensagens.
- Mesmo jeito do ichiro: SQLAlchemy Core com `text()`, `psycopg`, Alembic à mão; no lonzo, o
  engine é async (`create_async_engine`), porque o chat é streaming.
- Camadas: `routers/` → `services/` → `repositories/` (banco) e `clients/` (APIs).

## Fora (vira outra branch)
- Criar o banco e o usuário `lonzo` no Postgres (script em `/docker-entrypoint-initdb.d`):
  serviço `postgres`, branch `postgres/create-the-lonzo-database`, na mesma issue.
- Apagar e renomear conversa; título gerado pelo modelo.
- Blocos `tool_use`/`tool_result` (#77); `model` e tokens por mensagem; `user_id` (#48).
- Tela do chat (#76).
