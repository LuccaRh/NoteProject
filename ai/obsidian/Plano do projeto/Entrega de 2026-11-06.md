---
tags: [noteproject, plano]
---
# Entrega de 2026-11-06

O [[Roadmap]] deixa a v1 do [[Objetivo do app]] para o fim do M3 e a IA para depois dela. A entrega de 2026-11-06 (sexta) pede antes disso duas coisas: notas `.md` que se criam, editam, salvam, deletam, mudam de pasta e se acham por busca no navegador, e a IA funcionando dentro do app com as ideias do [[Workspace no app]], por um [[Chat com o workspace|chat]] no servidor (mudança de 2026-10-31, no lugar de Ctrl+D e fila). O servidor roda em localhost pelo [[Docker Compose]], sem login, [[TLS]] nem AWS, e a fase v1 do workspace sobe para antes do M2. A data era 2026-10-29; os dias a mais (mudança de 2026-10-27) trazem busca, mover entre pastas, importar o vault e CI do servidor.

## O que entra

| Parte | Entra | Fica para depois |
|---|---|---|
| notas | CRUD completo no [[Postgres]], pastas por `parent_id`, mover entre pastas, salvar sozinho, busca com `tsvector`, importar um vault do Obsidian | campos, views, sidebar de pastas e views |
| site | o [[Reverse proxy\|Caddy]] do compose de dev, com [[TLS]] local, entrega o front (Vite) e a [[API de notas]] na mesma origem ([[Navegador]]); `make check` do servidor no [[CI]] | login, servir o build em produção (#47), AWS |
| IA | [[Chat com o workspace\|chat]] no servidor: serviço `lonzo` com a lib `anthropic` (`tool_runner` para as ferramentas), `.workspace/` com regras e skills como notas, conversas guardadas, ferramentas para ler, buscar, criar e editar notas | [[Edição por âncora\|sugestão por âncora]], [[Fila de pedidos\|fila]] e worker, [[Marcar dúvida\|Ctrl+D]] e chips, scripts em [[Sandbox\|sandbox]], mapa do workspace, agentes, hooks, [[MCP]], classificação de tema, modelo local |

## O que a IA faz

1. O painel de chat, ao lado do editor, manda `POST /api/chat` com o workspace, a conversa e a pergunta; o [[Reverse proxy|Caddy]] encaminha ao `lonzo`.
2. O `lonzo` lê as regras e o índice de skills do `.workspace/` daquele workspace pela [[API de notas]] e monta a [[Chamada a um modelo|chamada ao modelo]], com a chave no `.env` ([[Sem Claude Code — provedores#Harness]]).
3. Quando o modelo pede uma ferramenta (`list_folder`, `read_note`, `search_notes`, `create_note`, `edit_note`, `delete_note`), só dentro da pasta do workspace, o `lonzo` executa pela [[API de notas]] e chama de novo ([[Laço de ferramentas]]).
4. A resposta chega ao painel aos pedaços, e a conversa fica no banco do `lonzo`: recarregar a página ou abrir em outro aparelho mostra a mesma conversa.

Workspace é qualquer pasta com um `.workspace/` dentro, um por assunto; as regras e skills são notas comuns, editáveis no próprio app, e um workspace novo nasce de um texto breve: o `lonzo` preenche um esqueleto fixo, e skills prontas de um catálogo ficam para depois ([[Workspace no app#Como nasce]]). O `lonzo` vem antes dos workspaces (mudança de 2026-11-01): é a parte arriscada, e é ele quem cria o workspace. O passo a passo, lado a lado com o Claude Code, está em [[Caminho de uma pergunta]]. Pelo chat, a IA também altera o workspace ("responde mais curto" muda a regra).

![[chat-workspace.drawio.svg]]
*Uma pergunta: o `lonzo` monta o pacote, chama a Anthropic e, a cada pedido de ferramenta, lê a nota pelo `ichiro`.*

## Sequência das issues

| # | Issue | Nome | O que faz | Milestone | Data |
|---|---|---|---|---|---|
| 0 | [#11](https://github.com/LuccaRh/NoteProject/issues/11) ✅ | Run the server in Docker Compose | a API roda num container do [[Docker Compose\|compose]], com imagem própria ([[Dockerfile]]) e porta só no loopback ([[Endereço IP\|IP]] e [[Porta\|porta]]) | [M0 Server skeleton](https://github.com/LuccaRh/NoteProject/milestone/1) | feita |
| 1 | [#13](https://github.com/LuccaRh/NoteProject/issues/13) ✅ | Keep server secrets in an env file outside git | `.env` fora do git e `.env.example` com as variáveis (senha do [[Postgres]], chave da API do [[Sem Claude Code — provedores\|provedor]] do modelo) | [M0 Server skeleton](https://github.com/LuccaRh/NoteProject/milestone/1) | feita |
| 2 | [#12](https://github.com/LuccaRh/NoteProject/issues/12) ✅ | Add Postgres with migrations to the server | [[Postgres]] no [[Docker Compose\|compose]] e uma [[Migration\|migration]] com `notes` (`parent_id`, `is_folder`), sem `users`, que entra com o login (M2); os dados sobrevivem ao `docker compose down` | [M0 Server skeleton](https://github.com/LuccaRh/NoteProject/milestone/1) | feita |
| 3 | [#46](https://github.com/LuccaRh/NoteProject/issues/46) ✅ | Expose the notes API on the server | rotas `/notes` da [[API de notas]] no [[FastAPI]] (listar, ler, criar, editar, deletar), com testes contra o [[Postgres]] | [M1 Notes in the browser](https://github.com/LuccaRh/NoteProject/milestone/2) | feita |
| 4 | [#62](https://github.com/LuccaRh/NoteProject/issues/62) ✅ | List, create and edit notes in the editor through the API | front novo, do zero: cliente da [[API de notas]] e lista de notas (abrir, criar, renomear, deletar); abre a nota no [[Front — editor e UI\|editor]] e salva sozinho | [M1 Notes in the browser](https://github.com/LuccaRh/NoteProject/milestone/2) | feita |
| 5 | [#16](https://github.com/LuccaRh/NoteProject/issues/16) ✅ | Put Caddy with local TLS in front of the server | [[Reverse proxy\|Caddy]] no [[Docker Compose\|compose]] de dev com [[TLS]] local: `/api/notes` → `ichiro`, o resto → Vite; sai o proxy do Vite e nenhuma porta de API fica exposta | [M1 Notes in the browser](https://github.com/LuccaRh/NoteProject/milestone/2) | feita |
| 6 | [#74](https://github.com/LuccaRh/NoteProject/issues/74) | Answer chat questions through the lonzo service | serviço novo `apps/lonzo`, em [[Container\|container]] próprio, com a lib `anthropic` (Haiku): `POST /api/chat {pergunta}`, regras de um `.md` no `system` (as do `.workspace/` entram com a #73), resposta em SSE com eventos nomeados; um PR do `caddy` com `/api/chat/*` e `/api/notes/*`, sem pega-tudo | [AI in the app](https://github.com/LuccaRh/NoteProject/milestone/9) | 01/11 dom |
| 7 | [#73](https://github.com/LuccaRh/NoteProject/issues/73) | Create a workspace from a short description of its goal | qualquer pasta vira workspace com um `.workspace/` dentro: o `lonzo` preenche um esqueleto (objetivo, como responder, fatos fixos, estado, fontes) a partir de um texto breve, numa chamada só, e grava as notas pela [[API de notas]]; as regras do workspace passam a ir no `system`; vários por pessoa ([[Workspace no app#Como nasce]]); fatia da [#42](https://github.com/LuccaRh/NoteProject/issues/42) | [AI in the app](https://github.com/LuccaRh/NoteProject/milestone/9) | 02/11 seg |
| 8 | [#75](https://github.com/LuccaRh/NoteProject/issues/75) | Keep chat conversations on the server | banco `lonzo` no mesmo [[Postgres]] do compose, com usuário próprio, e a primeira [[Migration\|migration]] do `lonzo`: conversas (cada uma presa a um workspace) e mensagens | [AI in the app](https://github.com/LuccaRh/NoteProject/milestone/9) | 02/11 seg |
| 9 | [#76](https://github.com/LuccaRh/NoteProject/issues/76) | Chat with the AI from the web app | painel de chat ao lado do [[Front — editor e UI\|editor]]: escolha do workspace, lista de conversas, pergunta e resposta chegando aos pedaços | [AI in the app](https://github.com/LuccaRh/NoteProject/milestone/9) | 02/11 seg |
| 10 | [#56](https://github.com/LuccaRh/NoteProject/issues/56) | Search notes with Postgres full-text search | `/search` com `tsvector` e índice GIN no [[Postgres]] (nova [[Migration\|migration]]), e uma caixa de busca no front | [M1 Notes in the browser](https://github.com/LuccaRh/NoteProject/milestone/2) | 03/11 ter |
| 11 | [#77](https://github.com/LuccaRh/NoteProject/issues/77) | Let the chat read and search notes | ferramentas `list_folder`, `read_note` e `search_notes` (usa o `/search` da #56), só dentro da pasta do workspace, pela [[API de notas]] ([[Laço de ferramentas]]) | [AI in the app](https://github.com/LuccaRh/NoteProject/milestone/9) | 03/11 ter |
| 12 | [#78](https://github.com/LuccaRh/NoteProject/issues/78) | Let the chat create, edit and delete notes | ferramentas `create_note`, `edit_note` (trecho velho → novo) e `delete_note`: a IA grava notas e monta o próprio workspace | [AI in the app](https://github.com/LuccaRh/NoteProject/milestone/9) | 04/11 qua |
| 13 | [#51](https://github.com/LuccaRh/NoteProject/issues/51) | Keep host files out of the web build context | `.dockerignore` do web: `node_modules/` e `dist/` do host fora da imagem | [M0 Server skeleton](https://github.com/LuccaRh/NoteProject/milestone/1) | 04/11 qua |
| 14 | [#6](https://github.com/LuccaRh/NoteProject/issues/6) | Move notes between folders, including back to the root | `PATCH` do `parent_id` (inclusive `null`, a raiz), sem deixar uma pasta dentro dela mesma; arrastar na lista de notas | [M1 Notes in the browser](https://github.com/LuccaRh/NoteProject/milestone/2) | 05/11 qui |
| 15 | [#79](https://github.com/LuccaRh/NoteProject/issues/79) | Import an Obsidian vault into the server | script que manda cada `.md` de uma pasta para a [[API de notas]], mantendo as [[Pastas, campos e views\|pastas]]; a entrega roda com as notas de verdade | [M1 Notes in the browser](https://github.com/LuccaRh/NoteProject/milestone/2) | 05/11 qui |
| 16 | [#17](https://github.com/LuccaRh/NoteProject/issues/17) | Run server checks in CI | job do [[CI]] com um Postgres de serviço, rodando ruff, mypy e pytest do `ichiro` a cada PR | [M2 Login and TLS](https://github.com/LuccaRh/NoteProject/milestone/3) | 06/11 sex, se sobrar |

- 30/10 fechou o site com notas atrás do Caddy; 02/11, o chat respondendo com as regras do workspace; 04/11, o chat lendo e editando notas; 05/11, pastas e o vault importado; 06/11 é ensaio.
- `backend` e `infrastructure` são do Lucca; a tela do chat (#76) e a parte de front de #56 e #6 são da sessão, com revisão; na #76, a chamada à API e o streaming são do Lucca (área `cliente-api`).

## Se faltar tempo

Sai nesta ordem: #17, #51, #79 (importar o vault), #78 (o chat só lê notas, sem gravar) e #6. O chat com as regras do workspace (#73–#76) e a leitura de notas (#77) ficam: são a IA da entrega.

## Fora da entrega

#7–#9 (campos, views e sidebar de pastas e views), #47 (o build servido pelo Caddy, na M3), o resto do M2 Login and TLS, M3 Online on AWS, M4 Live edits, #33, #34, #36, #37, #43–#45 e as milestones Desktop app e Mobile app. Da IA: #32 ([[Edição por âncora|sugestão por âncora]]; o chat grava direto até ela existir), #35 (worker da [[Fila de pedidos|fila]]; o chat não usa fila), o resto da #42 e os scripts em [[Sandbox|sandbox]]. #31 e #5 ([[Marcar dúvida]]) ficam sem milestone, para depois ([[Ordem de implementação#Depois, sem data]]). Sem login, o servidor fica só em `127.0.0.1`, e o chat não sai dele: qualquer um que alcançasse o servidor gastaria a chave.

## Risco

Pela regra de [[Roadmap#Duas trilhas|duas trilhas]], `backend` e `infrastructure` são escritos à mão, com o conceito antes. Serviço novo (`lonzo`), banco novo, busca e mover entre pastas à mão é o trecho apertado: schema, migration e rotas ficam à mão, e o esqueleto do `lonzo` e o prompt podem sair gerados e revisados no PR. O plano B virou o plano (2026-11-01): o Agent SDK trazia um binário de 328 MB, e o [[Laço de ferramentas|laço]] fica no `tool_runner` da lib `anthropic` ([[Sem Claude Code — provedores#Harness]]).

mac ipv6 modem firewal