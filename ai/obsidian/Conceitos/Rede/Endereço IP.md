---
tags: [noteproject, conceito, infra]
---
# Endereço IP

Um pedido pela rede precisa dizer duas coisas: **qual máquina** e **qual programa dentro dela**. A máquina é o IP; o programa é a [[Porta|porta]].

- **IP**: o endereço da máquina numa [[Rede|rede]]. Público (`203.0.113.7`) a internet alcança; privado (`172.18.0.3`, `192.168.0.x`) só quem está na mesma rede.
- Uma máquina em várias redes tem um IP em cada (`ip -4 -br addr`).
- O IP é dividido em blocos, como um CEP: `/24` diz que os três primeiros números são a rede (`192.168.15.x`); `/16`, os dois primeiros. É o que o [[Roteamento|roteamento]] usa para achar o caminho.
- IP privado não vale na internet: o roteador de casa troca pelo público dele ([[NAT]]).

## De onde vem o IP

- Ninguém "cria" a rede: basta o caminho físico (cabo ou wi-fi) e um IP da mesma faixa em cada aparelho.
- **Automático (DHCP)**: um servidor na rede (em casa, o roteador) entrega o IP a quem se conecta.
- **Fixo**: digitado à mão na configuração de cada aparelho. Muda-se para qualquer valor, com duas condições: o mesmo começo dos vizinhos (com máscara `255.255.255.0`, os três primeiros números) e nenhum outro aparelho com o mesmo IP.
- Quem guarda o IP de outro aparelho (um script, uma IHM) precisa ser atualizado junto; senão procura um endereço onde não há ninguém.
- IP é difícil de lembrar e muda quando a máquina é recriada; por isso os clientes usam um [[Domínio|nome]], traduzido pelo [[DNS]].

> [!example] Bancada de CLP
> Rede cabeada só de IP fixo `192.168.101.x`, sem DHCP: o IP do CLP vai na configuração de hardware do TIA Portal (Devices & networks → Ethernet addresses, e depois download); o do PC, nas configurações da placa de rede com fio; o da IHM, na configuração dela. Um script Python que fala com o CLP (python-snap7) traz o IP do CLP escrito no código.

Doc: `man ip-address`.
