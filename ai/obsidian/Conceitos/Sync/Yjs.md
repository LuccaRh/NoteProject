---
tags: [noteproject, conceito, sync]
---
# Yjs

Um editor colaborativo precisa de um [[CRDT]] pronto, ligado ao editor e a um canal de rede. O Yjs é a biblioteca de CRDT em JavaScript que faz isso.

- Cada edição gera um *update* pequeno e binário; aplicar os updates de outro dispositivo junta as edições.
- `y-codemirror.next` liga o documento Yjs a um editor [[CodeMirror]].
- Os updates viajam por qualquer canal; o comum é um [[WebSocket]] até um servidor que junta e repassa.
- `y-py` (e `pycrdt`) leem e juntam os mesmos updates em Python.
- O documento inteiro pode ser salvo como um snapshot binário, guardado fora do banco ([[S3]]).

> [!example] No NoteProject
> O sync de M4 leva os updates do editor ao servidor ([[Back — daemon e servidor]]).

Doc: [Yjs](https://docs.yjs.dev/).
