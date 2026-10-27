---
tags: [noteproject, conceito, infra]
---
# Rede

Duas máquinas só trocam dados se estão ligadas, por cabo ou wi-fi, e se uma sabe o endereço da outra. A rede é esse grupo de máquinas que se alcançam direto.

- **Rede**: grupo de máquinas que falam direto entre si, com [[Endereço IP|IPs]] da mesma faixa (o wi-fi de casa: `192.168.0.x`).
- Uma máquina está em várias redes, com um IP em cada: o notebook é `127.0.0.1`, `192.168.0.223` e `172.18.0.1` ao mesmo tempo (`ip -4 -br addr`).
- **Loopback** (`127.x`, nome `localhost`): a rede em que só está a própria máquina; nada sai pelo cabo ou wi-fi. Cada máquina tem a sua, e cada [[Container|container]] também.
- **Ligar duas redes**: uma máquina que está nas duas repassa o pedido ([[Roteamento|roteador]]). O roteador liga o wi-fi à operadora; no notebook, o `docker-proxy` liga o loopback à rede do Docker ([[Rede de containers]]).
- **Internet**: milhões de redes ligadas por roteadores. Para o YouTube: casa → operadora → redes de trânsito → rede do Google (`traceroute youtube.com` mostra cada roteador).

![[redes-do-notebook.drawio.svg]]
*Cada caixa é uma rede separada; o tracejado liga a mesma máquina nas redes em que ela está (notebook em três, roteador em duas). 1 e 2: o caminho de `127.0.0.1:8000` até o container, pelo `docker-proxy`.*

Doc: `man ip-address`.
