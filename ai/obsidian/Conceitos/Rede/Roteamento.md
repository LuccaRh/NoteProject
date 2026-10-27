---
tags: [noteproject, conceito, infra]
---
# Roteamento

Direto, uma máquina só alcança quem está na mesma [[Rede|rede]]. Para um pacote ([[TCP#Pacote|pacote]]) chegar a outra rede, alguém no meio precisa repassá-lo, e cada um no caminho precisa saber para onde.

- **Roteador**: uma máquina que está em duas ou mais redes **e repassa** pacotes entre elas. Estar em duas redes não basta; no Linux, repassar depende de `net.ipv4.ip_forward = 1`.

## Tabela de rotas

Cada máquina decide só o próximo pulo, pela sua **tabela de rotas** (`ip route`), guardada na memória dela: não existe tabela central "na rede".

```
192.168.15.0/24 dev wlan0    → destino 192.168.15.x: direto pelo wi-fi
172.18.0.0/16   dev br-…     → destino 172.18.x.x: direto para a rede do Docker
default via 192.168.15.1     → todo o resto: para o gateway (o roteador de casa)
```

- `/24` diz quantos bits do começo do [[Endereço IP|IP]] são a rede: `/24` = os três primeiros números iguais (`192.168.15.x`); `/16` = os dois primeiros.
- **Gateway**: o roteador da linha `default`, a saída da rede. Quem escreve essa linha é o DHCP, junto com o IP. Com duas linhas `default`, vence a de menor `metric`. *(geral)*
- Uma máquina em várias redes também roteia: um notebook com Docker repassa pacotes entre o wi-fi e a [[Rede de containers|rede dos containers]], e é o gateway deles.
- **Vários roteadores na mesma rede**: cada linha da tabela diz por qual roteador ir (`via 192.168.15.1`), conforme o destino. O IP de destino do pacote não muda; a máquina o entrega ao roteador escolhido pelo endereço de placa dele (MAC), que ela descobre perguntando na rede local "quem é 192.168.15.1?" (ARP, `ip neigh`). *(geral)*

## Blocos anunciados

Nenhum roteador conhece o caminho inteiro: cada um sabe só qual vizinho está mais perto de cada destino. Isso funciona porque o IP é dividido em **blocos**, como um CEP: o Google é dono de `142.250.0.0/15` (todo IP que começa com `142.250` ou `142.251`).

- O dono **anuncia** o bloco aos vizinhos ("cheguem a 142.250.0.0/15 por mim"); cada vizinho anota de quem ouviu e repassa o anúncio (BGP). Os anúncios correm **antes** de qualquer pacote.
- Cada roteador fica com uma tabela **bloco → vizinho**; os do meio da internet têm na casa de 1 milhão de blocos. No pacote, ele olha só o destino e escolhe o bloco mais específico que o contém: uma consulta, sem busca nem tentativa.
- O pacote sobe só até um roteador que conhece o bloco e desce rumo ao dono. O roteador do dono entrega à máquina pela rede local dele.
- Roteadores pequenos têm `default` ("o resto vai para cima"); os do topo da internet não têm, e descartam o que nenhuma linha cobre, com um erro "destino inalcançável".
- **IP novo**: um site novo quase sempre pega IP de um bloco do provedor (AWS, Google Cloud), já anunciado, e nenhuma tabela muda. Um bloco novo é dado pelo registro da região (LACNIC, na América Latina) e anunciado; em minutos as tabelas ganham a linha. *(geral)*

![[blocos-anunciados.drawio.svg]]
*Cada roteador anota de quem ouviu cada bloco; o pacote sobe até quem conhece o bloco e desce rumo ao dono.*

## Ida e volta

- Na ida, o destino nunca muda. A origem muda uma vez só, no [[NAT]] do roteador de casa; os roteadores do caminho só leem o pacote e repassam.
- A volta é um **pacote novo**: origem = o servidor, destino = o IP público e a porta que vieram na origem da ida. Ele é roteado do zero pelas tabelas (o bloco da operadora também é anunciado) e pode seguir outro caminho. No roteador de casa, o NAT troca o destino de volta para a máquina de dentro.

![[tcp-pc-google.drawio.svg]]
*Na ida, cada roteador consulta a própria tabela de rotas; na volta, o NAT desfaz a troca pela porta.*

| Tabela | Onde fica | Responde |
|---|---|---|
| de rotas | em todo roteador e em toda máquina | bloco de destino → próximo vizinho: acha o servidor na ida e a casa na volta |
| do [[NAT]] | só no roteador que faz NAT (o de casa) | porta pública ⇄ aparelho de dentro: acha o notebook ou o celular na volta |

Docs: `man ip-route`, `traceroute`.
