---
tags: [noteproject, conceito, sync]
---
# WebSocket

HTTP é pedido e resposta: o cliente pergunta, o servidor responde, acabou. Num sync, o servidor precisa **mandar** a mudança assim que outro dispositivo edita, sem esperar pedido.

WebSocket é uma conexão que fica aberta nos dois sentidos. Começa como um pedido HTTP com `Upgrade: websocket`; depois, cliente e servidor mandam mensagens quando quiserem.

| | HTTP | WebSocket |
|---|---|---|
| quem começa a mensagem | só o cliente | os dois |
| conexão | por pedido | uma, aberta |
| bom para | ler, salvar, login | updates ao vivo |

- Atrás de um [[Reverse proxy|reverse proxy]], o proxy precisa repassar o `Upgrade` e não cortar a conexão parada.
- Cada instância do servidor só conhece as próprias conexões; com mais de uma, elas se avisam por [[Redis pub-sub|pub/sub]].
- Quem ficou offline perdeu as mensagens: volta por outro caminho, como o [[Sync por versão]].

> [!example] No NoteProject
> O endpoint `/sync` do servidor leva os updates do [[Yjs]] ([[Back — daemon e servidor]]).

Spec: [RFC 6455](https://datatracker.ietf.org/doc/html/rfc6455).
