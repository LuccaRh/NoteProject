---
tags: [noteproject, infra]
---
# Custo zero — créditos e free tier

Para o servidor de [[AWS ou infra própria]] sair de graça no primeiro ano, juntam-se os créditos da AWS, um teste grátis da [[EC2]] e o que é gratuito no GitHub.

## AWS

| O quê | Quanto | Fonte |
|---|---|---|
| crédito de conta nova (desde 15/07/2025) | US$100 na criação + até US$100 por 5 tarefas de US$20 | [AWS News Blog](https://aws.amazon.com/blogs/aws/aws-free-tier-update-new-customers-can-get-started-and-explore-aws-with-up-to-200-in-credits) |
| tarefas que dão crédito | lançar [[EC2]], criar RDS, criar Lambda, usar Bedrock, **criar um Budget** | idem |
| validade | 12 meses a partir da criação da conta | idem |
| [[EC2]] `t4g.small` | 750 h/mês grátis até **31/12/2026** (o disco [[EC2\|EBS]] é cobrado à parte) | [Classmethod](https://dev.classmethod.jp/en/articles/ec2-t4g-small-free-tier-2026/) |
| sempre grátis | Lambda 1M req/mês, DynamoDB 25 GB, SQS/SNS 1M req, CloudFront 1 TB | [Rackspace](https://spot.rackspace.com/blog/aws-free-tier), [infratally](https://infratally.com/articles/aws-free-tier-2026/) |
| AWS Educate | crédito de US$35 (US$100 se a faculdade for membro) + laboratórios | [nachonacho](https://blog.nachonacho.com/best/aws-credits-promo-codes/) *(site de promoção; conferir)* |

### Plano Free × plano Paid

| | Free | Paid |
|---|---|---|
| pode gerar cobrança | não | sim, o que passar do crédito |
| fecha a conta | em 6 meses ou quando o crédito acaba | não |
| créditos | valem 12 meses | os mesmos; passar de Free para Paid **mantém** o saldo |

- **Abrir no Free** (não tem como gerar cobrança), criar o Budget e passar para o Paid antes de completar 6 meses.

### Quanto custa sem crédito (us-east-1)

| Item | US$/mês | Fonte |
|---|---|---|
| [[EC2]] `t4g.small` (2 GB) | ~12,26 | [Holori](https://calculator.holori.com/aws/ec2/t4g.small/us-east-1) |
| [[EC2]] `t4g.micro` (1 GB) | ~6,13 | [Holori](https://calculator.holori.com/aws/ec2/t4g.micro/us-east-1) |
| IPv4 público | ~3,65 (US$0,005/h) | [Classmethod](https://dev.classmethod.jp/en/articles/ec2-t4g-small-free-tier-2026/) |
| [[EC2\|EBS]] 20 GB gp3 | ~1,60 *(de memória)* | — |
| [[S3]] | US$0,023/GB; bucket vazio não custa nada | [Upstash](https://upstash.com/blog/aws-s3-pricing-explained-2026) |
| **total** | **~US$10–18** | — |

- Com a `t4g.small` grátis até dezembro, os ~US$200 cobrem o resto dos 12 meses.

> [!warning] O que gera fatura sem aviso
> NAT Gateway, ALB, RDS e IPv4 sobrando cobram **por hora**, mesmo parados. Uma [[EC2]] parada também continua pagando o [[EC2|EBS]] e o IPv4. O alarme do Budget avisa, mas **não desliga** nada.

## GitHub (aluno da UNICAMP)

| Benefício | Serve? | Fonte |
|---|---|---|
| domínio grátis por 1 ano (Namecheap `.me`, Name.com, `.tech`) | **sim**: dá o nome do servidor; depois paga preço cheio | [devhunt](https://devhunt.org/blog/github-student-pack-essentials) |
| Azure US$100 | não: o plano é AWS | idem |
| DigitalOcean US$200 | **acabou** em 31/07/2026 | [Capital & Compute](https://capitalandcompute.net/blog/github-student-developer-pack-2026/) |
| crédito AWS | não está no pack | [devhunt](https://devhunt.org/blog/github-student-pack-essentials) |
| Copilot Student | inscrições novas pausadas desde 20/04/2026 | [perkstack](https://perkstack.co/blog/github-student-pack-guide) |
| [[CI\|GitHub Actions]] + [[CD\|GHCR]] | grátis em repositório público, com cota em privado *(de memória)* | — |

- Domínio: o grátis do pack serve no primeiro ano. Para algo que dure, `.com.br` no registro.br sai por ~R$40/ano *(de memória)*.
- A lista do pack muda: conferir em [education.github.com/pack](https://education.github.com/pack).

Pesquisado em 2026-10-15. Quase tudo vem de blogs, não da AWS; confirmar no console de billing.
