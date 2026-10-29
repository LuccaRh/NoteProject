---
tags: [noteproject, conceito, ui, cliente-api]
---
# Promise

O JavaScript da página roda numa linha só: se ele parasse esperando a rede, a tela congelaria. Por isso, quem demora (um `fetch`, um timer) devolve na hora uma Promise, um valor que vai chegar depois, e o código segue. Quando a resposta chega, quem estava esperando continua.

## Estados

| Estado | Quando |
|---|---|
| pendente | o pedido saiu e a resposta não voltou |
| cumprida | chegou o valor |
| rejeitada | deu erro (rede fora, status de erro tratado como exceção) |

## Esperar o valor

```ts
// com await: só dentro de função async
async function load() {
    const notes = await listNotes(null)   // pausa aqui até chegar
    render(notes)
}

// com .then: em qualquer lugar
listNotes(null).then(notes => render(notes))
```

- Uma função `async` sempre devolve uma Promise, mesmo sem `return`.
- `await` é o mesmo do Python (`asyncio`), com uma diferença: no JS a Promise começa a rodar ao ser criada, mesmo que ninguém faça `await`; no Python a corrotina só anda quando alguém espera por ela.
- `p.then(f)` também devolve uma Promise. Encadear `fila = fila.then(proximo)` põe as tarefas uma atrás da outra, nunca duas ao mesmo tempo.

## Erros

- Rejeição se trata com `try { await p } catch { ... }` ou `p.catch(f)`.
- Rejeição que ninguém trata dispara o evento `unhandledrejection` na janela; um ouvinte dele é o último lugar para mostrar "servidor fora".
- `void p` diz "não vou esperar esta Promise aqui, de propósito". Ela roda igual; o erro, se vier, vai para o `unhandledrejection`.

> [!warning] Erros comuns
> - Esquecer o `await`: a variável fica com a Promise, não com o valor (`notes.length` vira `undefined`).
> - `await` fora de função `async`: erro de sintaxe (salvo no topo de um módulo).

> [!example] No NoteProject
> Abrir o app chama `void tree.load(null).then(...)`, que apaga o "Loading" quando a lista chega ([[Como ler o front]]).

Docs: [MDN — Using promises](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Using_promises).
