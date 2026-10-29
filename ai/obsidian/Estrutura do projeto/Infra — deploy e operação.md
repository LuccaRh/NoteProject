---
tags: [noteproject, infra]
---
# Infra — deploy e operação

Enquanto tudo roda no notebook, infra é só o [[Docker Compose|`docker compose`]] de desenvolvimento. Quando o servidor existir (M0–M2), ele precisa de um endereço na internet, [[TLS|HTTPS]], deploy, [[Backup|backup]] e alguém avisando quando cai.

## O que existe (✅)

| Arquivo | Faz |
|---|---|
| `docker-compose-dev.yml` | `web` (Vite :5173) e `notes` (FastAPI :8000), com reload; sobe com `-f` |
| `apps/web/Dockerfile.dev`, `apps/notes/Dockerfile.dev` | imagens de desenvolvimento, com reload |
| `Makefile` | `make dev` sem [[Container\|Docker]]; `make check` |
| `.github/workflows/ci.yml` | tsc + build do web; testes de `ai/tools/`; ruff, mypy e pytest entram com o servidor (#17) |

Os serviços do compose de desenvolvimento são programas separados, cada um na sua [[Porta|porta]]. O front é só o `web`; a "api" é o `notes`, o back.

| Serviço | Pasta | Porta | Faz |
|---|---|---|---|
| `web` | `apps/web/` | 5173 | entrega o HTML e o JS do editor ao navegador; repassa `/api` ao `notes` ([[Proxy de desenvolvimento\|proxy de desenvolvimento]]) |
| `notes` | `apps/notes/` | 8000 | a api: rotas `/notes` em [[FastAPI]], lê e grava no [[Postgres]] |
| `postgres` | — | 5432 | o banco |

A ideia de partida: um [[Docker Compose|compose]] com FastAPI, sync, [[Postgres]], armazenamento de objetos e reverse proxy numa máquina só, que para uso pessoal custa pouco. O plano usa uma [[EC2]] e o [[S3]] ([[AWS ou infra própria]]); [[TLS]], domínio, [[Backup|backup]] e [[Observabilidade|monitoramento]] entram abaixo.

## O que falta (⏳)

![[estrutura-infra-aws-ec2.drawio.svg]]
*Plano de produção: uma [[EC2]] com o mesmo [[Docker Compose|compose]]; [[S3]], [[IAM]] e alarme de custo da AWS em volta.*

| Peça | Para quê | No plano |
|---|---|---|
| domínio + [[DNS]] | um nome fixo para os dispositivos acharem o servidor | domínio do GitHub pack + Cloudflare |
| [[Reverse proxy\|reverse proxy]] + [[TLS]] | só a porta 443 aberta, [[TLS\|HTTPS]], roteia `/api` e `/sync` | [[Reverse proxy\|Caddy]] |
| máquina | onde os [[Container\|containers]] rodam | [[EC2]] `t4g.small` |
| [[Docker Compose\|compose]] de produção | sem bind de código, `restart: unless-stopped`, healthcheck | api, sync, [[Postgres]], [[Reverse proxy\|Caddy]] |
| imagens + registry | o servidor baixa a imagem pronta em vez de buildar | [[CI\|GitHub Actions]] → [[CD\|GHCR]] |
| segredos | senha do [[Postgres]] e chaves fora do git | `.env` fora do git; [[IAM]] no lugar de chave |
| [[Backup\|backup]] | [[Backup\|`pg_dump`]] + blobs fora da máquina, com [[Backup\|restore]] testado | cron → [[S3]] |
| [[Observabilidade\|monitoramento]] | saber que caiu antes de abrir o app no celular | healthcheck + alarme do [[Observabilidade\|CloudWatch]] |
| firewall e acesso | só 443 aberta; shell sem porta 22 | [[Security Group]] + [[SSM Session Manager\|SSM]] |
| criar a infra | recriar o servidor do zero | [[Terraform]] |

### Detalhes do plano

- [[Docker Compose|Compose]] de produção: o mesmo jeito do de desenvolvimento, com imagens prontas do [[CD|GHCR]] em vez de código montado.
- [[EC2]] `t4g.small`, grátis até 31/12/2026 ([[Custo zero — créditos e free tier]]).
- [[Reverse proxy|Caddy]] na frente de api e sync (#16 e #22 do [[Roadmap]]); portas e caminho de um pedido na [[Rede do servidor|rede do servidor]].
- [[TLS|Certificado]]: no PC (M1), local, emitido pelo Caddy; na AWS (M2), Let's Encrypt, pedido pelo Caddy.
- [[Domínio]] (#21): GitHub Student Pack, DNS no Cloudflare.
- [[CI]]: hoje o `ci.yml`; CI do servidor (#17) e deploy por merge (#23), entrando na AWS por [[OIDC]] com uma role que só aceita a `master` deste repo.
- [[Terraform]] (#19): [[EC2]], Security Group, [[IAM]] e [[S3]], na pasta `infra/` ([[Um repo ou vários]]).
- [[Backup]] (#24): `pg_dump` por cron → [[S3]]; a M2 só fecha depois de um restore feito uma vez.
- [[Observabilidade]]: `/health` (#10) + `healthcheck` no compose; alarme do CloudWatch por e-mail (#25); AWS Budgets para custo.

### Por que Caddy

Critério: uma máquina, serviços fixos (api, sync), [[TLS|HTTPS]] no PC e na AWS sem passo à parte, custo zero. Opções lado a lado em [[Reverse proxy]].

- **Caddy**: o certificado sai sozinho nos dois lugares (CA local no PC, Let's Encrypt na [[EC2]]); o `/sync` por [[WebSocket]] passa sem config extra; o `Caddyfile` cabe em poucas linhas.
- nginx faria o mesmo com certbot e os cabeçalhos de `Upgrade` à mão; Traefik compensa com muitos containers dinâmicos, o que o [[Docker Compose|compose]] daqui não tem; ALB cobra por hora para uma máquina só.

Revisar se: o servidor passar a mais de uma máquina (vira ALB + ACM, passo 15 da [[Trilha de infra]]) ou o número de serviços crescer a ponto de as rotas mudarem toda semana.

| Quem ([[IAM]]) | Como | Pode |
|---|---|---|
| a [[EC2]] | role da instância | gravar no [[S3]]; abrir sessão pelo [[SSM Session Manager\|SSM]] |
| o [[CI\|GitHub Actions]] | role assumida por [[OIDC]] | fazer o deploy |

| Porta ([[Security Group]]) | Aberta? | Por quê |
|---|---|---|
| 443 | sim | [[TLS\|HTTPS]] do [[Reverse proxy\|Caddy]] |
| 22 (SSH) | não | o [[SSM Session Manager\|SSM]] substitui |
| 5432 ([[Postgres]]) | não | só os [[Container\|containers]] falam com ele |

- Por que uma [[EC2]] e o que é da AWS e o que é na mão: [[AWS ou infra própria]].
- A ordem de aprender cada peça: [[Trilha de infra]].
