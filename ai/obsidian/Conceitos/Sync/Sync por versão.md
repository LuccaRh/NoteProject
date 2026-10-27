---
tags: [noteproject, conceito, sync]
---
# Sync por versão

Um [[WebSocket]] entrega as mudanças a quem está conectado. Um dispositivo que ficou offline perdeu essas mensagens e precisa saber o que mudou, sem baixar tudo de novo.

A ideia: o servidor numera cada mudança com um contador que só cresce (`version`). O dispositivo guarda o último número que viu.

## Como volta do offline

1. O dispositivo guardou `N`, a última versão que recebeu.
2. Ao reconectar, pede tudo com `version > N`.
3. O servidor devolve só o que mudou; o dispositivo aplica e guarda o novo `N`.

- Com um contador por usuário (e não por nota), uma consulta só acha tudo o que mudou.
- O que foi editado offline sobe do mesmo jeito; quem junta as duas edições é um [[CRDT]].

> [!example] No NoteProject
> Coluna `version` em `notes` no servidor ([[Back — daemon e servidor]]).
