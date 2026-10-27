---
tags: [noteproject, servidor, auth, cliente-api, decisao]
---
# Navegador

O navegador abre as notas de qualquer computador, sem instalar nada. Quem serve o app e as notas é o servidor, pela internet; sem internet, a página não abre. É o primeiro cliente do projeto ([[Roadmap]], M0–M4). Depois vêm o app desktop, [[Local-first|local-first]] com o [[O daemon notesd|`notesd`]] (milestone Desktop app), e o app do celular.

## Como funciona

1. O servidor entrega o build do front e responde `/api` com as rotas `/notes` e `/search`.
2. A tela usa [[UI otimista]]: a edição aparece na hora e vai ao servidor em seguida.
3. O servidor confirma → nada muda na tela. Recusa ou a rede cai → a tela desfaz ou avisa e tenta de novo.

### Ler as notas

A [[UI otimista]] cobre a escrita; a leitura pede ao servidor só o necessário, uma vez:

| Momento | Pedido (`api.ts`) | O que vem |
|---|---|---|
| abrir o site | `GET /notes/recent` e `GET /notes` | título, pasta e id: poucos KB, mesmo com milhares de notas |
| abrir uma pasta | `GET /notes?parent_id=X` | os filhos da pasta |
| abrir uma nota | `GET /notes/:id` | o texto da nota |

- O que já veio fica num `Map` na memória da aba: voltar a uma pasta ou nota não pede de novo. Fechar a aba ou recarregar apaga esse `Map`, e o primeiro pedido se repete (⏳, hoje cada clique pede ao servidor).
- Mudança feita em outro aparelho só aparece ao recarregar, até o sync (M4) empurrar pelo [[WebSocket]].

![[estrutura-completa.drawio.svg]]
*O navegador entra pelo [[Reverse proxy|Caddy]] como qualquer cliente; o app desktop (milestone Desktop app) passa pelo `notesd`.*

| Peça | O que muda | Estado |
|---|---|---|
| servidor | serve o build do front (`apps/web/dist`), #47 | ⏳ |
| servidor | expõe as rotas `/notes` (#46) e `/search` (#56) que o front vai chamar | ⏳ |
| `apps/web/src/notes/api.ts` | cliente da API: chama `/api` na própria origem, o proxy do Vite repassa | ⏳ |
| front | [[UI otimista]]: estado pendente na tela, desfaz ou tenta de novo se o servidor recusar | ⏳ |
| login | cookie de sessão (httpOnly, mesma origem), #48 | ⏳ |
| busca | a busca full-text do [[Postgres]] ([doc](https://www.postgresql.org/docs/current/textsearch.html)) | ⏳ |
| IA | worker da [[Fila de pedidos\|fila]] no servidor; o navegador só pede e mostra a proposta ([[Workspace no app]]) | ⏳ |

- O `api.ts` será a única fronteira de rede do front: quando o app desktop vier, o [[O daemon notesd|`notesd`]] responde o mesmo contrato e a tela não muda.
- Cookie no navegador porque ele já guarda e envia sozinho; o [[Token por dispositivo|token por dispositivo]] fica para o app desktop, que não tem sessão de navegador.

## Por que não SQLite em WASM

A outra saída é o navegador virar um dispositivo [[Local-first|local-first]]: um "`notesd` em TS" dentro da página, com o [[SQLite]] compilado em [[WebAssembly|WASM]] guardando as notas no navegador.

| | [[UI otimista]] | SQLite em WASM |
|---|---|---|
| navegador fala com | servidor, pela internet | uma cópia local dentro da página |
| sem internet | não abre | funciona |
| tela ao editar | na hora | na hora |
| fechar a aba com edição pendente | perde o que não subiu | guarda |
| custo | estado pendente + desfazer no erro | lógica local escrita duas vezes (Python e TS) + Service Worker + sync no navegador |

A [[UI otimista]] é bem mais simples de implementar, e o navegador funcionar sem internet não é requisito: o uso offline fica no app desktop. A IA reforça a escolha: o worker roda no servidor e lê as notas do [[Postgres]]; com WASM, haveria duas cópias para manter iguais já na v1.

> [!warning] Em aberto com o sync (#26)
> Com o [[Yjs]], a nota no servidor vira um documento CRDT. Um `PATCH` com o texto inteiro vindo do navegador pode apagar o que outro dispositivo acabou de mandar. Saídas: o navegador editar pelo [[WebSocket]] do sync (online, sem guardar nada) ou o servidor transformar o `PATCH` em update [[Yjs]]. Decidir junto com onde mora o documento ([[Back — daemon e servidor]]).

## Revisar se...

- a edição pendente perdida ao fechar a aba incomodar, ou o uso no navegador precisar de offline → SQLite em WASM;
- quando o app desktop vier, manter o contrato igual nos dois lados der trabalho demais → o app desktop também falar direto com o servidor e o `notesd` virar só cache offline.
