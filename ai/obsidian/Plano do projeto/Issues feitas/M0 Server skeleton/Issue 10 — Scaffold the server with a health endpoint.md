---
tags: [noteproject, plano, servidor]
---
# #10 Scaffold the server with a health endpoint

Issue do [[M0 Server skeleton]]. Cria `apps/notes`, a API com só `GET /health`, testada no `make check` e no [[CI e CD|CI]]. Passou por [[FastAPI]], Python e testes.

## FastAPI

- WSGI × ASGI: o uvicorn abre a porta e chama a app; o Starlette acha a rota; o [[FastAPI]] valida pela type hint (erro vira 422 sem a função rodar).
- Concorrência: no Django clássico, um pedido por worker; no FastAPI com `await`, centenas de esperas de I/O num processo só.
- `async def` roda no event loop; `def` vai para uma thread do pool. Chamada bloqueante dentro de `async def` trava o processo inteiro; na dúvida, `def`.
- `fastapi dev` escuta em `127.0.0.1` (só a própria máquina) e recarrega; `fastapi run` escuta em `0.0.0.0` e não recarrega.

## Python

- O `import` não aceita caminho: procura o primeiro nome no primeiro nível de cada pasta do `sys.path`, e a primeira que tiver vence ([[Python — módulo, package e venv|módulo, package e venv]]).
- venv = um Python com `site-packages` próprio; o `uv sync` instala nele o que o `uv.lock` fixa.
- Package é o formato; biblioteca é package feito para outros importarem; serviço é programa que roda e ninguém importa.
- Estrutura `src/` em vez de plana: o serviço é instalado no `.venv` (um `notes.pth` aponta para `src/`), e todo import começa por `notes.` ([[API de notas]]).

## Testes

- Quebrar o teste de propósito (esperar 201) e ver o `make check` falhar prova que o alvo está ligado.
