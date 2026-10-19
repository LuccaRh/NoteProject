---
tags: [noteproject, conceito, infra]
---
# Observabilidade

Um servidor que cai de madrugada só é notado quando alguém abre o app e nada funciona.

Observabilidade é o servidor contar como está antes de alguém perguntar.

| Peça | Responde | Exemplo |
|---|---|---|
| healthcheck | o serviço responde? | rota `/health` + `healthcheck` no [[Container e Docker Compose\|compose]] |
| logs | o que aconteceu? | saída dos [[Container e Docker Compose\|containers]] |
| alarme | alguém precisa saber agora? | CloudWatch avisando por e-mail |
| alarme de custo | a conta está subindo? | AWS Budgets |

- Healthcheck que falha deixa o [[Container e Docker Compose|container]] marcado `unhealthy`; o alarme é o que avisa alguém.

> [!example] No NoteProject
> O servidor começa com `/health` (#10); os alarmes vêm em M3 ([[Infra — deploy e operação]]).

Docs: [healthcheck do compose](https://docs.docker.com/reference/compose-file/services/#healthcheck), [alarme do CloudWatch](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html).
