---
tags: [noteproject, conceito, infra]
---
# Rede de containers

Cada [[Container|container]] é como uma máquina pequena: tem [[Endereço IP|IP]] privado próprio e suas [[Porta|portas]]. Os containers de um sistema precisam se achar entre si, e só alguns devem ser alcançados de fora.

- O [[Docker Compose|compose]] cria uma **[[Rede|rede]]** e põe todos os serviços do arquivo nela. Lá dentro, o **nome do serviço** é o endereço: `http://api:8000` acha o container `api` (o Docker tem um [[DNS]] interno).
- **Qual DNS responde**: o programa pergunta ao DNS que está no `/etc/resolv.conf` de onde ele roda. Dentro de um container do compose, é o DNS do Docker (`nameserver 127.0.0.11`), que conhece os nomes dos serviços; na máquina, é o da rede (do roteador ou da rede da faculdade), que não conhece. Por isso `curl ichiro:8000` da máquina falha com `Could not resolve host`, e de lá o caminho é a porta publicada (`curl localhost:8000`).
- O IP do container (`172.18.0.x`) é dado quando ele é criado e pode mudar no próximo `up`; o nome do serviço não muda. Por isso URLs e configs usam o nome.

## Porta publicada

- `ports: ["443:443"]` liga a porta da máquina à do container. `host:container`. Só o que é publicado é alcançável de fora da máquina. Com IP na frente (`127.0.0.1:8000:8000`), a porta da máquina só aceita quem está nela; sem IP, aceita por qualquer rede da máquina.
- **Quem atende a porta publicada**: a porta é mesmo a da máquina. Ao subir o container, o Docker põe o `docker-proxy` para escutar nela; a máquina não sabe do container e entrega a conexão a quem escuta na porta, como faz com qualquer programa.
- O `docker-proxy` abre outra conexão, da máquina (`172.18.0.1`) até a porta do container (`172.18.0.4:8000`), e copia os bytes nos dois sentidos. `pgrep -a docker-proxy` mostra um processo por porta publicada, com o IP e a porta de destino.
- Porta da máquina já ocupada por outro programa → o container não sobe (`address already in use`).
- Pedido vindo de outra máquina pode nem passar pelo proxy: o Docker também grava regras de [[NAT]] (DNAT) no firewall do Linux (iptables/nftables), e o kernel troca o destino do pacote para o IP do container. *(geral)*
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
