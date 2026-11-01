---
tags: [noteproject, arquitetura]
---
# Estrutura do projeto — mapa

O app em três partes (front, back, infra), marcando o que já existe no código (✅) e o que é plano (⏳).

![[estrutura-completa.drawio.svg]]
*Front, back e infra no plano ([[EC2]] + [[Docker Compose|compose]], [[S3]]); hoje só existe o editor web.*

- [[Navegador]] (primeiro): fala direto com o servidor, só online, com [[UI otimista]].
- App desktop (depois): o editor e a IA ([[MCP]]) só falam com o [[O daemon notesd|`notesd`]]; quem sai para a rede é ele.
- App do celular (por último).
- [[EC2]]: o que sobe na mão com [[Docker Compose|`docker compose`]] ([[Reverse proxy|Caddy]], api, sync, [[Postgres]], [[Backup|backup]]). [[Redis pub-sub|Redis]] só com 2+ syncs.
- Em volta: o que a AWS fornece ([[S3]], [[IAM]], [[SSM Session Manager|SSM]], [[Observabilidade|CloudWatch]], [[Security Group]], Budgets) e a entrega (Actions → [[CD|GHCR]], [[Terraform]]).

## As três partes

| Página                        | Ideia                                                                         |
| ----------------------------- | ----------------------------------------------------------------------------- |
| [[Front — editor e UI]]       | [[CodeMirror\|CodeMirror 6]] no navegador; `notes/api.ts` (⏳) será a única porta para a rede  |
| [[Back — daemon e servidor]]  | o servidor guarda e sincroniza; no app desktop, o [[O daemon notesd\|`notesd`]] é dono do [[SQLite]] do dispositivo |
| [[Infra — deploy e operação]] | o que precisa existir para o servidor rodar fora do notebook                  |
| [[Rede do servidor]] | as duas URLs, as portas e o caminho de um pedido até o sync dentro da EC2 |

## Peças

| Página | Ideia |
|---|---|
| [[Como ler o front]] | a ordem para ler `apps/chimchar/`, do formato da nota até a tela |
| [[API de notas]] | o serviço `ichiro` em [[FastAPI]]: rotas, etapas e o esqueleto da #10 |
| [[O daemon notesd]] | desenho do [[Daemon\|daemon]] do app desktop: camadas, rotas, busca |
| [[Pastas, campos e views]] | organizar = escolher onde criar a nota |
| [[Comandos do Docker no dev]] | o alias `dc` e os comandos de subir, apagar, psql e migrations |
| [[Marcador no texto, conteúdo fora]] | o texto guarda um marcador curto; o pesado mora fora |

## Decisão

| Página | Ideia |
|---|---|
| [[AWS ou infra própria]] | AWS por fora ([[EC2]], [[S3]], [[IAM]], [[Terraform]]), [[Docker Compose\|compose]] por dentro ([[Docker Compose\|compose]], [[Reverse proxy\|Caddy]], [[Backup\|backup]]) |
| [[Navegador]] | no navegador, o servidor serve o app e as notas (só online, [[UI otimista]]); offline fica no desktop |
| [[Custo zero — créditos e free tier]] | créditos da AWS + [[EC2]] grátis até dez/2026 + domínio do GitHub pack |
| [[Trilha de infra]] | os conceitos de infra na ordem em que o projeto pede cada um |

## Ordem

- Ordem e milestones no [[Roadmap]]: navegador → app desktop → celular; hoje, M0.
- O que é cada peça (SQLite, Yjs, Caddy, EC2...): [[00 Mapa — Conceitos|Conceitos]].
