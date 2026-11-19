---
tags: [noteproject, infra]
---
# Infra hoje e o plano na AWS

Hoje tudo roda no notebook com [[Docker Compose]] (✅). A ida para a AWS é a milestone M3 (⏳): o plano está escrito e as decisões tomadas, mas nada subiu ainda. Detalhe em [[Infra — deploy e operação]].

## O compose de desenvolvimento (✅)

| Peça | Como |
|---|---|
| código | bind mount (`./apps/ichiro:/app`) + `fastapi dev` com reload: salvar o arquivo recarrega o serviço |
| dependências | volume anônimo em `/app/.venv` e `/app/node_modules`: o bind não esconde o que a imagem instalou |
| [[Postgres]] | `postgres:18`, porta só em `127.0.0.1:5432` (testes e psql do host); dados num [[Volume do Docker\|volume]] nomeado |
| bancos | `postgres/init/*.sh` em `/docker-entrypoint-initdb.d`: rodam só com o volume vazio |
| Caddy | portas 80/443 em `127.0.0.1`; `tls internal` = certificado da [[CA]] local do Caddy, guardada no volume `caddy_data` (confiar uma vez) |
| nomes | `notes.localhost`: `*.localhost` resolve para 127.0.0.1 sem `/etc/hosts` |
| rede | serviços se acham pelo nome (`ichiro:8000`) na [[Rede de containers\|rede do compose]]; só o Caddy e o Postgres têm porta no host |
| segredos | `.env` fora do git; cada serviço recebe só as próprias variáveis |

## Dockerfile

```dockerfile
FROM python:3.14-slim
COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project
COPY . .
RUN uv sync --locked
```

- Copiar `pyproject.toml` e `uv.lock` antes do código: mudar código não invalida a camada das dependências ([[Dockerfile]]).
- `--locked`: falha se o lockfile não bate com o `pyproject.toml`, build reproduzível.

## O plano na AWS (⏳)

![[estrutura-infra-aws-ec2.drawio.svg]]
*Uma [[EC2]] com o mesmo compose; [[S3]], [[IAM]] e alarmes em volta.*

| Peça | Escolha | Por quê |
|---|---|---|
| máquina | [[EC2]] `t4g.small` (ARM) | grátis até 31/12/2026 ([[Custo zero — créditos e free tier]]) |
| dentro dela | o mesmo compose, com imagens prontas | dev e prod iguais; sem Kubernetes para 5 containers |
| front | `dist/` do Vite dentro da imagem do Caddy, por [[Build multi-stage\|build multi-stage]] | sem servidor Node em produção |
| [[TLS]] | Caddy com Let's Encrypt | certificado e renovação automáticos |
| [[Domínio]] / [[DNS]] | GitHub Student Pack + Cloudflare | custo zero |
| imagens | GitHub Actions → GHCR ([[CD]]) | a EC2 baixa, não builda |
| entrar na AWS pela CI | [[OIDC]] com role que só aceita a `master` do repo | sem chave de acesso guardada |
| shell | [[SSM Session Manager]] | sem porta 22 aberta |
| firewall | [[Security Group]] só com 443 | |
| infra como código | [[Terraform]] em `infra/` | recriar do zero |
| [[Backup]] | `pg_dump` por cron → [[S3]], restore testado uma vez | backup sem restore testado não conta |
| [[Observabilidade\|monitoramento]] | `/health` + healthcheck + alarme do CloudWatch + AWS Budgets | saber que caiu e quanto custa |

## Se perguntarem

- **"Por que EC2 com compose e não ECS/EKS ou serverless?"** Uma máquina, poucos serviços fixos, custo zero e o objetivo de aprender a operar o servidor. ECS/Fargate e RDS custam por hora e escondem justamente o que se quer aprender ([[AWS ou infra própria]]).
- **"Por que Caddy e não nginx?"** TLS automático nos dois ambientes, `forward_auth` pronto, config curta; nginx precisaria de certbot e de mais configuração.
- **"E escalar?"** Primeiro, Postgres gerenciado e mais réplicas dos serviços sem estado atrás do Caddy; a edição ao vivo pediria [[Redis pub-sub|Redis]] entre réplicas do sync.
