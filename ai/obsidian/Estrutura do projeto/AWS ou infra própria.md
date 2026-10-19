---
tags: [noteproject, infra, decisao]
---
# AWS ou infra própria

O servidor (M0–M4) precisa rodar fora do notebook. Há três jeitos: subir [[Container e Docker Compose|containers]] numa máquina e cuidar de tudo, alugar cada peça pronta da AWS, ou misturar os dois.

## Decidido (2026-10-15): AWS por fora, compose por dentro

A AWS fornece **a máquina, o disco, o storage, as permissões e o alarme de custo**. Dentro da máquina, os serviços sobem **na mão** com [[Container e Docker Compose|`docker compose`]].

![[estrutura-infra-aws-ec2.drawio.svg]]
*Caixa cinza = feito na mão; caixa roxa = serviços da AWS, criados por [[Terraform — infra como código|Terraform]].*

| Peça | Na mão | AWS | Por quê |
|---|---|---|---|
| máquina | — | **[[EC2]]** `t4g.small` (ARM) | grátis até 31/12/2026; depois os créditos cobrem |
| disco do banco | — | **[[EC2\|EBS]]** (o disco da [[EC2]]) | vem junto com a [[EC2]] |
| sistema e [[Container e Docker Compose\|containers]] | **Linux + [[Container e Docker Compose\|`docker compose`]]** | — | é a base de qualquer servidor com [[Container e Docker Compose\|containers]] |
| proxy + [[TLS e HTTPS\|HTTPS]] | **[[Reverse proxy\|Caddy]]** com [[TLS e HTTPS\|Let's Encrypt]] | — | o ALB custa ~US$16/mês e não ensina [[TLS e HTTPS\|TLS]] |
| api e sync | **[[Container e Docker Compose\|containers]]** no [[Container e Docker Compose\|compose]] | — | — |
| [[Postgres e migrations\|Postgres]] | **[[Container e Docker Compose\|container]]** com volume no [[EC2\|EBS]] | (RDS depois) | o RDS cobra por hora; trocar depois muda só a URL |
| anexos e snapshots | — | **[[S3 — armazenamento de objetos\|S3]]** (no lugar do MinIO) | centavos por GB; API que todo lugar usa |
| [[Backup e restore\|backup]] | **script [[Backup e restore\|`pg_dump`]] + cron** | destino: **[[S3 — armazenamento de objetos\|S3]]** | [[Backup e restore\|backup]] fora da máquina |
| firewall | — | **[[Security Group e SSM\|Security Group]]** (só 443) | substitui o fail2ban/firewall da máquina |
| acesso ao servidor | — | **[[Security Group e SSM\|SSM Session Manager]]** | entra no shell sem abrir a porta 22 |
| permissões | — | **[[IAM]]**: [[EC2]] escreve no [[S3 — armazenamento de objetos\|S3]]; GitHub faz deploy | sem chave fixa guardada |
| deploy | **[[CI e CD\|GitHub Actions]]** (build → [[CI e CD\|GHCR]]) | entra na AWS por **[[OIDC]]** | jeito recomendado hoje |
| criar tudo isso | — | **[[Terraform — infra como código\|Terraform]]** | infra como código: apaga e recria com um comando |
| custo | — | **AWS Budgets** com alarme | ganha US$20 de crédito ao criar |
| [[DNS e domínio\|DNS]] | **Cloudflare** (grátis) | (Route 53: US$0,50/mês) | — |

- Na mão fica o básico de operar um servidor: Linux, [[Container e Docker Compose|compose]], proxy, [[TLS e HTTPS|TLS]], [[Backup e restore|backup]].
- Na AWS fica o que as empresas e as vagas usam: [[EC2]], [[S3 — armazenamento de objetos|S3]], [[IAM]], [[Terraform — infra como código|Terraform]], [[OIDC]].
- Custo e créditos estão em [[Custo zero — créditos e free tier]].

## Opções comparadas

| | A. VPS + [[Container e Docker Compose\|compose]] (Hetzner) | **B. [[EC2]] + [[Container e Docker Compose\|compose]] (escolhida)** | C. AWS gerenciada (ECS, RDS, ALB) |
|---|---|---|---|
| aprende Linux, proxy, [[TLS e HTTPS\|TLS]] | sim | sim | pouco (a AWS esconde) |
| aprende AWS | não | [[EC2]], [[S3 — armazenamento de objetos\|S3]], [[IAM]], [[Terraform — infra como código\|Terraform]], [[OIDC]] | tudo, mas caro |
| tempo até subir | curto | médio ([[IAM]] e [[Terraform — infra como código\|Terraform]] no começo) | longo |
| custo no 1º ano | ~€4–6/mês | **~US$0** com créditos | ~US$50+/mês |
| custo depois | ~€4–6/mês | ~US$10–18/mês | ~US$50+/mês |

![[estrutura-infra-aws-gerenciada.drawio.svg]]
*Opção C: é o que empresas maiores usam e o caminho para crescer: cada caixa na mão de B vira uma destas.*

## O que fica fora, e por quê

- **App Runner**: fechado para clientes novos desde 30/04/2026; a AWS indica o **ECS Express Mode** no lugar ([docs AWS](https://docs.aws.amazon.com/ja_jp/apprunner/latest/dg/apprunner-availability-change.html)).
- **Lightsail** (US$5/mês com IPv4, 3 meses grátis): mais barato que a [[EC2]] depois dos créditos, mas tem VPC e [[IAM]] simplificados, que são o que se quer aprender. Fica como plano B de custo ([preços](https://aws.amazon.com/lightsail/pricing)).
- **Kubernetes (EKS)**: 82% de quem usa [[Container e Docker Compose|containers]] roda Kubernetes em produção ([CNCF, jan/2026](https://www.cncf.io/announcements/2026/01/20/kubernetes-established-as-the-de-facto-operating-system-for-ai-as-production-use-hits-82-in-2025-cncf-annual-cloud-native-survey/)), mas o EKS cobra pelo control plane e é demais para um servidor. Conceito para depois.

## Revisar se...

- os créditos acabarem e a conta passar de ~US$15/mês → Lightsail ou Hetzner com o mesmo [[Container e Docker Compose|compose]];
- o [[Backup e restore|backup]] ou o [[Postgres e migrations|Postgres]] der trabalho demais → RDS;
- precisar de mais de uma instância de sync → ALB + ECS (opção C) e [[Redis pub-sub|Redis]].

Fontes consultadas em 2026-10-15; preços e créditos estão em [[Custo zero — créditos e free tier]].
