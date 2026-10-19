---
tags: [noteproject, conceito, infra]
---
# DNS e domínio

Os clientes precisam achar o servidor. O endereço da máquina é um IP, difícil de lembrar e que muda quando a máquina é recriada.

- **Domínio**: um nome registrado (`notas.exemplo.me`), alugado por ano num registrador.
- **DNS**: o sistema que traduz nome em IP. Um registro `A` diz "este nome → este IP".

1. O cliente pergunta ao DNS o IP de `notas.exemplo.me`.
2. Recebe o IP do servidor e conecta.
3. Recriar a máquina = trocar o registro; os clientes não mudam nada.

- O nome é o que o [[TLS e HTTPS|certificado]] protege.

> [!example] No NoteProject
> Domínio do GitHub Student Pack, DNS no Cloudflare ([[Infra — deploy e operação]]).

Doc: [MDN — DNS](https://developer.mozilla.org/en-US/docs/Glossary/DNS).
