---
tags: [noteproject, conceito, cliente-api]
---
# UI otimista

Um app que guarda os dados num servidor precisa esperar a resposta para saber se a gravação deu certo. Se a tela também esperar, cada ação demora o tempo de ida e volta da rede (50–500 ms).

UI otimista é mostrar o resultado **antes** da confirmação, apostando que o servidor vai aceitar.

## Como funciona

1. A ação muda o estado da tela na hora.
2. Ao mesmo tempo, o pedido vai ao servidor.
3. Deu certo → nada muda na tela. Deu erro → a tela volta ao estado anterior ou avisa e tenta de novo.

- A mudança pendente fica só na memória da página: fechar a aba antes da confirmação perde o que não subiu.
- Sem rede, o passo 2 falha; a tela não abre nem salva.

## Comparação

| | UI otimista | [[Local-first]] |
|---|---|---|
| a tela atualiza | na hora | na hora |
| a mudança fica | na memória, até o servidor confirmar | no banco do dispositivo |
| fechar a aba offline | perde o pendente | guarda |
| abrir sem internet | não abre | abre e edita |
| conflito | o servidor decide a cada pedido | resolvido ao reconectar ([[CRDT e Yjs]]) |
| custo | estado pendente + desfazer no erro | banco local, sync, fila |

> [!example] No NoteProject
> O editor no [[Navegador|navegador]] fala com o servidor e mostra a edição sem esperar a resposta.

Exemplo de implementação: [TanStack Query, *Optimistic Updates*](https://tanstack.com/query/latest/docs/framework/react/guides/optimistic-updates).
