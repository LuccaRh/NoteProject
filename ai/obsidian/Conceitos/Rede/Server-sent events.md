---
tags: [noteproject, conceito, servidor]
---
# Server-sent events

Uma resposta HTTP comum chega inteira de uma vez: o servidor monta o corpo e o cliente só o lê no fim. Quando a resposta demora e sai aos poucos (um modelo escrevendo, um progresso), o cliente ficaria parado até o último byte. SSE (*Server-sent events*) é o formato para o servidor mandar pedaços pela mesma resposta, à medida que ficam prontos.

## Como é

O cliente faz um pedido HTTP normal; o servidor responde com `Content-Type: text/event-stream` e não fecha a resposta. Cada evento é texto: linhas `campo: valor` e uma linha em branco no fim.

```
event: text_delta
data: {"text": "Olá"}

event: message_end
data: {"stop_reason": "end_turn"}

```

- `data:` é o conteúdo; `event:` dá um nome, para o cliente tratar cada tipo de um jeito. Sem `event:`, o nome é `message`.
- A conexão fica aberta até o servidor terminar; o [[TCP]] entrega os pedaços em ordem.
- O status (200, 404...) sai antes do primeiro evento. Erro depois disso só pode ir como mais um evento.

## Comparado

| | SSE | [[WebSocket]] |
|---|---|---|
| direção | só servidor → cliente | os dois lados, a qualquer hora |
| por cima de | HTTP comum | HTTP que vira outro protocolo (*upgrade*) |
| bom para | resposta longa a um pedido | conversa contínua, edição ao vivo |

No navegador, o `EventSource` lê SSE de um `GET`; para `POST` com corpo, o `fetch` lê a resposta aos pedaços.

> [!example]
> O `lonzo` responde o chat em SSE: cada pedaço do modelo vira um `text_delta` ([[Caminho de uma pergunta]]).

## Fontes

- WHATWG, *Server-sent events*: https://html.spec.whatwg.org/multipage/server-sent-events.html
