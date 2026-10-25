---
tags: [noteproject, conceito, infra]
---
# TCP e pacotes

O [[IP, porta e rede de containers|IP e a porta]] dizem para qual máquina e qual programa algo vai. Falta como os bytes chegam lá: a rede só carrega pedaços pequenos, que podem se perder ou chegar fora de ordem. O TCP monta, em cima disso, uma linha de bytes confiável entre dois programas.

## Pacote

- Nada viaja como um bloco grande: os dados são cortados em **pacotes** de até ~1,5 KB (o limite comum do cabo e do wi-fi, o MTU de 1500 bytes). Uma foto de 3 MB vira uns 2 mil pacotes. *(geral)*
- Cada pacote leva um cabeçalho, como um envelope: IP e porta de origem, IP e porta de destino, e o pedaço dos dados.
- Os roteadores olham só o IP de destino; a máquina que recebe olha a porta para saber a qual programa entregar.

## Como o pacote chega em outra rede

Direto, uma máquina só alcança quem está na mesma rede. Para sair dela, entra o **roteador**: uma máquina que está em duas ou mais redes **e repassa** pacotes entre elas. Estar em duas redes não basta; no Linux, repassar depende de `net.ipv4.ip_forward = 1`.

### Tabela de rotas

Cada máquina decide só o próximo pulo, pela sua **tabela de rotas** (`ip route`), guardada na memória dela: não existe tabela central "na rede".

```
192.168.15.0/24 dev wlan0    → destino 192.168.15.x: direto pelo wi-fi
172.18.0.0/16   dev br-…     → destino 172.18.x.x: direto para a rede do Docker
default via 192.168.15.1     → todo o resto: para o gateway (o roteador de casa)
```

- `/24` diz quantos bits do começo do IP são a rede: `/24` = os três primeiros números iguais (`192.168.15.x`); `/16` = os dois primeiros.
- **Gateway**: o roteador da linha `default`, a saída da rede. Quem escreve essa linha é o DHCP, junto com o IP. Com duas linhas `default`, vence a de menor `metric`. *(geral)*
- Uma máquina em várias redes também roteia: um notebook com Docker repassa pacotes entre o wi-fi e a rede dos [[Container e Docker Compose|containers]], e é o gateway deles.
- **Vários roteadores na mesma rede**: cada linha da tabela diz por qual roteador ir (`via 192.168.15.1`), conforme o destino. O IP de destino do pacote não muda; a máquina o entrega ao roteador escolhido pelo endereço de placa dele (MAC), que ela descobre perguntando na rede local "quem é 192.168.15.1?" (ARP, `ip neigh`). *(geral)*

### Blocos anunciados

Nenhum roteador conhece o caminho inteiro: cada um sabe só qual vizinho está mais perto de cada destino. Isso funciona porque o IP é dividido em **blocos**, como um CEP: o Google é dono de `142.250.0.0/15` (todo IP que começa com `142.250` ou `142.251`).

- O dono **anuncia** o bloco aos vizinhos ("cheguem a 142.250.0.0/15 por mim"); cada vizinho anota de quem ouviu e repassa o anúncio (BGP). Os anúncios correm **antes** de qualquer pacote.
- Cada roteador fica com uma tabela **bloco → vizinho**; os do meio da internet têm na casa de 1 milhão de blocos. No pacote, ele olha só o destino e escolhe o bloco mais específico que o contém: uma consulta, sem busca nem tentativa.
- O pacote sobe só até um roteador que conhece o bloco e desce rumo ao dono. O roteador do dono entrega à máquina pela rede local dele.
- Roteadores pequenos têm `default` ("o resto vai para cima"); os do topo da internet não têm, e descartam o que nenhuma linha cobre, com um erro "destino inalcançável".
- **IP novo**: um site novo quase sempre pega IP de um bloco do provedor (AWS, Google Cloud), já anunciado, e nenhuma tabela muda. Um bloco novo é dado pelo registro da região (LACNIC, na América Latina) e anunciado; em minutos as tabelas ganham a linha. *(geral)*

![[blocos-anunciados.drawio.svg]]
*Cada roteador anota de quem ouviu cada bloco; o pacote sobe até quem conhece o bloco e desce rumo ao dono.*

### NAT

**NAT** (Network Address Translation): IP privado (`192.168.x.x`) não vale na internet. O roteador de casa reescreve a origem do pacote com o IP público dele, o mesmo para todas as máquinas da casa, e anota a troca numa tabela. A volta chega ao IP público; a **porta** diz de quem é. *(geral)*

```
tabela do NAT (roteador de casa)
203.0.113.7:51234  ⇄  192.168.15.156:51234   (notebook)
203.0.113.7:40001  ⇄  192.168.15.171:40001   (celular)
```

- Se duas máquinas sorteiam a mesma porta, o roteador troca uma delas por outra livre e anota.
- A linha da tabela só nasce quando alguém **de dentro** abre a conexão. Pacote que chega de fora sem linha correspondente é descartado: um servidor na internet não consegue iniciar conexão com o notebook atrás do NAT, a menos que o roteador tenha um redirecionamento de porta configurado. Por isso servidor fica em IP público, e o cliente é quem conecta; num [[WebSocket]], o servidor fala pela linha que o cliente abriu.
- Muitas operadoras fazem um segundo NAT (CGNAT): o IP "público" do roteador de casa é compartilhado com vizinhos.

| Tabela | Onde fica | Responde |
|---|---|---|
| de rotas | em todo roteador e em toda máquina | bloco de destino → próximo vizinho: acha o servidor na ida e a casa na volta |
| do NAT | só no roteador que faz NAT (o de casa) | porta pública ⇄ aparelho de dentro: acha o notebook ou o celular na volta |

### Ida e volta

- Na ida, o destino nunca muda. A origem muda uma vez só, no NAT; os roteadores do caminho só leem o pacote e repassam.
- A volta é um **pacote novo**: origem = o servidor, destino = o IP público e a porta que vieram na origem da ida. Ele é roteado do zero pelas tabelas (o bloco da operadora também é anunciado) e pode seguir outro caminho. No roteador de casa, o NAT troca o destino de volta para a máquina de dentro.

![[tcp-pc-google.drawio.svg]]
*Na ida, cada roteador consulta a própria tabela de rotas; na volta, o NAT desfaz a troca pela porta.*

## TCP: a linha confiável

A rede pode perder, duplicar ou trocar a ordem dos pacotes. O TCP numera cada byte e confirma o que chegou:

| Passo | Marca no cabeçalho | Quer dizer |
|---|---|---|
| abrir | **SYN** (synchronize) | "quero abrir uma linha; meus bytes começam a contar em X" |
| responder | **SYN+ACK** | "aceito; os meus começam em Y, e recebi o seu X" |
| confirmar | **ACK** (acknowledge) | "recebi o seu Y": linha aberta |
| usar | dados + ACK | quem recebe confirma até onde chegou; o que não foi confirmado é reenviado, e os números põem os pedaços na ordem |
| fechar | **FIN** | "terminei de falar"; cada lado manda o seu |

![[tcp-conversa.drawio.svg]]
*A conversa no tempo, de cima para baixo: o aperto de mão (1–3), dados com confirmação (4–5) e o fim (6).*

- Uma conexão é o par (IP:porta do cliente, IP:porta do servidor). A porta do cliente é sorteada pelo sistema dele (`51234`), e é para ela que a resposta volta.
- O aperto de mão custa uma ida e volta antes do primeiro byte útil; por isso vale manter a linha aberta e reaproveitar (o pool de conexões do [[SQLAlchemy — engine e conexão|SQLAlchemy]]).

## Muitos pacotes ao mesmo tempo

- Cada placa de rede tem uma **fila** de pacotes, esvaziada em ordem e muito rápido.
- Fila cheia → o pacote que chega é **descartado**. A rede não avisa ninguém.
- O TCP percebe pelo ACK que não veio: reenvia o que faltou e **diminui o ritmo** de envio (controle de congestionamento), e volta a acelerar aos poucos. *(geral)*

## Camadas: o que vai dentro da linha

O TCP só entrega bytes; o sentido deles vem do protocolo de cima.

| Protocolo | Por cima do TCP | Quem fala primeiro |
|---|---|---|
| HTTP | texto `GET /health ...` e a resposta, na mesma linha | só o cliente pergunta; o servidor só responde |
| [[WebSocket]] | começa como um pedido HTTP com `Upgrade: websocket`; depois, mensagens nos dois sentidos | qualquer lado, quando quiser |
| [[Postgres e migrations\|Postgres]] | protocolo próprio na porta 5432 (login, consulta, linhas de volta); não é HTTP | o cliente (a API) |

Docs: [RFC 9293 — TCP](https://www.rfc-editor.org/rfc/rfc9293), [RFC 5681 — controle de congestionamento](https://www.rfc-editor.org/rfc/rfc5681), [RFC 3022 — NAT](https://www.rfc-editor.org/rfc/rfc3022), [RFC 6455 — WebSocket](https://www.rfc-editor.org/rfc/rfc6455), `man ip-route`.
