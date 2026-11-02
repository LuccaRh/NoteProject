---
tags: [noteproject, prova, servidor]
---
# Questões de Python e FastAPI

O que roda dentro do `ichiro` ([[API de notas]], [[Issue 10 — Scaffold the server with a health endpoint|#10]], [[Issue 46 — Expose the notes API on the server|#46]]).

## 1. Um pedido chega ao processo do `ichiro`. Diga o papel do uvicorn, do Starlette e do [[FastAPI]].

> [!note]- Resposta
> O uvicorn abre a porta e chama a app (servidor ASGI). O Starlette acha a rota pelo caminho. O [[FastAPI]] valida e converte os parâmetros pela type hint e chama a função ([[Issue 10 — Scaffold the server with a health endpoint|#10]]).

## 2. Na rota `@router.get("/{note_id}")` com `def read(note_id: int, conn: Connection = Depends(get_conn))`, chamada como `GET /notes/7?x=1`, de onde vem cada parâmetro?

> [!note]- Resposta
> `note_id` vem do caminho (nome entre chaves), convertido de `"7"` para `7`. `conn` vem da dependência. O `x` da query é ignorado: não há parâmetro com esse nome. Modelo Pydantic viria do corpo; tipo simples fora do caminho, da query ([[FastAPI#De onde vem cada parâmetro|FastAPI]]).

## 3. E `GET /notes/abc`?

> [!note]- Resposta
> 422 sem a função rodar: `"abc"` não converte em `int` ([[FastAPI]]).

## 4. Erro de formato no corpo dá 422. E um erro dentro da função?

> [!note]- Resposta
> 500. O 422 vem da validação antes da função; o que a função levanta sem tratar vira 500 (por isso o `errors/notes.py` dá o 404 de propósito) ([[Issue 46 — Expose the notes API on the server|#46]]).

## 5. Uma rota `async def` chama uma função bloqueante (um `time.sleep` ou um driver de banco síncrono). O que acontece com os outros pedidos?

> [!note]- Resposta
> Esperam: `async def` roda no event loop, e a chamada bloqueante trava o processo inteiro. Com `def`, a rota vai para uma thread do pool. Na dúvida, `def` ([[FastAPI]]).

## 6. Um arquivo novo `routers/search.py` tem `@router.get("/notes/search")`, mas `GET /notes/search` dá 404. O que faltou, e por quê?

> [!note]- Resposta
> O `include_router` no `main.py`. O `@` só registra a rota quando o arquivo é importado; sem o import pelo `main.py`, o arquivo nunca roda ([[Módulo Python]], [[Decorator]]).

## 7. Reescreva sem `@`: `@router.get("/x")` em cima de `def f(): ...`.

> [!note]- Resposta
> `f = router.get("/x")(f)`. `router.get("/x")` é uma fábrica: devolve o decorator, que recebe `f` ([[Decorator]]).

## 8. Em que ordem roda o código, numa rota que recebe `conn` de `get_conn`?

```python
def get_conn() -> Iterator[Connection]:
    with engine.begin() as conn:
        yield conn
```

> [!note]- Resposta
> 1. O FastAPI roda `get_conn` até o `yield`: pega uma conexão do pool e abre a transação.
> 2. Chama a rota com a conexão.
> 3. Volta a `get_conn` e termina o `with`: `COMMIT` se a rota não deu erro, `ROLLBACK` se deu, e a conexão volta ao pool.
>
> A rota nunca abre nem fecha a conexão ([[Context manager]], [[SQLAlchemy]], `apps/ichiro/src/ichiro/db.py`).

## 9. O que o `with` garante, e em que dois métodos isso se apoia?

> [!note]- Resposta
> A saída roda sempre, com ou sem erro: `__enter__` na entrada, `__exit__` na saída. O `@contextmanager` monta os dois a partir de uma função com `yield` ([[Context manager]]).

## 10. Por que o `ichiro` usa a estrutura `src/` e não a plana?

> [!note]- Resposta
> O código é achado de um jeito só, como package instalado no `.venv` (um `notes.pth` aponta para `src/`): no teste, no `fastapi dev` e na imagem. Todo import começa por `notes.`, sem colidir com libs ou outros serviços. Na plana, o import depende da pasta atual ([[API de notas]], [[Package Python]], [[sys.path]]).

## 11. Verdadeiro ou falso: o `uv` e o `uvicorn` são da mesma família de ferramentas.

> [!note]- Resposta
> Falso. O [[uv]] instala libs e roda comandos; o uvicorn é o servidor ASGI, e o "uv" do nome vem do uvloop ([[Issue 46 — Expose the notes API on the server|#46]]).

## 12. O que o `uv sync` faz com o `pyproject.toml`, o `uv.lock` e o `.venv`?

> [!note]- Resposta
> O `pyproject.toml` é o pedido; o `uv.lock` fixa as versões exatas; o `uv sync` deixa o `.venv` igual ao lock ([[uv]], [[venv]]).
