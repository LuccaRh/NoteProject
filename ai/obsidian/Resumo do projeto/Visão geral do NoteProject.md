---
tags: [noteproject, arquitetura]
---
# Visão geral do NoteProject

Um app de notas em [[Markdown]] com um chat de IA que lê e escreve nas notas. Nasceu para dois fins: uso diário e aprender engenharia de sistemas (servidor, banco, auth, infra, sync). A v1 é ler notas no navegador com o servidor na AWS ([[Objetivo do app]]); hoje tudo roda em localhost, no [[Docker Compose|compose]].

## Os serviços

Cada serviço é uma pasta em `apps/`, um [[Container|container]] e, no backend, um banco próprio. Os nomes são apelidos, sem ligação com a função.

| Serviço | Função | Stack | Versão |
|---|---|---|---|
| `chimchar` | front: editor, árvore, chat | Vite + TypeScript, [[CodeMirror\|CodeMirror 6]] | 0.34.0 |
| `ichiro` | notas e pastas, busca | [[FastAPI]] síncrono, [[SQLAlchemy]] Core, psycopg 3 | 0.19.0 |
| `lonzo` | chat com IA, skills, configurações | FastAPI async, SDK `anthropic`, SQLAlchemy async | 0.21.0 |
| `nujabes` | login e sessões | FastAPI síncrono, `pgcrypto` | 0.2.0 |
| `caddy` | [[Reverse proxy\|reverse proxy]], [[TLS]], confere a sessão | Caddy 2.11 | — |
| `postgres` | um banco por serviço | [[Postgres]] 18 | — |

- Python 3.14 com [[uv]] (lockfile, `uv sync --locked`); [[Migration\|migrations]] com Alembic, uma pasta por serviço.
- Um pedido do navegador sempre passa pelo Caddy: `/api/notes/*` → `ichiro`, `/api/chat/*` → `lonzo`, `/api/auth/*` → `nujabes`, o resto → front.
- O `lonzo` não toca no banco de notas: lê e escreve pela API HTTP do `ichiro`, como qualquer cliente.

## Por que vários serviços

- Cada um tem dono claro do seu dado (notas, conversas, usuários) e um banco que só ele acessa ([[Isolamento por usuário]]).
- A IA vira mais um cliente da API de notas: o app funciona inteiro sem ela ([[00 Mapa — IA no projeto|IA no projeto]]).
- Custo aceito: mais containers, mais [[CI]], chamada HTTP entre `lonzo` e `ichiro` em vez de uma consulta direta.

## Backend em camadas

Os três serviços Python seguem o mesmo desenho, conferido por lint:

| Camada | Pasta | Faz |
|---|---|---|
| router | `routers/` | recebe o pedido, chama **um** service, devolve |
| service | `services/` | regra do domínio, abre a [[Transação\|transação]], lança erro do domínio (`NoteNotFound`) |
| repository / client | `repositories/`, `clients/` | uma função por consulta SQL; uma classe por API externa, um método por endpoint |
| handlers | `handlers.py` | tabela erro do domínio → status HTTP, num `exception_handler` |

## O front, em poucas linhas

- TypeScript sem framework; o editor é [[CodeMirror]] 6 com live preview (títulos, tabelas e código desenhados; marcas escondidas fora do cursor).
- Árvore de pastas, abas (nota/chat), busca (`Ctrl+O`), links entre notas (`[[` grava `[Título](note:<uuid>)`), temas, modo de leitura.
- Chat lê o [[Server-sent events|SSE]] com `fetch` + `ReadableStream` (o pedido é `POST`, que o `EventSource` não faz); cancelar usa `AbortController`. Resposta em Markdown com KaTeX, limpa por DOMPurify.
- Só online: [[UI otimista]] no navegador; offline fica para o app desktop ([[Navegador]]).

## Números

- ~690 commits, ~180 testes nos três serviços Python, PRs empilhados ([[Desenvolvimento com Claude Code]]).

## Se perguntarem

- **"Por que FastAPI?"** Tipagem com Pydantic, OpenAPI de graça, sync e async no mesmo framework; o `lonzo` precisa de async (stream do modelo), o `ichiro` não.
- **"O que você faria diferente?"** Um gateway que assina o usuário (JWT curto) em vez de confiar no cabeçalho `X-User-Id` dentro da rede ([[Login e gateway]]).
