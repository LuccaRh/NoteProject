---
tags: [noteproject, conceito, infra]
---
# IP, porta e rede de containers

Um pedido pela rede precisa dizer duas coisas: **qual máquina** e **qual programa dentro dela**. A máquina é o IP; o programa é a porta.

## IP e porta

- **IP**: o endereço da máquina. Público (`203.0.113.7`) a internet alcança; privado (`172.18.0.3`) só quem está na mesma rede.
- **Porta**: um número de 0 a 65535. Um programa **escuta** numa porta; o sistema entrega a ele tudo o que chega nela. Duas coisas não escutam na mesma porta da mesma máquina.
- **Endereço de escuta**: `127.0.0.1:8000` só aceita quem está na própria máquina; `0.0.0.0:8000` aceita de qualquer rede que chegue nela.
- Portas de costume: 80 (HTTP), 443 ([[TLS e HTTPS|HTTPS]] e `wss://`), 22 (SSH), 5432 ([[Postgres e migrations|Postgres]]). Na URL, a porta some quando é a de costume: `https://site.com` = `https://site.com:443`.

## Do nome até o programa

1. [[DNS e domínio|DNS]]: o nome vira o IP público.
2. O cliente abre uma conexão TCP com `IP:porta`.
3. Firewall (na nuvem, o [[Security Group e SSM|Security Group]]): a porta está liberada? Se não, a conexão nem chega à máquina.
4. A máquina entrega a conexão ao programa que escuta naquela porta.

## Rede de containers

Cada [[Container e Docker Compose|container]] é como uma máquina pequena: tem IP privado próprio e suas portas.

- O [[Container e Docker Compose|compose]] cria uma **rede** e põe todos os serviços do arquivo nela. Lá dentro, o **nome do serviço** é o endereço: `http://api:8000` acha o container `api` (o Docker tem um DNS interno).
- **Porta publicada** (`ports: ["443:443"]`): liga a porta da máquina à do container. `host:container`. Só o que é publicado é alcançável de fora da máquina.
- Serviço sem `ports` continua falando com os vizinhos pela rede do compose; só não recebe nada de fora.

| Quem chama | Alcança | Como |
|---|---|---|
| internet | só porta publicada **e** liberada no firewall | `IP público:443` |
| um container | outro da mesma rede, qualquer porta em que ele escute | `nome-do-serviço:porta` |
| a própria máquina | porta publicada | `localhost:443` |

> [!warning] Erros comuns
> - Programa escutando em `127.0.0.1` dentro do container: os vizinhos não alcançam. Dentro de container, escutar em `0.0.0.0`.
> - `localhost` dentro de um container é o próprio container, não a máquina nem o vizinho.
> - Publicar a porta do banco "para testar" abre o banco para quem passar pelo firewall.

> [!example] No NoteProject
> Só o reverse proxy publica porta; api, sync e banco ficam na rede do compose ([[Rede do servidor]]).

Docs: [Networking in Compose](https://docs.docker.com/compose/how-tos/networking/), [Docker — published ports](https://docs.docker.com/engine/network/#published-ports).
