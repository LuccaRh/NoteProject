---
tags: [noteproject, conceito, cliente-api]
---
# CORS

Uma página aberta no navegador roda código de quem a escreveu. Se esse código pudesse chamar qualquer site com os cookies do usuário, um site malicioso leria o e-mail ou o banco de quem o abrisse. Por isso o navegador segue a **política da mesma origem**: o JavaScript de uma página só lê respostas da mesma origem dela.

CORS (*Cross-Origin Resource Sharing*) é a exceção combinada: o servidor de outra origem diz, por cabeçalho, quais origens podem ler as respostas dele.

## Origem

Origem = esquema + host + [[Porta|porta]]. Basta uma das três mudar para a origem ser outra.

| Página em `http://localhost:5173` chama | Mesma origem? | Por quê |
|---|---|---|
| `http://localhost:5173/api/notes` | sim | tudo igual |
| `http://localhost:8000/notes` | não | porta diferente |
| `https://localhost:5173/` | não | esquema diferente |
| `http://127.0.0.1:5173/` | não | host diferente, mesmo sendo a mesma máquina |

## Como o navegador decide

1. O código da página faz `fetch('http://localhost:8000/notes')`.
2. O navegador manda o pedido com o cabeçalho `Origin: http://localhost:5173`.
3. O servidor responde. Se a resposta traz `Access-Control-Allow-Origin: http://localhost:5173` (ou `*`), o navegador entrega a resposta ao código.
4. Sem esse cabeçalho, o navegador **joga a resposta fora** e o `fetch` falha com erro de CORS no console.

- Quem bloqueia é o navegador, não o servidor: o pedido chegou e foi atendido. `curl` e Python não têm essa regra e leem tudo.
- Pedido que pode mudar algo (`PATCH`, `DELETE`, JSON no corpo) vai antes com um **preflight**: um `OPTIONS` perguntando se pode. O pedido de verdade só sai se o servidor responder que sim.

```http
OPTIONS /notes/42 HTTP/1.1
Origin: http://localhost:5173
Access-Control-Request-Method: PATCH
Access-Control-Request-Headers: content-type
```

```http
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: http://localhost:5173
Access-Control-Allow-Methods: GET, POST, PATCH, DELETE
Access-Control-Allow-Headers: content-type
```

## Dois jeitos de resolver

| | Liberar CORS no servidor | Ficar na mesma origem |
|---|---|---|
| Como | middleware que escreve os cabeçalhos (no [[FastAPI]], `CORSMiddleware`) | um intermediário serve front e api no mesmo endereço: [[Proxy de desenvolvimento\|proxy do servidor de desenvolvimento]], [[Reverse proxy\|reverse proxy]] em produção |
| Pedido a mais | preflight antes de cada `PATCH`/`DELETE` (o navegador guarda a resposta por um tempo) | nenhum |
| Cookie de login | precisa de `credentials: 'include'`, `Allow-Credentials` e origem exata, sem `*` | vai sozinho |
| Quando faz sentido | api pública chamada por sites de outros donos | front e api do mesmo dono |

> [!warning] Erros comuns
> - `Access-Control-Allow-Origin: *` junto com cookie não funciona: o navegador exige a origem escrita por extenso.
> - Erro de CORS esconde o erro real: um 500 sem os cabeçalhos aparece no console como CORS. Olhar a aba Network ou o log do servidor.
> - CORS não protege o servidor: qualquer programa fora do navegador chama a api. Quem protege é o login.

Docs: [MDN — CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS), [MDN — Same-origin policy](https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy).
