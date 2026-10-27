---
tags: [noteproject, conceito, infra]
---
# Security Group

Uma máquina com IP público recebe tentativas de conexão o tempo todo, e cada [[Porta|porta]] aberta é uma porta a mais para tentar.

- **Security Group**: o firewall da [[EC2]], do lado de fora dela: a lista do que pode entrar (porta e origem). O resto é barrado antes de chegar à máquina.

Um servidor web típico:

| Porta | Aberta? | Por quê |
|---|---|---|
| 443 | sim | [[TLS\|HTTPS]] do [[Reverse proxy\|reverse proxy]] |
| 22 (SSH) | não | o [[SSM Session Manager]] substitui |
| 5432 ([[Postgres]]) | não | só os serviços da própria máquina falam com o banco |

> [!example] No NoteProject
> Só a 443 aberta ([[Infra — deploy e operação]]).

Doc: [Security Groups](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html).
