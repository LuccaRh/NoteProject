---
tags: [noteproject, conceito, infra]
---
# IP, porta e rede de containers

Um pedido pela rede precisa dizer duas coisas: **qual máquina** e **qual programa dentro dela**. A máquina é o IP; o programa é a porta.

## IP e porta

- **IP**: o endereço da máquina. Público (`203.0.113.7`) a internet alcança; privado (`172.18.0.3`) só quem está na mesma rede.
- **Porta**: um número de 0 a 65535. Um programa **escuta** numa porta; o sistema entrega a ele tudo o que chega nela. Duas coisas não escutam na mesma porta da mesma máquina.
- **Endereço de escuta**: `127.0.0.1:8000` só aceita quem está na própria máquina; `0.0.0.0:8000` aceita de qualquer rede que chegue nela. `0.0.0.0` não é uma rede nem o mesmo que `localhost`: quer dizer "por todos os IPs que esta máquina tem".
- Portas de costume: 80 (HTTP), 443 ([[TLS e HTTPS|HTTPS]] e `wss://`), 22 (SSH), 5432 ([[Postgres e migrations|Postgres]]). Na URL, a porta some quando é a de costume: `https://site.com` = `https://site.com:443`.

## Redes: uma máquina em várias

- **Rede**: grupo de máquinas que falam direto entre si, com IPs da mesma faixa (o wi-fi de casa: `192.168.0.x`).
- Uma máquina está em várias redes, com um IP em cada: o notebook é `127.0.0.1`, `192.168.0.223` e `172.18.0.1` ao mesmo tempo (`ip -4 -br addr`).
- **Loopback** (`127.x`, nome `localhost`): a rede em que só está a própria máquina; nada sai pelo cabo ou wi-fi. Cada máquina tem a sua, e cada container também.
- **Ligar duas redes**: uma máquina que está nas duas repassa o pedido. O roteador liga o wi-fi à operadora; no notebook, o `docker-proxy` liga o loopback à rede do Docker (a linha `ports` do compose).
- **Internet**: milhões de redes ligadas por roteadores. Para o YouTube: casa → operadora → redes de trânsito → rede do Google (`traceroute youtube.com` mostra cada roteador).

![[redes-do-notebook.drawio.svg]]
*Cada caixa é uma rede separada; o tracejado liga a mesma máquina nas redes em que ela está (notebook em três, roteador em duas).*

## Do nome até o programa

1. [[DNS e domínio|DNS]]: o nome vira o IP público.
2. O cliente abre uma conexão TCP com `IP:porta`.
3. Firewall (na nuvem, o [[Security Group e SSM|Security Group]]): a porta está liberada? Se não, a conexão nem chega à máquina.
4. A máquina entrega a conexão ao programa que escuta naquela porta.

## Rede de containers

Cada [[Container e Docker Compose|container]] é como uma máquina pequena: tem IP privado próprio e suas portas.

- O [[Container e Docker Compose|compose]] cria uma **rede** e põe todos os serviços do arquivo nela. Lá dentro, o **nome do serviço** é o endereço: `http://api:8000` acha o container `api` (o Docker tem um DNS interno).
- **Porta publicada** (`ports: ["443:443"]`): liga a porta da máquina à do container. `host:container`. Só o que é publicado é alcançável de fora da máquina. Com IP na frente (`127.0.0.1:8000:8000`), a porta da máquina só aceita quem está nela; sem IP, aceita por qualquer rede da máquina.
- Serviço sem `ports` continua falando com os vizinhos pela rede do compose; só não recebe nada de fora.
- **`0.0.0.0` dentro do container** = todas as interfaces **do container**: o loopback dele e a rede do Docker; a rede do host não entra na conta. Escutar só no IP da rede do Docker não serve: ele é escolhido a cada container criado (`172.18.0.x` muda). O controle de quem alcança fica fora, no `ports:` (`127.0.0.1:8000:8000` publica só no loopback do host).

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
