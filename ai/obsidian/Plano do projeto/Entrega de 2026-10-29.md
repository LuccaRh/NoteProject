---
tags: [noteproject, plano]
---
# Entrega de 2026-10-29

O [[Roadmap]] deixa a v1 do [[Objetivo do app]] para o fim do M3 e a IA para depois dela. A entrega de 2026-10-29 pede antes disso duas coisas: notas `.md` que se criam, editam, salvam e deletam no navegador, e a IA funcionando dentro do app com as ideias do [[Workspace no app]]. Para caber em 8 dias, o servidor roda em localhost pelo [[Container e Docker Compose|Docker Compose]], sem login, [[TLS e HTTPS|TLS]] nem AWS, e a fase v1 do workspace sobe para antes do M2.

## O que entra

| Parte | Entra | Fica para depois |
|---|---|---|
| notas | CRUD completo no [[Postgres e migrations\|Postgres]], pastas por `parent_id`, salvar sozinho | campos, views, busca com `tsvector` (agora `ILIKE`) |
| site | o [[FastAPI]] serve o build do front e a [[API de notas]] na mesma origem ([[Navegador]]) | login, Caddy, AWS |
| IA | [[Marcar dúvida\|Ctrl+D]], [[Fila de pedidos\|fila]], worker, `.workspace/` com regras e skills, [[Edição por âncora\|sugestão por âncora]] | mapa do workspace, agentes, scripts e hooks, [[MCP]], classificação de tema, modelo local |

## O que a IA faz

1. Selecionar um trecho e apertar `Ctrl+D` cria um pedido `pendente` na tabela `pedidos`; o editor mostra um chip no lugar.
2. `Responder` (um pedido) ou `Responder todas` (a nota inteira) põe os pedidos na fila.
3. O worker (`apps/worker`, container próprio) pega o pedido no Postgres e monta o contexto: as regras de `.workspace/regras/`, a skill escolhida em `.workspace/skills/` (ex.: `explicar`, `resumir`), a seção da nota em volta do trecho e a pergunta.
4. Uma chamada só à API da Anthropic, com a chave no `.env` ([[Sem Claude Code — provedores]]). A resposta volta em JSON como operação presa a um trecho: `{anchor, op, text}`.
5. O pedido vira `sugerida` e o editor mostra o texto proposto; `Tab` aplica, `Esc` volta o pedido para `pendente`.

O `.workspace/` são notas comuns, editáveis no próprio app, e começa com um kit "Estudo" (uma regra de como responder e duas skills). Cada pedido guarda quais regras e skill usou.

## Sequência das issues

| # | Issue | Nome | O que faz | Milestone | Dia |
|---|---|---|---|---|---|
| 0 | [#11](https://github.com/LuccaRh/NoteProject/issues/11) ✅ | Run the server in Docker Compose | fechada; a API roda num container do [[Container e Docker Compose\|compose]], com imagem própria ([[Dockerfile e camadas\|Dockerfile]]) e porta só no loopback ([[IP, porta e rede de containers\|IP e porta]]); PR [#52](https://github.com/LuccaRh/NoteProject/issues/52) mergeado | [M0 Server skeleton](https://github.com/LuccaRh/NoteProject/milestone/1) | 1 |
| 1 | [#13](https://github.com/LuccaRh/NoteProject/issues/13) | Keep server secrets in an env file outside git | `.env` fora do git e `.env.example` com as variáveis (senha do [[Postgres e migrations\|Postgres]], chave da API do [[Sem Claude Code — provedores\|provedor]] do modelo) | [M0 Server skeleton](https://github.com/LuccaRh/NoteProject/milestone/1) | 1 |
| 2 | [#12](https://github.com/LuccaRh/NoteProject/issues/12) | Add Postgres with migrations to the server | [[Postgres e migrations\|Postgres]] no [[Container e Docker Compose\|compose]] e uma [[Migrations com Alembic\|migration]] com `notes` (`parent_id`, `is_folder`), sem `users`, que entra com o login (M2); os dados sobrevivem ao `docker compose down` | [M0 Server skeleton](https://github.com/LuccaRh/NoteProject/milestone/1) | 1 |
| 3 | [#46](https://github.com/LuccaRh/NoteProject/issues/46) | Expose the notes API on the server | rotas `/notes` da [[API de notas]] no [[FastAPI]] (listar, ler, criar, editar, deletar) e `/search` com `ILIKE`, com testes contra o [[Postgres e migrations\|Postgres]] | [M1 Notes in the browser](https://github.com/LuccaRh/NoteProject/milestone/2) | 2–3 |
| 4 | nova | Bring back the sidebar to list, create, rename and delete notes | volta o cliente da [[API de notas]] e a sidebar da tag `backup-before-drop-sidebar`; abre a nota no [[Front — editor e UI\|editor]] e salva sozinho | [M1 Notes in the browser](https://github.com/LuccaRh/NoteProject/milestone/2) | 3 |
| 5 | [#47](https://github.com/LuccaRh/NoteProject/issues/47) | Serve the web build from the server | o [[FastAPI]] serve `apps/web/dist`; `localhost:8000` abre o site no [[Navegador\|navegador]] | [M1 Notes in the browser](https://github.com/LuccaRh/NoteProject/milestone/2) | 4 |
| 6 | [#31](https://github.com/LuccaRh/NoteProject/issues/31) | Queue a question from the editor with Ctrl+D | `Ctrl+D` [[Marcar dúvida\|marca a dúvida]], grava o pedido na [[Fila de pedidos\|fila]] (`pedidos`, criada numa [[Migrations com Alembic\|migration]] desta issue) e o editor o mostra com uma [[CodeMirror e decorações\|decoração]] | [Editor](https://github.com/LuccaRh/NoteProject/milestone/5) | 5 |
| 7 | [#5](https://github.com/LuccaRh/NoteProject/issues/5) | Show chips for duvida and fix markers in the editor | chips ([[CodeMirror e decorações\|decorações]]) no lugar de `[!duvida]` e `[!fix]`, com o estado do pedido ([[Marcador no texto, conteúdo fora\|marcador no texto, conteúdo fora]]) | [Editor](https://github.com/LuccaRh/NoteProject/milestone/5) | 5 |
| 8 | [#35](https://github.com/LuccaRh/NoteProject/issues/35) | Process the request queue with a worker | `apps/worker`, em [[Container e Docker Compose\|container]] próprio, lê a [[Fila de pedidos\|fila]], monta o contexto, chama o modelo ([[Sem Claude Code — provedores\|provedor]]) e grava a resposta como sugestão | [AI in the app](https://github.com/LuccaRh/NoteProject/milestone/9) | 6 |
| 9 | [#42](https://github.com/LuccaRh/NoteProject/issues/42) | Organize agent workspaces in the app | só a fase v1 do [[Workspace no app\|workspace]]: `.workspace/regras/` e `.workspace/skills/` como notas, kit "Estudo", o worker lê dali | [AI in the app](https://github.com/LuccaRh/NoteProject/milestone/9) | 6 |
| 10 | [#32](https://github.com/LuccaRh/NoteProject/issues/32) | Apply edits by anchor with Tab and Esc | a operação [[Edição por âncora\|presa à âncora]] aparece como sugestão no editor; `Tab` aplica, `Esc` descarta | [Editor](https://github.com/LuccaRh/NoteProject/milestone/5) | 7 |
| 11 | nova | Answer queued requests from the editor | botões `Responder` e `Responder todas`, escolha da skill do [[Workspace no app\|workspace]] e estado do pedido na [[Fila de pedidos\|fila]] (pendente → fila → sugerida) | [AI in the app](https://github.com/LuccaRh/NoteProject/milestone/9) | 7 |
| 12 | nova (opcional) | Import an Obsidian vault into the server | script que manda cada `.md` de uma pasta para a [[API de notas]], mantendo as [[Pastas, campos e views\|pastas]] | [M1 Notes in the browser](https://github.com/LuccaRh/NoteProject/milestone/2) | 8 |

- Dia 4 fecha o site com notas; dia 6, a IA respondendo; dia 8 é folga e ensaio.
- A #51 (`.dockerignore` do web, M0) é pequena e entra se sobrar tempo.

## Se faltar tempo

A #32 é a primeira a sair: o worker escreve a resposta como callout `> [!resposta]` logo abaixo da dúvida, e `Tab`/`Esc` ficam para depois da entrega. O resto do desenho continua igual: contexto montado pelo workspace e uma chamada só, sem a IA procurar nada.

## Fora da entrega

#6–#9 (pastas, campos e views), M2 Login and TLS, M3 Online on AWS, M4 Live edits, #33, #34, #36, #37, #43–#45 e as milestones Desktop app e Mobile app. Sem login, o servidor fica só em `127.0.0.1`.

## Risco

Pela regra de [[Roadmap#Duas trilhas|duas trilhas]], `backend` e `infrastructure` são escritos à mão, com o conceito antes. Em 8 dias, Postgres, rotas e worker à mão é o trecho apertado: schema, migration e rotas ficam à mão, e o esqueleto do worker e o prompt podem sair gerados e revisados no PR.

mac ipv6 modem firewall