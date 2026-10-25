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
*Cada caixa é uma rede separada; o tracejado liga a mesma máquina nas redes em que ela está (notebook em três, roteador em duas). 1 e 2: o caminho de `127.0.0.1:8000` até o container, pelo `docker-proxy`.*

## De onde vem o IP

- Ninguém "cria" a rede: basta o caminho físico (cabo ou wi-fi) e um IP da mesma faixa em cada aparelho.
- **Automático (DHCP)**: um servidor na rede (em casa, o roteador) entrega o IP a quem se conecta.
- **Fixo**: digitado à mão na configuração de cada aparelho. Muda-se para qualquer valor, com duas condições: o mesmo começo dos vizinhos (com máscara `255.255.255.0`, os três primeiros números) e nenhum outro aparelho com o mesmo IP.
- Quem guarda o IP de outro aparelho (um script, uma IHM) precisa ser atualizado junto; senão procura um endereço onde não há ninguém.

> [!example] Bancada de CLP
> Rede cabeada só de IP fixo `192.168.101.x`, sem DHCP: o IP do CLP vai na configuração de hardware do TIA Portal (Devices & networks → Ethernet addresses, e depois download); o do PC, nas configurações da placa de rede com fio; o da IHM, na configuração dela. Um script Python que fala com o CLP (python-snap7) traz o IP do CLP escrito no código.

## Do nome até o programa

1. [[DNS e domínio|DNS]]: o nome vira o IP público.
2. O cliente abre uma conexão [[TCP e pacotes|TCP]] com `IP:porta`.
3. Firewall (na nuvem, o [[Security Group e SSM|Security Group]]): a porta está liberada? Se não, a conexão nem chega à máquina.
4. A máquina entrega a conexão ao programa que escuta naquela porta.

## Rede de containers

Cada [[Container e Docker Compose|container]] é como uma máquina pequena: tem IP privado próprio e suas portas.

- O [[Container e Docker Compose|compose]] cria uma **rede** e põe todos os serviços do arquivo nela. Lá dentro, o **nome do serviço** é o endereço: `http://api:8000` acha o container `api` (o Docker tem um DNS interno).
- **Qual DNS responde**: o programa pergunta ao DNS que está no `/etc/resolv.conf` de onde ele roda. Dentro de um container do compose, é o DNS do Docker (`nameserver 127.0.0.11`), que conhece os nomes dos serviços; na máquina, é o da rede (do roteador ou da rede da faculdade), que não conhece. Por isso `curl notes:8000` da máquina falha com `Could not resolve host`, e de lá o caminho é a porta publicada (`curl localhost:8000`).
- O IP do container (`172.18.0.x`) é dado quando ele é criado e pode mudar no próximo `up`; o nome do serviço não muda. Por isso URLs e configs usam o nome.
- **Porta publicada** (`ports: ["443:443"]`): liga a porta da máquina à do container. `host:container`. Só o que é publicado é alcançável de fora da máquina. Com IP na frente (`127.0.0.1:8000:8000`), a porta da máquina só aceita quem está nela; sem IP, aceita por qualquer rede da máquina.
- **Quem atende a porta publicada**: a porta é mesmo a da máquina. Ao subir o container, o Docker põe o `docker-proxy` para escutar nela; a máquina não sabe do container e entrega a conexão a quem escuta na porta, como faz com qualquer programa.
- O `docker-proxy` abre outra conexão, da máquina (`172.18.0.1`) até a porta do container (`172.18.0.4:8000`), e copia os bytes nos dois sentidos. `pgrep -a docker-proxy` mostra um processo por porta publicada, com o IP e a porta de destino.
- Porta da máquina já ocupada por outro programa → o container não sobe (`address already in use`).
- Pedido vindo de outra máquina pode nem passar pelo proxy: o Docker também grava regras de NAT (DNAT) no firewall do Linux (iptables/nftables), e o kernel troca o destino do pacote para o IP do container. *(geral)*
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

Docs: [Networking in Compose](https://docs.docker.com/compose/how-tos/networking/), [Docker — DNS services](https://docs.docker.com/engine/network/#dns-services), [Docker — published ports](https://docs.docker.com/engine/network/#published-ports).
