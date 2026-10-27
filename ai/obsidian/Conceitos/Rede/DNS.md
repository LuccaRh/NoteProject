---
tags: [noteproject, conceito, infra]
---
# DNS

Os clientes precisam achar o servidor. O endereço da máquina é um [[Endereço IP|IP]], difícil de lembrar e que muda quando a máquina é recriada; o cliente guarda um [[Domínio|domínio]], e alguém precisa traduzi-lo.

- **DNS**: o sistema que traduz nome em IP. Um registro `A` diz "este nome → este IP".

1. O cliente pergunta ao DNS o IP de `notas.exemplo.me`.
2. Recebe o IP do servidor e conecta.
3. Recriar a máquina = trocar o registro; os clientes não mudam nada.

- Cada máquina pergunta ao DNS escrito no `/etc/resolv.conf`; dentro de um container do compose, é o DNS do Docker, que conhece os nomes dos serviços ([[Rede de containers]]).

> [!example] No NoteProject
> DNS no Cloudflare ([[Infra — deploy e operação]]).

Doc: [MDN — DNS](https://developer.mozilla.org/en-US/docs/Glossary/DNS).
