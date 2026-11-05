---
tags: [noteproject, conceito, auth]
---
# Sessão de login

Depois de conferir a senha uma vez, o servidor precisa reconhecer a mesma pessoa nos pedidos seguintes sem pedir a senha de novo. A sessão é o registro, no servidor, de que um login aconteceu; o cliente guarda só um token que aponta para esse registro.

1. O login confere a senha ([[Hash de senha]]).
2. O servidor sorteia um token longo e aleatório e grava uma linha: hash do token, usuário, validade.
3. O cliente recebe o token, no navegador normalmente num [[Cookie|cookie]].
4. A cada pedido, o servidor calcula o hash do token recebido e procura a linha. Achou e está na validade: o pedido é daquele usuário.
5. Logout apaga a linha; o token deixa de valer na hora.

- O token não carrega informação: é um número sorteado, como a ficha de um guarda-volumes. O id do usuário fica no servidor.
- Como o token é aleatório e grande, adivinhar é inviável, e um hash rápido (SHA-256) basta para guardá-lo. Senha pede um hash lento, porque é fraca por natureza.
- Guardar só o hash do token protege contra vazamento do banco: quem lê a tabela não consegue se passar pelo usuário.

## Token e linha da tabela

São duas coisas, em dois lugares, ligadas pelo hash:

| | Token | Linha da sessão |
|---|---|---|
| Onde fica | com o cliente, no [[Cookie\|cookie]] | na tabela do servidor |
| O que contém | só o número sorteado | hash do token, usuário, validade |

```
token ── sha256 ──> hash ── procura na tabela ──> linha ──> usuário
```

O hash do token serve de chave de busca: ele não se desfaz nem se traduz, e o usuário vem de outra coluna da linha encontrada. O token nasce do sorteio, sem relação com a senha, o email ou o id.

Depois do login, o token é a única prova pedida: quem o tiver passa pelo usuário até a validade acabar ou o logout apagar a linha. Por isso o [[Cookie|cookie]] que o guarda leva `HttpOnly` e `Secure`.

## Sessão ou JWT

| | Sessão no servidor | Token assinado (JWT) |
|---|---|---|
| Onde mora o estado | numa tabela | dentro do próprio token |
| Custo por pedido | uma consulta | conferir a assinatura |
| Encerrar antes da validade | apaga a linha | difícil, o token segue válido |

> [!example] Um uso
> O serviço `nujabes` guarda as sessões do [[Login no navegador]].
