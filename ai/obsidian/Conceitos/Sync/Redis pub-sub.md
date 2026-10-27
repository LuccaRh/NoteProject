---
tags: [noteproject, conceito, sync]
---
# Redis pub-sub

Um servidor de sync guarda na memória quem está conectado. Com duas instâncias, um cliente ligado na instância A edita, e quem está na B não fica sabendo.

- **Pub/sub**: quem publica manda a mensagem para um canal; todos os inscritos recebem.
- **Redis**: banco em memória que tem pub/sub.

1. A instância A recebe o update e publica no canal do documento.
2. A instância B, inscrita no canal, recebe e repassa pelos seus [[WebSocket|WebSockets]].

- Só serve com mais de uma instância; com uma só, a memória do processo basta.

> [!example] No NoteProject
> Fica de fora enquanto houver um sync só ([[Back — daemon e servidor]]).

Doc: [Redis Pub/Sub](https://redis.io/docs/latest/develop/pubsub/).
