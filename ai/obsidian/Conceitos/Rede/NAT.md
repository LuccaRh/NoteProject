---
tags: [noteproject, conceito, infra]
---
# NAT

[[Endereço IP|IP]] privado (`192.168.x.x`) não vale na internet, e uma casa tem um IP público só para todos os aparelhos. O NAT faz os aparelhos de dentro saírem por esse IP público e acha de quem é cada resposta.

- **NAT** (Network Address Translation): o roteador de casa reescreve a origem do pacote com o IP público dele, o mesmo para todas as máquinas da casa, e anota a troca numa tabela. A volta chega ao IP público; a **[[Porta|porta]]** diz de quem é. *(geral)*

```
tabela do NAT (roteador de casa)
203.0.113.7:51234  ⇄  192.168.15.156:51234   (notebook)
203.0.113.7:40001  ⇄  192.168.15.171:40001   (celular)
```

- Se duas máquinas sorteiam a mesma porta, o roteador troca uma delas por outra livre e anota.
- A linha da tabela só nasce quando alguém **de dentro** abre a conexão. Pacote que chega de fora sem linha correspondente é descartado: um servidor na internet não consegue iniciar conexão com o notebook atrás do NAT, a menos que o roteador tenha um redirecionamento de porta configurado. Por isso servidor fica em IP público, e o cliente é quem conecta; num [[WebSocket]], o servidor fala pela linha que o cliente abriu.
- Muitas operadoras fazem um segundo NAT (CGNAT): o IP "público" do roteador de casa é compartilhado com vizinhos.
- O mesmo truque ao contrário (trocar o **destino**, DNAT) é o que o Docker faz para levar uma porta publicada até o container ([[Rede de containers#Porta publicada|porta publicada]]).
- Onde o NAT entra na ida e na volta de um pedido: [[Roteamento#Ida e volta|ida e volta]].

Doc: [RFC 3022 — NAT](https://www.rfc-editor.org/rfc/rfc3022).
