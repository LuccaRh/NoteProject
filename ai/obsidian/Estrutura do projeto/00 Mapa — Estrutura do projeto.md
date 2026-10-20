---
tags: [noteproject, arquitetura]
---
# Estrutura do projeto — mapa

O app em três partes (front, back, infra), marcando o que já existe no código (✅) e o que é plano (⏳).

![[estrutura-completa.drawio.svg]]
*Front, back e infra no plano ([[EC2]] + [[Container e Docker Compose|compose]], [[S3 — armazenamento de objetos|S3]]); hoje só existe o editor web.*

- [[Navegador]] (primeiro): fala direto com o servidor, só online, com [[UI otimista]].
- App desktop (depois): o editor e a IA ([[MCP]]) só falam com o [[O daemon notesd|`notesd`]]; quem sai para a rede é ele.
- App do celular (por último).
- [[EC2]]: o que sobe na mão com [[Container e Docker Compose|`docker compose`]] ([[Reverse proxy|Caddy]], api, sync, [[Postgres e migrations|Postgres]], [[Backup e restore|backup]]). [[Redis pub-sub|Redis]] só com 2+ syncs.
- Em volta: o que a AWS fornece ([[S3 — armazenamento de objetos|S3]], [[IAM]], [[Security Group e SSM|SSM]], [[Observabilidade|CloudWatch]], [[Security Group e SSM|Security Group]], Budgets) e a entrega (Actions → [[CI e CD|GHCR]], [[Terraform — infra como código|Terraform]]).

## As três partes

| Página                        | Ideia                                                                         |
| ----------------------------- | ----------------------------------------------------------------------------- |
| [[Front — editor e UI]]       | [[CodeMirror e decorações\|CodeMirror 6]] no navegador; `notes/api.ts` (⏳) será a única porta para a rede  |
| [[Back — daemon e servidor]]  | o servidor guarda e sincroniza; no app desktop, o [[O daemon notesd\|`notesd`]] é dono do [[SQLite e FTS5\|SQLite]] do dispositivo |
| [[Infra — deploy e operação]] | o que precisa existir para o servidor rodar fora do notebook                  |
| [[Rede do servidor]] | as duas URLs, as portas e o caminho de um pedido até o sync dentro da EC2 |

## Peças

| Página | Ideia |
|---|---|
| [[API de notas]] | o serviço `notes` em [[FastAPI]]: rotas, etapas e o esqueleto da #10 |
| [[O daemon notesd]] | desenho do [[Daemon\|daemon]] do app desktop: camadas, rotas, busca |
| [[Pastas, campos e views]] | organizar = escolher onde criar a nota |
| [[Marcador no texto, conteúdo fora]] | o texto guarda um marcador curto; o pesado mora fora |

## Decisão

| Página | Ideia |
|---|---|
| [[AWS ou infra própria]] | AWS por fora ([[EC2]], [[S3 — armazenamento de objetos\|S3]], [[IAM]], [[Terraform — infra como código\|Terraform]]), [[Container e Docker Compose\|compose]] por dentro ([[Container e Docker Compose\|compose]], [[Reverse proxy\|Caddy]], [[Backup e restore\|backup]]) |
| [[Navegador]] | no navegador, o servidor serve o app e as notas (só online, [[UI otimista]]); offline fica no desktop |
| [[Custo zero — créditos e free tier]] | créditos da AWS + [[EC2]] grátis até dez/2026 + domínio do GitHub pack |
| [[Trilha de infra]] | os conceitos de infra na ordem em que o projeto pede cada um |

## Ordem

- Ordem e milestones no [[Roadmap]]: navegador → app desktop → celular; hoje, M0.
- O que é cada peça (SQLite, Yjs, Caddy, EC2...): [[00 Mapa — Conceitos|Conceitos]].
