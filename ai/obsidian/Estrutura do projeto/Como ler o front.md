---
tags: [noteproject, ui, cliente-api, editor]
---
# Como ler o front

O código de `apps/web/` tem ~1000 linhas, e a maior parte é CSS. A ordem abaixo vai do formato da nota que vem do servidor até a tela, e cada passo responde uma pergunta. As linhas são da branch da #62.

| # | Arquivo | O que olhar | Pergunta |
|---|---|---|---|
| 1 | `index.html` | o arquivo inteiro, um comentário por bloco | Que pedaços a tela tem? (`#tree`, `#title`, `#editor`, `#save-status`) |
| 2 | `src/notes/api.ts` | `type Note` (:5), `request` (:31), as 5 funções (:46–77) | Como o front fala com `/api/notes`? É o espelho das rotas da [[API de notas]] |
| 3 | `src/main.ts` | `new Page` (:13), `new Tree` (:22), `byId` (:31), `rename`/`remove`/`create` (:41–70) | Quem chama quem? |
| 4 | `src/notes/page.ts` | `SAVE_DELAY_MS` (:20), `RETRY_MS` (:23), `change` (:89), `flush` (:100), `save` (:112) | Como a nota aberta salva sozinha? |
| 5 | `src/notes/tree.ts` | `Handlers` (:8), `load` (:51), `click` (:236) | Como a lista abre pastas sob demanda e devolve os cliques para o `main.ts`? |
| 6 | `src/editor.ts` | `type Editor` (:9), `createEditor` (:43) | O que o [[CodeMirror]] entrega para o `Page`? |
| 7 | `src/style.css` | só ao mexer no visual | — |

## Como as peças se ligam

- **HTML → `main.ts`**: o `index.html` carrega o `main.ts` pela última linha (`<script type="module">`); o [[Servidor de desenvolvimento|Vite]] converte o TypeScript para JS. O `main.ts` acha cada pedaço da tela no [[DOM]] pelo `id`, com `byId`, que para tudo com `missing #<id>` se o HTML perder um.
- **`main.ts` → `Page` e `Tree`**: o `main.ts` cria os dois e é o único que conhece ambos; a `Tree` avisa os cliques por `Handlers`, três [[Callback|callbacks]] (abrir, renomear, apagar), e o `Page` avisa quando salvou, para a lista atualizar o título.
- **A lista aparece**: `tree.load(null)` busca só o que está direto na raiz e guarda em `children`; o `render` troca os `<li>` de dentro do `<ul id="tree">` pelos que o `rows` monta a partir de `children`.
- **`Page` e `Tree` → `api.ts`**: toda chamada à rede passa por `request`, que manda para `/api/notes`; no dev, o [[Proxy de desenvolvimento|proxy do Vite]] repassa ao serviço `notes`.
- **Salvar sozinho**: cada tecla junta o campo mudado em `dirty` e reinicia um timer de 600 ms; quando o timer vence, `flush` põe o `save` numa fila de [[Promise|Promises]] (um por vez) e manda um `PATCH`; se falhar, os campos voltam para `dirty` e tenta de novo em 3 s.
- **Sintaxe**: os cliques viram [[Arrow function|arrow functions]] (`note => page.open(...)`), e o `void` antes de uma chamada `async` diz que ninguém espera aquela [[Promise]] ali.

## A lista: cache e recursão

- **`children`** é um `Map<string, Note[]>` (como um `dict[str, list[Note]]`): para cada pasta já buscada, as notas de dentro dela. A raiz chega da API como `null` e vira a chave `'root'` (`parentId ?? ROOT`, [[Nullish coalescing]]); o pedido à API continua indo com `null`.
- **Cache**: uma pasta só é buscada no primeiro clique (`load(id)`); fechar e abrir de novo não pede nada, porque a lista dela continua em `children`. Fechar a pasta só tira o id de `expanded` (um `Set` das pastas abertas).
- **`rows` é recursivo**: para cada nota da pasta monta um `<li>`; quando a nota é uma pasta aberta, chama a si mesmo para os filhos, com `depth + 1`, e eles entram logo abaixo dela. Pasta que ainda não está em `children` conta como vazia (`?? []`).
- **`render`** junta tudo com `replaceChildren(...this.rows(null, 0))`: o [[Spread|spread]] passa cada `<li>` como um argumento.

```
children                              tela (rows)
'root'      → [Work, Inbox]           Work          depth 0  (aberta)
'<id Work>' → [Todo]                    Todo        depth 1
                                      Inbox         depth 0
```

## Ao ler

- Abrir com a app rodando (`make dev` e o serviço `notes` no ar) e a aba **Network** do navegador aberta: cada clique vira uma chamada de `api.ts`.
- No passo 4, digitar e parar: o `PATCH` sai ~600 ms depois.
- Toda função tem uma descrição `/** ... */` em cima; passar o mouse no nome mostra o texto no editor.
