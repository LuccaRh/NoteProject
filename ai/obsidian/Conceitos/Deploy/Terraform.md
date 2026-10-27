---
tags: [noteproject, conceito, infra]
---
# Terraform

Criar a infra clicando no console funciona uma vez. Na segunda, ninguém lembra o que foi clicado, e uma máquina perdida não volta igual.

- **Infra como código**: a infra descrita em arquivos de texto, no git, como o resto do código.
- **Terraform**: lê os arquivos `.tf` (o que deve existir), compara com o que existe e cria, muda ou apaga a diferença.

1. `terraform plan`: mostra o que vai mudar.
2. `terraform apply`: aplica.
3. O *state* guarda o que o Terraform criou, para comparar na próxima vez.

- Recriar o servidor do zero = um `apply`.

> [!example] No NoteProject
> [[EC2]], [[Security Group]], [[IAM]] e [[S3]] em `.tf` ([[Infra — deploy e operação]]).

Doc: [Terraform](https://developer.hashicorp.com/terraform/intro).
