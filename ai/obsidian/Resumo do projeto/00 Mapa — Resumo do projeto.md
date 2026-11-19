---
tags: [noteproject, arquitetura]
---
# Resumo do projeto — mapa

Visão de como cada parte do NoteProject foi feita, escrita a partir do código de 2026-11-09, para revisar o projeto inteiro de uma vez e responder perguntas de detalhe numa entrevista. Foco em backend, infra e IA; o front aparece só na [[Visão geral do NoteProject|visão geral]]. Cada página termina num "Se perguntarem", com a resposta curta e o trade-off.

![[arquitetura-de-hoje.drawio.svg]]
*Hoje: tudo num [[Docker Compose|compose]]; o [[Reverse proxy|Caddy]] confere a sessão e roteia cada `/api/<prefixo>` para o serviço dono.*

## Páginas

| Página | Ideia |
|---|---|
| [[Visão geral do NoteProject]] | o que é, os quatro serviços, a stack e o front em poucas linhas |
| [[Serviço de notas]] | `ichiro`: árvore de notas no [[Postgres]], CTE recursiva, busca [[Busca full-text no Postgres\|full-text]], camadas |
| [[Isolamento por usuário]] | um banco por serviço, dois [[Usuários do banco\|usuários do banco]] e [[Row-Level Security\|RLS]] com o usuário do pedido |
| [[Login e gateway]] | `nujabes` (senha com bcrypt, token com hash) + [[Forward auth\|forward auth]] do Caddy |
| [[Chat com IA]] | `lonzo`: [[Laço de ferramentas\|laço de ferramentas]] do SDK, [[Server-sent events\|SSE]], histórico no banco |
| [[Ferramentas e contexto da IA]] | as ferramentas de nota, o `.workspace/`, skills, o bloco `<context>` e o [[Cache de prompt\|cache]] |
| [[Chave da API por usuário]] | cada pessoa usa a própria chave da Anthropic, cifrada com Fernet |
| [[Testes, CI e qualidade]] | pytest com banco de verdade, savepoint por teste, mypy strict, um job de [[CI]] por serviço |
| [[Infra hoje e o plano na AWS]] | compose de dev, [[Dockerfile]], Caddy com [[TLS]] local; [[EC2]], [[Terraform]] e [[Backup\|backup]] no plano |
| [[Desenvolvimento com Claude Code]] | o workspace de IA: regras viram lint, hooks, escopo por branch, PRs empilhados |
| [[Perguntas de entrevista]] | perguntas prováveis com resposta dobrada, para treinar |

## Como usar

- Ordem sugerida: visão geral → notas → isolamento → login → chat → ferramentas → infra → perguntas.
- Para aprofundar um conceito, o link leva à página em [[00 Mapa — Conceitos|Conceitos]]; para o porquê de uma decisão, a página em [[00 Mapa — Estrutura do projeto|Estrutura do projeto]] ou [[00 Mapa — IA no projeto|IA no projeto]].
