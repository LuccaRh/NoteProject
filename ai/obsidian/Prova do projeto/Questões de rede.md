---
tags: [noteproject, prova, infra]
---
# Questões de rede

O caminho de um pedido do navegador até o [[Postgres]], no compose de dev (#16) e no plano da [[EC2]] ([[Rede do servidor]]).

## 1. Descreva, passo a passo, o caminho de `https://notes.localhost/api/notes/7` até a rota do `ichiro`.

> [!note]- Resposta
> 1. `*.localhost` vira `127.0.0.1` sem `/etc/hosts`.
> 2. O navegador abre [[TCP]] em `127.0.0.1:443`, publicada no container `caddy`.
> 3. O [[Reverse proxy|Caddy]] faz o [[TLS]] com o certificado da CA local dele (`tls internal`).
> 4. O caminho bate com `@ichiro` (`/api/notes/*`); `uri strip_prefix /api` tira o `/api` e repassa a `ichiro:8000/notes/7` pela [[Rede de containers|rede do compose]].
> 5. O uvicorn entrega o pedido ao [[FastAPI]], que acha a rota `GET /notes/{id}`.
>
> Fonte: `caddy/Caddyfile`, `docker-compose-dev.yml`.

## 2. Por que o `api.ts` chama `'/api/notes'` e não `'http://localhost:8000/notes'`?

> [!note]- Resposta
> - [[URL relativa]]: o navegador completa com a origem da página, e front e api ficam na mesma origem, sem [[CORS]].
> - `localhost:8000` seria outra origem (porta diferente) e, além disso, o `ichiro` nem publica porta: só o Caddy chega nele.

## 3. Quais destas URLs têm a mesma origem que `https://notes.localhost/`? `https://notes.localhost/api/notes`, `http://notes.localhost/`, `https://notes.localhost:8443/`, `https://127.0.0.1/`.

> [!note]- Resposta
> Só a primeira. Origem = esquema + host + [[Porta|porta]]; nas outras muda o esquema, a porta e o host ([[CORS]]).

## 4. O `Dockerfile.dev` do `ichiro` roda `fastapi dev ... --host 0.0.0.0`. Sem o `--host`, o Caddy alcançaria o container?

> [!note]- Resposta
> Não. Sem ele, `fastapi dev` escuta em `127.0.0.1`, o loopback do próprio container; o pedido do Caddy chega pelo IP do container na rede do Docker ([[Porta#Endereço de escuta|endereço de escuta]], [[Rede de containers]], [[API de notas]]).

## 5. O compose publica o Postgres em `127.0.0.1:5432:5432`. Um notebook no mesmo Wi-Fi conecta nele? E o pytest rodando no host?

> [!note]- Resposta
> O notebook não: a porta só existe no loopback do host. O pytest sim, por `localhost:5432` ([[Rede]], [[Issues 12 e 13 — Postgres com migrations e .env|#12]]).

## 6. Dentro do container `ichiro`, a `ICHIRO_DATABASE_URL` aponta para `localhost:5432`. O que acontece?

> [!note]- Resposta
> `Connection refused`: dentro do container, `localhost` é o próprio container. O host certo é `postgres`, o nome do serviço, que o DNS do Docker resolve ([[Rede de containers]]).

## 7. Verdadeiro ou falso: entre o uvicorn e o FastAPI há uma conexão TCP.

> [!note]- Resposta
> Falso. Os dois estão no mesmo processo, e a conversa é uma chamada de função (ASGI). [[TCP]] aparece entre processos: navegador ⇄ Caddy, Caddy ⇄ `ichiro`, `ichiro` ⇄ [[Postgres]] ([[Issue 46 — Expose the notes API on the server|#46]]).

## 8. Onde "mora" uma conexão TCP aberta?

> [!note]- Resposta
> Numa linha da tabela do sistema operacional de cada ponta. Nenhum fio nem roteador sabe dela; cada pacote viaja sozinho e o [[Roteamento|roteamento]] decide só o próximo pulo ([[TCP]]).

## 9. O navegador avisa que o certificado de `notes.localhost` não é confiável. Por quê, e o que resolve?

> [!note]- Resposta
> O certificado foi assinado pela CA local do Caddy, que só é confiável na máquina que a instalou. Resolve instalar essa CA (guardada no volume `caddy_data`) no navegador ou no sistema ([[TLS]]).

## 10. No ar, quais portas o [[Security Group]] abre, e por que a 80 fica fechada?

> [!note]- Resposta
> Só a 443. O app sempre chama `https`/`wss`, e o Let's Encrypt valida o domínio pela 443 (desafio TLS-ALPN). As portas do `api`, do `sync` e do [[Postgres]] nem são publicadas na [[EC2]] ([[Rede do servidor]]).

## 11. Por que HTTPS de verdade precisa de um [[Domínio|domínio]], e não só do IP da [[EC2]]?

> [!note]- Resposta
> O certificado liga um nome a uma chave, não um IP; o Let's Encrypt confere que quem pede controla o nome ([[TLS]], [[Domínio]]).
