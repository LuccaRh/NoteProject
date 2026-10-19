---
tags: [noteproject, conceito, infra]
---
# IAM

Na AWS, tudo é chamada de API: criar máquina, gravar no [[S3 — armazenamento de objetos|S3]]. Cada chamada precisa dizer quem é e se pode.

- **IAM** (*Identity and Access Management*): quem existe na conta e o que cada um pode fazer.
- **Usuário**: uma pessoa, com senha e MFA. O root (dono da conta) fica fora do dia a dia.
- **Role**: papel que um serviço **assume** para receber credenciais temporárias; nada de chave fixa guardada.
- **Policy**: JSON que diz o que é permitido (`s3:PutObject` neste bucket).

| Quem | Como recebe a role |
|---|---|
| uma [[EC2]] | *instance profile*: a role vem com a máquina |
| um workflow do [[CI e CD\|GitHub Actions]] | troca um token por [[OIDC]] |

- Regra: o mínimo de permissão que funciona.

> [!example] No NoteProject
> A EC2 grava no S3 e o deploy entra pelo OIDC, cada um com sua role ([[Infra — deploy e operação]]).

Doc: [IAM](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html).
