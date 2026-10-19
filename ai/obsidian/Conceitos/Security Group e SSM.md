---
tags: [noteproject, conceito, infra]
---
# Security Group e SSM

Uma máquina com IP público recebe tentativas de conexão o tempo todo, e cada porta aberta é uma porta a mais para tentar. Ainda assim é preciso entrar nela para operar.

- **Security Group**: o firewall da [[EC2]], do lado de fora dela: a lista do que pode entrar (porta e origem). O resto é barrado antes de chegar à máquina.
- **SSM Session Manager**: abre um shell na [[EC2]] pelo console ou pela CLI da AWS, sem SSH e sem porta 22. O acesso passa pelo [[IAM]] e fica registrado.

Um servidor web típico:

| Porta | Aberta? | Por quê |
|---|---|---|
| 443 | sim | [[TLS e HTTPS\|HTTPS]] do [[Reverse proxy\|reverse proxy]] |
| 22 (SSH) | não | o SSM substitui |
| 5432 ([[Postgres e migrations\|Postgres]]) | não | só os serviços da própria máquina falam com o banco |

> [!example] No NoteProject
> Só a 443 aberta, shell pelo SSM ([[Infra — deploy e operação]]).

Docs: [Security Groups](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html), [Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html).
