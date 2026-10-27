---
tags: [noteproject, ia, arquitetura]
---
# Edição por âncora

A IA leva alguns segundos para responder, e nesse tempo você continua digitando na mesma nota. O `PATCH /notes/{id}` planejado troca o texto inteiro e quem salva por último ganha (o cliente manda o `content` todo).

Se a IA devolvesse a nota inteira, apagaria o que você digitou enquanto ela pensava.

## A ideia

A IA não manda a nota nova. Manda uma **operação** presa a um trecho que já existe, a âncora:

```json
{"op": "inserir_depois", "ancora": "Cayley-Hamilton diz que", "bloco": {"bloco": "nota", "texto": "..."}}
```

| Operação | Faz |
|---|---|
| `inserir_depois` | põe um bloco depois da âncora |
| `substituir` | troca a âncora por texto novo (para `[fix]`) |
| `apagar_marca` | tira o callout da dúvida respondida |

## Como o daemon aplica

1. Procura a âncora no texto **atual** da nota.
2. Achou → guarda a operação como **sugestão**. Você digitou em outro lugar → nada muda.
3. Não achou (você apagou o trecho) → o pedido vira `conflito` e espera você decidir.

No editor, a sugestão aparece destacada no lugar: `Tab` aceita e `Esc` recusa. O texto só entra na nota quando você aceita.

## Por que

- Ninguém perde texto, e isso não depende do [[Yjs]] (M4).
- A IA escreve só o pedaço novo, e a saída é a parte mais cara por token ([[Gastar poucos tokens]]).
- É o "checkpoint humano" do workspace: a IA propõe e você aprova.
- Dá para testar sem IA: uma operação escrita à mão passa pelo mesmo caminho.
