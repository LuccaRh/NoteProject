---
pacote: httpx2
versao: 2.16.0
fonte: apps/lonzo/.venv/lib/python3.14/site-packages/httpx2/
areas: [ia, servidor]
---
# httpx2 — cliente HTTP do lonzo para o ichiro

Card destilado do código instalado (fonte acima, linhas citadas). Fork da `httpx` com a mesma
API; é a que a `anthropic` 2.3.0 (`anthropic/_base_client.py:40`) e o `TestClient` do Starlette
(`starlette/testclient.py:26`) importam. A `httpx` 0.28.1 também está no venv, mas só pelo
`fastapi-cli`; misturar as duas quebra o mypy (`Response` de uma não é a da outra).

## Cliente (`_client.py`)
- `httpx2.AsyncClient(base_url=, transport=)` (1401): `async with` fecha as conexões no fim.
- `await client.get(url, params=)`, `await client.post(url, json=)` devolvem `Response`.
- `AsyncClient(event_hooks={"request": [hook]})` (190): `await hook(request)` antes de cada
  envio (1877); no async o hook tem de ser `async`. O lonzo põe o `X-User-Id` assim.
- `response.raise_for_status()` (`_models.py:794`): 4xx/5xx viram `HTTPStatusError`.

## Erros (`_exceptions.py`)
- `HTTPError` (85): base de tudo (status e rede); o lonzo responde 502 para ela.
- `ConnectError` (198): o serviço do outro lado não atende.

## Testes (`_transports/mock.py`)
- `MockTransport(handler)` (15): `handler(request) -> Response`, síncrono ou async; o cliente
  com esse transporte nunca abre conexão. É o `FakeIchiro` dos testes do lonzo (`tests/fakes.py`).
