---
tags: [noteproject, plano, ia, servidor, infra]
---
# #74 Answer chat questions through the lonzo service

Issue do [[AI in the app]]: nasce o serviço `apps/lonzo` (versão `0.1.0`), em [[Container|container]] próprio, que recebe `POST /api/chat {question}`, pergunta ao Haiku 5.5 com as regras fixas de `rules.md` no `system` e devolve a resposta aos pedaços em [[Server-sent events|SSE]]. Dois PRs: #84 (`lonzo`) e #85 (`caddy`, um prefixo de `/api` por serviço). Passou por [[Chamada a um modelo|chamada a um modelo]], Python, [[FastAPI]], rede, [[Docker Compose|compose]], testes e as notas do vault.

## Chamada a um modelo

- Lib crua `anthropic`, sem Agent SDK: uma request por pergunta, `messages.stream(...)` com `model`, `max_tokens=512`, `system` (o `rules.md`) e a pergunta ([[Chamada a um modelo]]).
- O Haiku 5.5 raciocina por padrão (`thinking` adaptativo), e esse bloco gasta tokens de saída sem aparecer no texto. No primeiro teste, 512 tokens saíram e só ~50 eram texto: a resposta foi cortada (`stop_reason: max_tokens`) antes do `-- lonzo` da regra 2. Com `thinking={"type": "disabled"}`, a mesma pergunta gastou 135 tokens e terminou sozinha (`end_turn`) ([[Gastar poucos tokens]]).
- O `text_stream` da lib entrega só os pedaços de texto (`anthropic/lib/streaming/_messages.py:323`); outro tipo de bloco passa calado.
- Preço do Haiku 5.5 (2026-10-06): $0,10 por milhão de tokens de entrada e $0,50 de saída; uma pergunta curta sai por ~$0,00008.

## Python

- `answer` é um [[Gerador|gerador]] `async`: chamar não roda nada; o `StreamingResponse` pede um item por vez. Ele para no `yield` e no `async for` do stream.
- `async with client.messages.stream(...)` abre a request e garante o fechamento ([[Context manager]]).
- Enquanto o `answer` espera a rede, o event loop atende outras requests no mesmo processo; a ordem em que as tarefas voltam é a ordem em que cada espera termina.

## FastAPI e SSE

- `StreamingResponse(answer(...), media_type="text/event-stream")`: cada `yield` vira um evento nomeado (`message_start`, `text_delta`, `message_end`, `error`) ([[Server-sent events]]).
- Erro da Anthropic depois do 200 só pode sair como evento `error`: o status já foi.
- `status` ficou de fora: só tem o que contar quando houver ferramentas (#77), no tempo em que o `lonzo` roda uma e o modelo não escreve.

## Rede e compose

- O [[Reverse proxy|Caddy]] passou a rotear por prefixo: `/api/notes/*` → `ichiro:8000`, `/api/chat/*` → `lonzo:8000`, cortando o `/api`; outro `/api/*` → 404, nunca o front.
- A `ANTHROPIC_API_KEY` vem do `.env`, mas o [[Docker Compose|compose]] passa só ela ao `lonzo`; ele não vê a senha do [[Postgres]].
- Conferido com `curl -N -k https://notes.localhost/api/chat`: os eventos chegam um a um.

## Testes

- O teste da rota troca o cliente da Anthropic por um falso (`Depends(get_client)` sobrescrito): sem rede e sem gastar tokens.
- `make check` e a CI ganharam o job `lonzo` (ruff, mypy, pytest).

## Notas do vault

- Novas: [[Chat com o workspace]], [[Caminho de uma pergunta]] (com o gif do `answer`), [[Chamada a um modelo]], [[Laço de ferramentas]], [[Sandbox]], [[Gerador]], [[Server-sent events]].
- [[Context manager]] ganhou o `async with`; as [[Regras de resposta]], a regra de explicar palavra-chave com exemplo que roda sozinho.
- Mapa das [[00 Mapa — Issues feitas|issues feitas]]: figuras com os nomes novos e o `lonzo`.
