---
tags: [noteproject, conceito, infra]
---
# SSM Session Manager

Para operar um servidor é preciso um shell nele, mas abrir a porta 22 (SSH) é mais uma porta exposta e mais uma chave para guardar.

- **SSM Session Manager**: abre um shell na [[EC2]] pelo console ou pela CLI da AWS, sem SSH e sem porta 22. O acesso passa pelo [[IAM]] e fica registrado.
- Com ele, o [[Security Group]] fecha a 22.

> [!example] No NoteProject
> Shell pelo SSM ([[Infra — deploy e operação]]).

Doc: [Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html).
