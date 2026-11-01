---
tags: [noteproject, prova]
---
# Questões do projeto

O plano e as decisões grandes: o que é a v1, por que nessa ordem e como o [[Navegador|navegador]] fala com o servidor.

## 1. O que a v1 entrega, e o que fica de fora?

> [!note]- Resposta
> Ler e navegar notas `.md` organizadas, com links, no navegador, com as notas num servidor na AWS. Fica de fora a IA, que entra depois, já dentro do app ([[Objetivo do app]], [[Workspace no app]]).

## 2. Rodar o servidor em localhost já resolveria o uso diário no fim da M1. Por que a v1 só fecha na M3?

> [!note]- Resposta
> O motivo 1 do projeto (aprender servidor, banco, login, [[TLS]], deploy) vem antes do uso diário. Com o servidor na internet, login e HTTPS viram obrigatórios, e isso só existe depois da M2 e da M3 ([[Objetivo do app]], [[Roadmap]]).

## 3. Ordene os três clientes e diga qual deles é local-first.

> [!note]- Resposta
> Navegador → app desktop → celular. O [[Local-first|local-first]] é o app desktop, com o [[O daemon notesd|`notesd`]] dono do [[SQLite]] do dispositivo; o navegador fala direto com o servidor, só online ([[Navegador]]).

## 4. Verdadeiro ou falso: sem internet, a página do navegador abre e mostra as notas já vistas.

> [!note]- Resposta
> Falso. O servidor serve o app e as notas; sem internet, a página não abre. O `Map` em memória só evita pedir de novo dentro da mesma aba ([[Navegador]]).

## 5. Por que o navegador usa [[UI otimista]] e não [[SQLite]] em [[WebAssembly|WASM]]?

> [!note]- Resposta
> - A [[UI otimista]] só pede estado pendente e desfazer no erro.
> - O WASM pediria a lógica local escrita duas vezes (Python e TS), Service Worker e sync no navegador.
> - Offline não é requisito do navegador: fica no desktop.
> - A IA roda no servidor e lê o [[Postgres]]; com WASM, haveria duas cópias para manter iguais já na v1 ([[Navegador]]).

## 6. Qual o custo aceito com a [[UI otimista]]?

> [!note]- Resposta
> Fechar a aba com edição pendente perde o que não subiu ([[Navegador]], tabela "Por que não SQLite em WASM").

## 7. Para que serve ter o `apps/chimchar/src/notes/api.ts` como a única porta de rede do front?

> [!note]- Resposta
> Quando o app desktop vier, o [[O daemon notesd|`notesd`]] responde o mesmo contrato, e a tela não muda ([[Navegador]], [[Front — editor e UI]]).

## 8. No navegador o login é por cookie; no app desktop, por [[Token por dispositivo|token por dispositivo]]. Por que a diferença?

> [!note]- Resposta
> O navegador já guarda e manda o cookie sozinho (httpOnly, mesma origem). O app desktop não tem sessão de navegador, então guarda um token e o manda em todo pedido ([[Navegador]], [[Token por dispositivo]]).

## 9. Qual o problema em aberto entre o `PATCH` do navegador e o sync com [[Yjs]] (#26)?

> [!note]- Resposta
> Com o [[Yjs]], a nota no servidor vira um documento [[CRDT]]. Um `PATCH` com o texto inteiro pode apagar o que outro dispositivo acabou de mandar. Saídas: o navegador editar pelo [[WebSocket]] do sync, ou o servidor transformar o `PATCH` em update Yjs ([[Navegador]], [[Roadmap]] M4).

## 10. Por que o projeto tem duas trilhas, e quem escreve cada uma?

> [!note]- Resposta
> A principal (dados, servidor, auth, infra, sync) é escrita à mão, com o conceito antes, porque é o que se quer aprender. A do editor (editor, ui, cliente-api) é gerada e revisada no PR ([[Roadmap]]).
