---
tags: [noteproject, conceito, infra]
---
# EC2

Um servidor precisa de uma máquina ligada o tempo todo, com IP público, fora do notebook.

- **EC2**: máquina virtual alugada na AWS. Escolhe-se o tipo (CPU, memória) e o sistema; paga-se por hora ligada.
- **Tipo de instância**: família + tamanho. `t4g.small` = 2 vCPU ARM (Graviton) e 2 GB; o `g` indica ARM, mais barato que o x86 do mesmo tamanho.
- **EBS**: o disco da EC2; continua cobrando com a máquina parada.

- Em volta dela: o [[Security Group e SSM|Security Group]] (o que entra), uma role do [[IAM]] (o que ela pode fazer na AWS) e, para arquivos grandes, o [[S3 — armazenamento de objetos|S3]].

> [!example] No NoteProject
> Uma `t4g.small` roda o [[Container e Docker Compose|compose]] de produção ([[Infra — deploy e operação]]).

Doc: [Amazon EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/concepts.html).
