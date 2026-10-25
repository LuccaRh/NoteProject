---
tags: [noteproject, infra, plano]
---
# Trilha de infra

As peças de [[Infra — deploy e operação]] em ordem: cada uma é pedida pela anterior. A coluna "Onde" diz se a peça é montada na mão ou é serviço da AWS ([[AWS ou infra própria]]). Cada linha vira um `/aprender` antes do código e uma issue das milestones M1 e M2 do [[Roadmap]].

## Fase 1 — no PC, custo zero

| # | Conceito | Onde | Ver também |
|---|---|---|---|
| 1 | [[Container e Docker Compose\|containers e compose]] de produção | na mão | — |
| 2 | [[Postgres e migrations\|Postgres em container + migrations]] | na mão | — |
| 3 | [[Reverse proxy\|reverse proxy]] + [[TLS e HTTPS\|TLS]] ([[Reverse proxy\|Caddy]], certificado local) | na mão | — |
| 4 | [[Token por dispositivo\|autenticação por token]] | código | — |
| 5 | segredos fora do git (`.env`) | na mão | — |

## Fase 2 — na AWS, com créditos

| # | Conceito | Onde | Ver também |
|---|---|---|---|
| 6 | conta AWS: plano Free, Budget, [[IAM\|usuário sem root]] | AWS | [[Custo zero — créditos e free tier]] |
| 7 | [[Terraform — infra como código\|Terraform]]: [[EC2]] + [[Security Group e SSM\|Security Group]] + [[IAM]] + [[S3 — armazenamento de objetos\|S3]] | AWS | — |
| 8 | Linux no servidor: [[Security Group e SSM\|SSM]], usuário, [[Container e Docker Compose\|Docker]] | na mão | — |
| 9 | domínio + [[DNS e domínio\|DNS]] apontando para a [[EC2]] | Cloudflare | — |
| 10 | [[TLS e HTTPS\|Let's Encrypt]] de verdade + [[WebSocket]] atrás do proxy | na mão | — |
| 11 | [[CI e CD\|CI/CD]]: imagem no [[CI e CD\|GHCR]], deploy por [[OIDC]] | GitHub + AWS | — |
| 12 | [[Backup e restore\|backup]] `pg_dump` → [[S3 — armazenamento de objetos\|S3]] e restore testado | na mão + AWS | — |
| 13 | [[Observabilidade\|observabilidade]]: healthcheck, logs, alarme | na mão + AWS | — |

## Fase 3 — trocar peças da mão por gerenciadas (opcional)

| # | Troca | O que se aprende |
|---|---|---|
| 14 | [[Postgres e migrations\|Postgres]] [[Container e Docker Compose\|container]] → RDS | o que o banco gerenciado faz por você ([[Backup e restore\|backup]], patch) |
| 15 | [[Reverse proxy\|Caddy]] → ALB + ACM | balanceador e certificado gerenciado |
| 16 | [[Container e Docker Compose\|compose]] → ECS Express Mode | orquestrador de [[Container e Docker Compose\|containers]] |

- Cada troca da fase 3 custa por hora: só com motivo (ver "Revisar se..." da decisão).
- [[Redis pub-sub|Redis]], várias instâncias e Kubernetes ficam fora: são para quando houver mais de uma máquina ou de uma instância de sync. Várias pessoas usando o app numa [[EC2]] só não pedem nenhum deles.
- O conceito de cada linha tem página em [[00 Mapa — Conceitos|Conceitos]].
