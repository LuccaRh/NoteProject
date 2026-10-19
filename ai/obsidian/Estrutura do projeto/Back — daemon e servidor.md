---
tags: [noteproject, daemon, dados, sync, servidor, auth]
---
# Back — daemon e servidor

O back começa pelo **servidor** na internet, que atende o [[Navegador|navegador]] ([[Roadmap]], M0–M4). O **[[O daemon notesd|daemon]] em cada dispositivo** vem com o app desktop (milestone Desktop app). Os dois resolvem problemas diferentes:

| | [[O daemon notesd\|Daemon]] local ([[O daemon notesd\|`notesd`]]) | Servidor de sync |
|---|---|---|
| problema | o app desktop funcionar offline | a mesma nota em vários dispositivos |
| dono de | `notes.db` ([[SQLite e FTS5\|SQLite + FTS5]]) | [[Postgres e migrations\|Postgres]] (metadados) + [[S3 — armazenamento de objetos\|S3]] (conteúdo grande) |
| sem rede | funciona inteiro | — |
| milestone | Desktop app ⏳ | M0–M4 ⏳ |

![[estrutura-back.drawio.svg]]
*À esquerda o [[O daemon notesd|daemon]] do app desktop; à direita o servidor, feito primeiro. [[Redis pub-sub|Redis]] só com mais de uma instância.*

## Daemon local (⏳, Desktop app)

- `notesd` (FastAPI + [[SQLite e FTS5|SQLite]]); desenho em [[O daemon notesd]]; por que um dono só: [[Daemon]].
- Segue as regras do servidor: título do primeiro heading, [[Pastas, campos e views|pastas e campos]] (`parent_id`, `fields`), busca full-text.

## Servidor (⏳)

Primeiro: **persistir, servir o [[Navegador|navegador]] e autenticar** (M0–M2). Depois: **sincronizar** (M4) e **servir o bootstrap** ao app desktop. O servidor serve o build do front e as rotas `/notes` e `/search` que o front vai chamar.

| Peça | Papel |
|---|---|
| `notes` (FastAPI) | rotas de notas e busca, upload, export; para o navegador, o build do front |
| `auth` (FastAPI) | login, sessões, bootstrap do app desktop |
| `worker` | pedidos de IA da [[Fila de pedidos\|fila]], depois da v1 |
| [[WebSocket]] + y-py | recebe updates [[CRDT e Yjs\|Yjs]], faz o merge, repassa aos outros dispositivos |
| [[Postgres e migrations\|Postgres]] | `users`, `notes` com `parent_id`, `fields` e `version BIGINT` por usuário |
| [[S3 — armazenamento de objetos\|S3]] | snapshots [[CRDT e Yjs\|Yjs]], imagens, ink, [[Backup e restore\|backups]] ([[AWS ou infra própria]]) |
| [[Redis pub-sub\|Redis]] | pub/sub entre instâncias de [[WebSocket]]; **não** na primeira versão |

### Como uma nota chega no outro dispositivo

1. Tecla → editor na hora (~0 ms) e, no desktop, [[SQLite e FTS5|SQLite]] local.
2. [[CRDT e Yjs|Yjs]] gera um update → [[WebSocket]] → servidor faz o merge.
3. Os outros dispositivos recebem em ~50–200 ms.
4. Dispositivo que ficou offline pede [[Sync por versão|`version > N`]] e recebe só o que mudou.

- [[WebSocket]]: endpoint `/sync` (#27 do [[Roadmap]]); atrás do [[Reverse proxy|Caddy]], a conexão tem de passar pelo proxy sem ser cortada (#30).
- [[Sync por versão]]: `version BIGINT` em `notes`, contador por usuário, uma consulta acha tudo (#29).
- [[Postgres e migrations|Postgres]] (#12): [[Container e Docker Compose|container]] no compose, volume no disco da [[EC2]], cópia diária em [[Backup e restore|backup]].
- Até o [[CRDT e Yjs|Yjs]] chegar, o `PATCH /notes/{id}` troca o texto inteiro; a [[Edição por âncora]] evita que a IA apague o que foi digitado.

### Auth

- Cada nota tem `owner_id`. No [[Navegador|navegador]], o login é por [[Autenticação|cookie de sessão]] (#48).
- No app desktop, depois, o [[O daemon notesd|daemon]] guarda um [[Token por dispositivo|token por dispositivo]] (#14 e #15, milestone Desktop app).

> [!warning] Em aberto: onde mora o documento Yjs
> Duas opções: conteúdo Markdown no [[S3 — armazenamento de objetos|S3]] com `y-websocket` (Node), ou y-py (Python) no servidor com só `content_key` no [[Postgres e migrations|Postgres]]. Decidir antes de M4 (#26 no [[Roadmap]]).
