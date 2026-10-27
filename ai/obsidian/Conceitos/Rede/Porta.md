---
tags: [noteproject, conceito, infra]
---
# Porta

O [[Endereço IP|IP]] leva o pedido até a máquina, mas nela rodam muitos programas. A porta diz para qual deles.

- **Porta**: um número de 0 a 65535. Um programa **escuta** numa porta; o sistema entrega a ele tudo o que chega nela. Duas coisas não escutam na mesma porta da mesma máquina (`address already in use`).
- Portas de costume: 80 (HTTP), 443 ([[TLS|HTTPS]] e `wss://`), 22 (SSH), 5432 ([[Postgres]]). Na URL, a porta some quando é a de costume: `https://site.com` = `https://site.com:443`.
- Do lado do cliente, a porta é sorteada pelo sistema (`51234`), e é para ela que a resposta volta ([[TCP]]).

## Endereço de escuta

- `127.0.0.1:8000` só aceita quem está na própria máquina (a rede loopback, [[Rede|rede]] em que só ela está).
- `0.0.0.0:8000` aceita de qualquer rede que chegue nela. `0.0.0.0` não é uma rede nem o mesmo que `localhost`: quer dizer "por todos os IPs que esta máquina tem".
- Dentro de um container, `0.0.0.0` são as interfaces **do container** ([[Rede de containers]]).

## Do nome até o programa

1. [[DNS]]: o nome vira o IP público.
2. O cliente abre uma conexão [[TCP]] com `IP:porta`.
3. Firewall (na nuvem, o [[Security Group]]): a porta está liberada? Se não, a conexão nem chega à máquina.
4. A máquina entrega a conexão ao programa que escuta naquela porta.

> [!warning] Erros comuns
> - Programa escutando em `127.0.0.1` e esperado de fora da máquina (ou de fora do container): ninguém alcança.

Doc: `man 7 ip`, `ss -tln` (portas em escuta).
