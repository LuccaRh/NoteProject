---
tags: [noteproject, conceito, infra]
---
# TCP

O [[Endereço IP|IP]] e a [[Porta|porta]] dizem para qual máquina e qual programa algo vai. Falta como os bytes chegam lá: a rede só carrega pedaços pequenos, que podem se perder ou chegar fora de ordem. O TCP monta, em cima disso, uma linha de bytes confiável entre dois programas.

## Pacote

- Nada viaja como um bloco grande: os dados são cortados em **pacotes** de até ~1,5 KB (o limite comum do cabo e do wi-fi, o MTU de 1500 bytes). Uma foto de 3 MB vira uns 2 mil pacotes. *(geral)*
- Cada pacote leva um cabeçalho, como um envelope: IP e porta de origem, IP e porta de destino, e o pedaço dos dados.
- Os roteadores olham só o IP de destino ([[Roteamento|roteamento]]); a máquina que recebe olha a porta para saber a qual programa entregar.

## A linha confiável

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
- A conexão é só **uma linha numa tabela do sistema operacional de cada ponta** (portas, estado, até que byte foi mandado e recebido); nenhum fio nem roteador sabe dela. Cada pacote viaja sozinho, e a ponta que o recebe acha a linha pelas portas do cabeçalho e atualiza os números. Ver a tabela: `ss -tn`.
- O aperto de mão custa uma ida e volta antes do primeiro byte útil; por isso vale manter a linha aberta e reaproveitar (o pool de conexões do [[SQLAlchemy]]).

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
| [[Postgres]] | protocolo próprio na porta 5432 (login, consulta, linhas de volta); não é HTTP | o cliente (a API) |

Docs: [RFC 9293 — TCP](https://www.rfc-editor.org/rfc/rfc9293), [RFC 5681 — controle de congestionamento](https://www.rfc-editor.org/rfc/rfc5681), [RFC 6455 — WebSocket](https://www.rfc-editor.org/rfc/rfc6455).
