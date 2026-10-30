---
tags: [noteproject, plano]
---
# Entrega de 2026-11-06

O [[Roadmap]] deixa a v1 do [[Objetivo do app]] para o fim do M3 e a IA para depois dela. A entrega de 2026-11-06 (sexta) pede antes disso duas coisas: notas `.md` que se criam, editam, salvam, deletam, mudam de pasta e se acham por busca no navegador, e a IA funcionando dentro do app com as ideias do [[Workspace no app]]. O servidor roda em localhost pelo [[Docker Compose]], sem login, [[TLS]] nem AWS, e a fase v1 do workspace sobe para antes do M2. A data era 2026-10-29; os dias a mais (mudança de 2026-10-27) trazem busca, mover entre pastas, importar o vault e CI do servidor.

## O que entra

| Parte | Entra | Fica para depois |
|---|---|---|
| notas | CRUD completo no [[Postgres]], pastas por `parent_id`, mover entre pastas, salvar sozinho, busca com `tsvector`, importar um vault do Obsidian | campos, views, sidebar de pastas e views |
| site | o [[Reverse proxy\|Caddy]] do compose de dev, com [[TLS]] local, entrega o front (Vite) e a [[API de notas]] na mesma origem ([[Navegador]]); `make check` do servidor no [[CI]] | login, servir o build em produção (#47), AWS |
| IA | [[Marcar dúvida\|Ctrl+D]], [[Fila de pedidos\|fila]], worker, `.workspace/` com regras e skills, [[Edição por âncora\|sugestão por âncora]] | mapa do workspace, agentes, scripts e hooks, [[MCP]], classificação de tema, modelo local |

## O que a IA faz

1. Selecionar um trecho e apertar `Ctrl+D` cria um pedido `pendente` na tabela `pedidos`; o editor mostra um chip no lugar.
2. `Responder` (um pedido) ou `Responder todas` (a nota inteira) põe os pedidos na fila.
3. O worker (`apps/worker`, container próprio) pega o pedido no Postgres e monta o contexto: as regras de `.workspace/regras/`, a skill escolhida em `.workspace/skills/` (ex.: `explicar`, `resumir`), a seção da nota em volta do trecho e a pergunta.
4. Uma chamada só à API da Anthropic, com a chave no `.env` ([[Sem Claude Code — provedores]]). A resposta volta em JSON como operação presa a um trecho: `{anchor, op, text}`.
5. O pedido vira `sugerida` e o editor mostra o texto proposto; `Tab` aplica, `Esc` volta o pedido para `pendente`.

O `.workspace/` são notas comuns, editáveis no próprio app, e começa com um kit "Estudo" (uma regra de como responder e duas skills). Cada pedido guarda quais regras e skill usou.

## Sequência das issues

| # | Issue | Nome | O que faz | Milestone | Data |
|---|---|---|---|---|---|
| 0 | [#11](https://github.com/LuccaRh/NoteProject/issues/11) ✅ | Run the server in Docker Compose | a API roda num container do [[Docker Compose\|compose]], com imagem própria ([[Dockerfile]]) e porta só no loopback ([[Endereço IP\|IP]] e [[Porta\|porta]]) | [M0 Server skeleton](https://github.com/LuccaRh/NoteProject/milestone/1) | feita |
| 1 | [#13](https://github.com/LuccaRh/NoteProject/issues/13) ✅ | Keep server secrets in an env file outside git | `.env` fora do git e `.env.example` com as variáveis (senha do [[Postgres]], chave da API do [[Sem Claude Code — provedores\|provedor]] do modelo) | [M0 Server skeleton](https://github.com/LuccaRh/NoteProject/milestone/1) | feita |
| 2 | [#12](https://github.com/LuccaRh/NoteProject/issues/12) ✅ | Add Postgres with migrations to the server | [[Postgres]] no [[Docker Compose\|compose]] e uma [[Migration\|migration]] com `notes` (`parent_id`, `is_folder`), sem `users`, que entra com o login (M2); os dados sobrevivem ao `docker compose down` | [M0 Server skeleton](https://github.com/LuccaRh/NoteProject/milestone/1) | feita |
| 3 | [#46](https://github.com/LuccaRh/NoteProject/issues/46) ✅ | Expose the notes API on the server | rotas `/notes` da [[API de notas]] no [[FastAPI]] (listar, ler, criar, editar, deletar), com testes contra o [[Postgres]] | [M1 Notes in the browser](https://github.com/LuccaRh/NoteProject/milestone/2) | feita |
| 4 | [#62](https://github.com/LuccaRh/NoteProject/issues/62) | List, create and edit notes in the editor through the API | front novo, do zero: cliente da [[API de notas]] e lista de notas (abrir, criar, renomear, deletar), pelo proxy do Vite; abre a nota no [[Front — editor e UI\|editor]] e salva sozinho | [M1 Notes in the browser](https://github.com/LuccaRh/NoteProject/milestone/2) | 28/10 qua |
| 5 | [#16](https://github.com/LuccaRh/NoteProject/issues/16) | Put Caddy with local TLS in front of the server | [[Reverse proxy\|Caddy]] no [[Docker Compose\|compose]] de dev com [[TLS]] local: `/api/notes` → `notes`, o resto → Vite; sai o proxy do Vite e nenhuma porta de API fica exposta | [M1 Notes in the browser](https://github.com/LuccaRh/NoteProject/milestone/2) | 29/10 qui |
| 6 | [#31](https://github.com/LuccaRh/NoteProject/issues/31) | Queue a question from the editor with Ctrl+D | `Ctrl+D` [[Marcar dúvida\|marca a dúvida]], grava o pedido na [[Fila de pedidos\|fila]] (`pedidos`, criada numa [[Migration\|migration]] desta issue) e o editor o mostra com uma [[CodeMirror\|decoração]] | [Editor](https://github.com/LuccaRh/NoteProject/milestone/5) | 30/10 sex |
| 7 | [#5](https://github.com/LuccaRh/NoteProject/issues/5) | Show chips for duvida and fix markers in the editor | chips ([[CodeMirror\|decorações]]) no lugar de `[!duvida]` e `[!fix]`, com o estado do pedido ([[Marcador no texto, conteúdo fora\|marcador no texto, conteúdo fora]]) | [Editor](https://github.com/LuccaRh/NoteProject/milestone/5) | 30/10 sex |
| 8 | [#35](https://github.com/LuccaRh/NoteProject/issues/35) | Process the request queue with a worker | `apps/worker`, em [[Container\|container]] próprio, lê a [[Fila de pedidos\|fila]], monta o contexto, chama o modelo ([[Sem Claude Code — provedores\|provedor]]) e grava a resposta como sugestão | [AI in the app](https://github.com/LuccaRh/NoteProject/milestone/9) | 31/10 sáb |
| 9 | [#42](https://github.com/LuccaRh/NoteProject/issues/42) | Organize agent workspaces in the app | só a fase v1 do [[Workspace no app\|workspace]]: `.workspace/regras/` e `.workspace/skills/` como notas, kit "Estudo", o worker lê dali | [AI in the app](https://github.com/LuccaRh/NoteProject/milestone/9) | 01/11 dom |
| 10 | [#32](https://github.com/LuccaRh/NoteProject/issues/32) | Apply edits by anchor with Tab and Esc | a operação [[Edição por âncora\|presa à âncora]] aparece como sugestão no editor; `Tab` aplica, `Esc` descarta | [Editor](https://github.com/LuccaRh/NoteProject/milestone/5) | 02/11 seg |
| 11 | nova | Answer queued requests from the editor | botões `Responder` e `Responder todas`, escolha da skill do [[Workspace no app\|workspace]] e estado do pedido na [[Fila de pedidos\|fila]] (pendente → fila → sugerida) | [AI in the app](https://github.com/LuccaRh/NoteProject/milestone/9) | 03/11 ter |
| 12 | [#56](https://github.com/LuccaRh/NoteProject/issues/56) | Search notes with Postgres full-text search | `/search` com `tsvector` e índice GIN no [[Postgres]] (nova [[Migration\|migration]]), e uma caixa de busca no front | [M1 Notes in the browser](https://github.com/LuccaRh/NoteProject/milestone/2) | 04/11 qua |
| 13 | [#51](https://github.com/LuccaRh/NoteProject/issues/51) | Keep host files out of the web build context | `.dockerignore` do web: `node_modules/` e `dist/` do host fora da imagem | [M0 Server skeleton](https://github.com/LuccaRh/NoteProject/milestone/1) | 04/11 qua |
| 14 | [#6](https://github.com/LuccaRh/NoteProject/issues/6) | Move notes between folders, including back to the root | `PATCH` do `parent_id` (inclusive `null`, a raiz), sem deixar uma pasta dentro dela mesma; arrastar na lista de notas | [M1 Notes in the browser](https://github.com/LuccaRh/NoteProject/milestone/2) | 05/11 qui |
| 15 | nova | Import an Obsidian vault into the server | script que manda cada `.md` de uma pasta para a [[API de notas]], mantendo as [[Pastas, campos e views\|pastas]]; a entrega roda com as notas de verdade | [M1 Notes in the browser](https://github.com/LuccaRh/NoteProject/milestone/2) | 05/11 qui |
| 16 | [#17](https://github.com/LuccaRh/NoteProject/issues/17) | Run server checks in CI | job do [[CI]] com um Postgres de serviço, rodando ruff, mypy e pytest do `notes` a cada PR | [M2 Login and TLS](https://github.com/LuccaRh/NoteProject/milestone/3) | 06/11 sex, se sobrar |

- 29/10 fecha o site com notas; 03/11, a IA respondendo; 05/11, busca, pastas e o vault importado; 06/11 é ensaio.
- `backend` e `infrastructure` são do Lucca; #62, #5, #32 e a parte de front de #56 e #6 são da sessão, com revisão.

## Se faltar tempo

Sai nesta ordem: #17, #51, a importação do vault, #6. Da IA, a #32 é a primeira: o worker escreve a resposta como callout `> [!resposta]` logo abaixo da dúvida, e `Tab`/`Esc` ficam para depois da entrega. O resto do desenho continua igual: contexto montado pelo workspace e uma chamada só, sem a IA procurar nada.

## Fora da entrega

#7–#9 (campos, views e sidebar de pastas e views), #47 (o build servido pelo Caddy, na M3), o resto do M2 Login and TLS, M3 Online on AWS, M4 Live edits, #33, #34, #36, #37, #43–#45 e as milestones Desktop app e Mobile app. Sem login, o servidor fica só em `127.0.0.1`.

## Risco

Pela regra de [[Roadmap#Duas trilhas|duas trilhas]], `backend` e `infrastructure` são escritos à mão, com o conceito antes. Worker, busca e mover entre pastas à mão é o trecho apertado: schema, migration e rotas ficam à mão, e o esqueleto do worker e o prompt podem sair gerados e revisados no PR.

mac ipv6 modem firewal