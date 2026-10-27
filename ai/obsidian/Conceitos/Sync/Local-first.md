---
tags: [noteproject, conceito, sync]
---
# Local-first

Um app de notas precisa responder na hora a cada tecla e, ao mesmo tempo, mostrar a mesma nota em vários dispositivos. Se cada tecla esperasse o servidor, digitar teria o atraso da rede.

Local-first inverte a ordem: **toda operação acontece primeiro no dispositivo**; a rede propaga depois, em segundo plano, sem segurar a digitação.

## Como funciona

1. A tecla grava num banco local (um [[SQLite]], por exemplo) e aparece na tela na hora.
2. Em segundo plano, a mudança vai a um servidor de sync, que repassa aos outros dispositivos.
3. Sem rede, o passo 2 espera; o passo 1 continua igual.

- Offline não é um modo à parte: é o passo 2 atrasado.
- Sync ao vivo e local-first são a mesma ideia: a rede nunca está no caminho da tecla.

## O que isso exige

| Exigência | Por quê | Peça |
|---|---|---|
| banco no dispositivo | ler e escrever sem rede | [[SQLite]] |
| juntar edições paralelas | dois dispositivos editam offline e depois se encontram | [[CRDT]] e [[Yjs]] |
| saber o que mudou | quem volta do offline pede só a diferença | [[Sync por versão]] |
| canal aberto com o servidor | a mudança chega aos outros em ~50–200 ms | [[WebSocket]] |

## Velocidade vem da arquitetura

| Escolha | Diferença por operação *(estimativa)* |
|---|---|
| local-first × esperar a rede | 50–500 ms |
| renderizar na web × nativo | 10–20 ms |
| linguagem do back | 0–2 ms |

Nada do caminho de digitar, buscar e criar passa pela rede nem pela linguagem do back.

> [!example] No NoteProject
> No app desktop, a tecla grava no [[O daemon notesd|notesd]] e o sync vem depois ([[Back — daemon e servidor]]).

Ensaio que deu nome à ideia: [Ink & Switch, *Local-first software*](https://www.inkandswitch.com/essay/local-first/).
