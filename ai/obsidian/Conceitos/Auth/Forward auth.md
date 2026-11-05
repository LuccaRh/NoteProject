---
tags: [noteproject, conceito, auth, infra]
---
# Forward auth

Com vários serviços atrás de um [[Reverse proxy|reverse proxy]], cada um precisaria saber ler a credencial do usuário. No forward auth, o proxy faz essa checagem antes: pergunta a um serviço de autenticação se o pedido pode passar, e só então repassa.

1. O pedido chega ao proxy.
2. O proxy manda um pedido à parte ao serviço de autenticação, com os cabeçalhos do pedido original (entre eles o `Cookie`).
3. Resposta de erro (401): o proxy a devolve ao cliente, e o serviço de destino nem fica sabendo do pedido.
4. Resposta 2xx: o pedido original segue, com os cabeçalhos que o proxy copiar da resposta.

- O serviço de destino recebe a identidade pronta num cabeçalho e não precisa conhecer cookie nem [[Sessão de login|sessão]].
- A confiança nesse cabeçalho depende de duas coisas: o proxy apagar o valor que veio do cliente, e o serviço só ser alcançável pelo proxy.
- Cada pedido ganha um salto de rede a mais até o serviço de autenticação.

## O cabeçalho de identidade

O cabeçalho com o id do usuário nasce na resposta do serviço de autenticação, a cada pedido, e dura só aquele pedido. O cliente não recebe esse cabeçalho no login nem o guarda; o que fica com ele é o [[Cookie|cookie]], e a identidade é recalculada a partir dele toda vez.

| | Cookie | Cabeçalho de identidade |
|---|---|---|
| Quem cria | serviço de autenticação, no login | serviço de autenticação, a cada checagem |
| Onde vive | guardado no navegador | só no trajeto até o serviço de destino |
| O que tem | token da [[Sessão de login\|sessão]] | id do usuário |
| Duração | vários pedidos | um pedido |

Um cliente normal nunca manda esse cabeçalho. Só que qualquer cliente pode escrever o cabeçalho que quiser, e um atacante com sessão válida poderia pedir como outro usuário:

```bash
curl -H "X-User-Id: <id de outra pessoa>" -b "session=..." https://site/api/notes
```

Por isso o proxy apaga o valor que chegou antes de escrever o verdadeiro. Na resposta 2xx, o `copy_headers` do Caddy (2.11, visto com `caddy adapt`) vira dois passos no pedido original:

```
1. delete X-User-Id                     apaga o que veio do cliente
2. set    X-User-Id = valor da resposta só se o valor não for vazio
```

Só os cabeçalhos listados são copiados, e numa resposta de erro nada disso roda.

> [!example] Um uso
> No [[Login no navegador]], o Caddy pergunta ao `nujabes` com a diretiva `forward_auth`.
