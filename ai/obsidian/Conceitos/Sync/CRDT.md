---
tags: [noteproject, conceito, sync]
---
# CRDT

Com [[Local-first|local-first]], dois dispositivos podem editar o mesmo documento ao mesmo tempo, ou offline. Quando se encontram, as duas versões precisam virar uma, sem perder texto e sem perguntar a ninguém.

- **CRDT** (*Conflict-free Replicated Data Type*): estrutura em que cada cópia aceita edições sozinha, e juntar as cópias dá o mesmo resultado em qualquer ordem.
- A lib de CRDT mais usada em JavaScript é o [[Yjs]].

## Como junta

1. Cada caractere tem um id único (dispositivo + contador).
2. "Inserir depois do caractere X" continua valendo mesmo que outro tenha mexido em outro lugar.
3. Juntar = aplicar os updates dos dois lados; a ordem não muda o resultado.

| Sem CRDT | Com CRDT |
|---|---|
| quem salva por último ganha; o outro perde o que digitou | as duas edições ficam |
| conflito para alguém resolver | sem conflito no texto |

Doc: [crdt.tech](https://crdt.tech/).
