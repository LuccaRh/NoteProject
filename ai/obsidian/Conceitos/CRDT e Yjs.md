---
tags: [noteproject, conceito, sync]
---
# CRDT e Yjs

Com [[Local-first|local-first]], dois dispositivos podem editar o mesmo documento ao mesmo tempo, ou offline. Quando se encontram, as duas versões precisam virar uma, sem perder texto e sem perguntar a ninguém.

- **CRDT** (*Conflict-free Replicated Data Type*): estrutura em que cada cópia aceita edições sozinha, e juntar as cópias dá o mesmo resultado em qualquer ordem.
- **Yjs**: biblioteca de CRDT em JavaScript. Cada edição gera um *update* pequeno e binário.

## Como junta

1. Cada caractere tem um id único (dispositivo + contador).
2. "Inserir depois do caractere X" continua valendo mesmo que outro tenha mexido em outro lugar.
3. Juntar = aplicar os updates dos dois lados; a ordem não muda o resultado.

| Sem CRDT | Com CRDT |
|---|---|
| quem salva por último ganha; o outro perde o que digitou | as duas edições ficam |
| conflito para alguém resolver | sem conflito no texto |

## Em volta do Yjs

- `y-codemirror.next` liga o documento Yjs a um editor [[CodeMirror e decorações|CodeMirror]].
- Os updates viajam por qualquer canal; o comum é um [[WebSocket]] até um servidor que junta e repassa.
- `y-py` (e `pycrdt`) leem e juntam os mesmos updates em Python.

> [!example] No NoteProject
> O sync de M4 leva os updates do editor ao servidor ([[Back — daemon e servidor]]).

Docs: [Yjs](https://docs.yjs.dev/), [crdt.tech](https://crdt.tech/).
