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
- Alguns nomes nem chegam a um servidor de DNS: `localhost` e qualquer `*.localhost` (`notas.localhost`) dão a [[Rede|loopback]] da própria máquina (`127.0.0.1` ou `::1`), sem registro e sem `/etc/hosts`. O nome é reservado para isso ([RFC 6761](https://www.rfc-editor.org/rfc/rfc6761#section-6.3)); no Linux quem responde é o próprio sistema (`getent hosts notas.localhost`), e os navegadores fazem o mesmo sozinhos. Serve para dar nome a sites de desenvolvimento.

> [!example] No NoteProject
> DNS no Cloudflare ([[Infra — deploy e operação]]).

Doc: [MDN — DNS](https://developer.mozilla.org/en-US/docs/Glossary/DNS).
