---
tags: [noteproject, infra]
---
# Infra — deploy e operação

Enquanto tudo roda no notebook, infra é só o [[Container e Docker Compose|`docker compose`]] de desenvolvimento. Quando o servidor existir (M0–M2), ele precisa de um endereço na internet, [[TLS e HTTPS|HTTPS]], deploy, [[Backup e restore|backup]] e alguém avisando quando cai.

## O que existe (✅)

| Arquivo | Faz |
|---|---|
| `docker-compose-dev.yml` | `web` (Vite :5173) e `notes` (FastAPI :8000), com reload; sobe com `-f` |
| `apps/web/Dockerfile.dev`, `apps/notes/Dockerfile.dev` | imagens de desenvolvimento, com reload |
| `Makefile` | `make dev` sem [[Container e Docker Compose\|Docker]]; `make check` |
| `.github/workflows/ci.yml` | tsc + build do web; testes de `ai/tools/`; ruff, mypy e pytest entram com o servidor (#17) |

A ideia de partida: um [[Container e Docker Compose|compose]] com FastAPI, sync, [[Postgres e migrations|Postgres]], armazenamento de objetos e reverse proxy numa máquina só, que para uso pessoal custa pouco. O plano usa uma [[EC2]] e o [[S3 — armazenamento de objetos|S3]] ([[AWS ou infra própria]]); [[TLS e HTTPS|TLS]], domínio, [[Backup e restore|backup]] e [[Observabilidade|monitoramento]] entram abaixo.

## O que falta (⏳)

![[estrutura-infra-aws-ec2.drawio.svg]]
*Plano de produção: uma [[EC2]] com o mesmo [[Container e Docker Compose|compose]]; [[S3 — armazenamento de objetos|S3]], [[IAM]] e alarme de custo da AWS em volta.*

| Peça | Para quê | No plano |
|---|---|---|
| domínio + [[DNS e domínio\|DNS]] | um nome fixo para os dispositivos acharem o servidor | domínio do GitHub pack + Cloudflare |
| [[Reverse proxy\|reverse proxy]] + [[TLS e HTTPS\|TLS]] | só a porta 443 aberta, [[TLS e HTTPS\|HTTPS]], roteia `/api` e `/sync` | [[Reverse proxy\|Caddy]] |
| máquina | onde os [[Container e Docker Compose\|containers]] rodam | [[EC2]] `t4g.small` |
| [[Container e Docker Compose\|compose]] de produção | sem bind de código, `restart: unless-stopped`, healthcheck | api, sync, [[Postgres e migrations\|Postgres]], [[Reverse proxy\|Caddy]] |
| imagens + registry | o servidor baixa a imagem pronta em vez de buildar | [[CI e CD\|GitHub Actions → GHCR]] |
| segredos | senha do [[Postgres e migrations\|Postgres]] e chaves fora do git | `.env` fora do git; [[IAM]] no lugar de chave |
| [[Backup e restore\|backup]] | [[Backup e restore\|`pg_dump`]] + blobs fora da máquina, com [[Backup e restore\|restore]] testado | cron → [[S3 — armazenamento de objetos\|S3]] |
| [[Observabilidade\|monitoramento]] | saber que caiu antes de abrir o app no celular | healthcheck + alarme do [[Observabilidade\|CloudWatch]] |
| firewall e acesso | só 443 aberta; shell sem porta 22 | [[Security Group e SSM\|Security Group + SSM]] |
| criar a infra | recriar o servidor do zero | [[Terraform — infra como código\|Terraform]] |

### Detalhes do plano

- [[Container e Docker Compose|Compose]] de produção: o mesmo jeito do de desenvolvimento, com imagens prontas do [[CI e CD|GHCR]] em vez de código montado.
- [[EC2]] `t4g.small`, grátis até 31/12/2026 ([[Custo zero — créditos e free tier]]).
- [[Reverse proxy|Caddy]] na frente de api e sync (#16 e #22 do [[Roadmap]]); portas e caminho de um pedido na [[Rede do servidor|rede do servidor]].
- [[TLS e HTTPS|Certificado]]: no PC (M1), local, emitido pelo Caddy; na AWS (M2), Let's Encrypt, pedido pelo Caddy.
- [[DNS e domínio|Domínio]] (#21): GitHub Student Pack, DNS no Cloudflare.
- [[CI e CD|CI]]: hoje o `ci.yml`; CI do servidor (#17) e deploy por merge (#23), entrando na AWS por [[OIDC]] com uma role que só aceita a `master` deste repo.
- [[Terraform — infra como código|Terraform]] (#19): [[EC2]], Security Group, [[IAM]] e [[S3 — armazenamento de objetos|S3]], na pasta `infra/` ([[Um repo ou vários]]).
- [[Backup e restore|Backup]] (#24): `pg_dump` por cron → [[S3 — armazenamento de objetos|S3]]; a M2 só fecha depois de um restore feito uma vez.
- [[Observabilidade]]: `/health` (#10) + `healthcheck` no compose; alarme do CloudWatch por e-mail (#25); AWS Budgets para custo.

### Por que Caddy

Critério: uma máquina, serviços fixos (api, sync), [[TLS e HTTPS|HTTPS]] no PC e na AWS sem passo à parte, custo zero. Opções lado a lado em [[Reverse proxy]].

- **Caddy**: o certificado sai sozinho nos dois lugares (CA local no PC, Let's Encrypt na [[EC2]]); o `/sync` por [[WebSocket]] passa sem config extra; o `Caddyfile` cabe em poucas linhas.
- nginx faria o mesmo com certbot e os cabeçalhos de `Upgrade` à mão; Traefik compensa com muitos containers dinâmicos, o que o [[Container e Docker Compose|compose]] daqui não tem; ALB cobra por hora para uma máquina só.

Revisar se: o servidor passar a mais de uma máquina (vira ALB + ACM, passo 15 da [[Trilha de infra]]) ou o número de serviços crescer a ponto de as rotas mudarem toda semana.

| Quem ([[IAM]]) | Como | Pode |
|---|---|---|
| a [[EC2]] | role da instância | gravar no [[S3 — armazenamento de objetos\|S3]]; abrir sessão pelo [[Security Group e SSM\|SSM]] |
| o [[CI e CD\|GitHub Actions]] | role assumida por [[OIDC]] | fazer o deploy |

| Porta ([[Security Group e SSM\|Security Group]]) | Aberta? | Por quê |
|---|---|---|
| 443 | sim | [[TLS e HTTPS\|HTTPS]] do [[Reverse proxy\|Caddy]] |
| 22 (SSH) | não | o [[Security Group e SSM\|SSM]] substitui |
| 5432 ([[Postgres e migrations\|Postgres]]) | não | só os [[Container e Docker Compose\|containers]] falam com ele |

- Por que uma [[EC2]] e o que é da AWS e o que é na mão: [[AWS ou infra própria]].
- A ordem de aprender cada peça: [[Trilha de infra]].
