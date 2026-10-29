---
tags: [noteproject, plano, servidor, dados]
---
# #46 Expose the notes API on the server

Issue do [[M1 Notes in the browser]]: o PR do `notes` põe as rotas `/notes` na [[API de notas]], gravando no [[Postgres]]. O front (cliente da API e proxy `/api` do Vite) é a #62. O `notes` sobe para `0.5.0`. Passou por [[FastAPI]], Python, Postgres, rede e [[TCP]], testes e as notas do vault.

## Rotas

| Rota | Faz | Resposta |
|---|---|---|
| `GET /notes?parent_id=` | lista as notas de uma pasta | 200 |
| `GET /notes/{id}` | lê uma nota | 200, ou 404 |
| `POST /notes` | cria | 201, ou 422 se o pai não existe ou não é pasta |
| `PATCH /notes/{id}` | edita só os campos enviados; `parent_id` move | 200, 404, ou 422 (`title`/`body` nulos, pai inválido, pasta dentro dela mesma) |
| `DELETE /notes/{id}` | apaga | 204, ou 404 |

## FastAPI

- ASGI: a app é uma função `async` que o servidor chama a cada pedido; uvicorn e [[FastAPI]] ficam no mesmo processo, e a conversa entre eles é uma chamada de função, sem rede ([[FastAPI#De onde vem cada parâmetro|FastAPI]]).
- O servidor não conhece as rotas: entrega o caminho como texto, e achar a rota e converter `"7"` em `int` é trabalho da app.
- De onde vem cada parâmetro, decidido uma vez ao registrar a rota: `Depends` → dependência; nome entre chaves → caminho; modelo Pydantic → corpo JSON; tipo simples → query. A type hint converte, e o que não converte vira 422 sem a função rodar.
- Corpo com Pydantic: campo sem valor padrão é obrigatório; erro de formato vira 422 antes da função, erro dentro dela vira 500.
- `Depends` com `yield`: o FastAPI roda `get_conn` até o `yield`, chama a rota com a conexão e depois termina o `with`, que faz `COMMIT` ou `ROLLBACK`. A rota nunca abre nem fecha a conexão.
- Pastas de `src/notes` por papel, um arquivo por recurso: `routers/notes.py` (rotas), `schemas/notes.py` (`Note`, `NoteCreate`, `NoteUpdate`), `errors/notes.py` (uma função por erro, a rota só dá `raise`) ([[API de notas#Pastas dentro de `src/notes`|API de notas]]).

## Python

- O primeiro `import` roda o arquivo inteiro uma vez: `def` só cria o objeto função, e o `@` em cima roda logo depois (`f = X(f)`). Por isso `@router.get(...)` registra a rota ao subir, e arquivo de rotas sem `include_router` dá 404 ([[Módulo Python|módulo]], [[Package Python|package]] e [[venv]]).
- [[Decorator]]: função que recebe uma função e devolve outra; com argumento (`@router.get("/x")`) é uma fábrica que devolve o decorator.
- `with`: `__enter__` na entrada e `__exit__` na saída, sempre, com ou sem erro; `@contextmanager` monta os dois a partir de uma função com `yield` ([[Context manager|with e yield]]).
- uv e uvicorn não têm relação: um instala libs e roda comandos, o outro é o servidor ASGI; o "uv" do uvicorn vem do uvloop.

## Postgres e banco

- Transação: `BEGIN` abre, `COMMIT` grava tudo de uma vez, `ROLLBACK` desfaz tudo; apagar uma pasta e as notas de dentro só vale junto ([[Transação|transação]]).
- `engine.begin()` é um `with` dentro de outro: o de dentro faz `COMMIT` sem erro e `ROLLBACK` com erro; o de fora devolve a conexão ao pool sempre.
- Schema Pydantic e tabela andam juntos sem ser a mesma coisa: coluna nova na [[Migration|migration]] só aparece na API se entrar no modelo e na consulta.

## Rede e TCP

- A conexão TCP é só uma linha numa tabela do sistema operacional de cada ponta; nenhum fio nem roteador sabe dela, e cada pacote viaja sozinho ([[TCP]]).
- O TCP só aparece entre processos: `curl` ⇄ container e API ⇄ Postgres; entre uvicorn e FastAPI é chamada de função ([[Rede de containers|rede de containers]]).

## Testes

- Cada teste roda dentro de uma transação que volta no fim (`rollback`), sobre o banco migrado uma vez por sessão: o [[SQLAlchemy]] abre um savepoint por pedido, e o banco fica limpo entre testes.
- Os testes falam com o Postgres do compose pelo `localhost:5432`: sem o container de pé, todos caem com `Connection refused`.

## Notas do vault

- Plano: o [[Roadmap]] ganhou a busca `/search` (#56) na M1; o [[Navegador]] e a [[API de notas]] separam as rotas `/notes` (#46) e `/search` (#56), com ✅/⏳; [[Features]] recebeu ideias novas (modo de leitura, links dentro das imagens e para um ponto da página, segurança, erros), e a [[Entrega de 2026-11-06]], a linha `mac ipv6 modem firewall`.
- Workspace: branch `<serviço>/<kebab>` e um serviço por branch, com o lint W13, e corpo do PR só `Issue #N` ([[Regras de git]], [[Tarefas no GitHub]]); [[Como usar]] cita os lints W01–W16.
- Conceitos novos ou crescidos: [[Decorator]] e [[Context manager]] (página nova), [[FastAPI]], [[SQLAlchemy]], [[Módulo Python|módulo]], [[Package Python|package]], [[venv]] e [[TCP]], com as figuras do caminho de um pedido, do decorator no import e da transação por pedido.
