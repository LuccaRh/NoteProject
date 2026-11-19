---
tags: [noteproject, servidor]
---
# Erros nos serviços

Os serviços Python (`ichiro`, `lonzo`) seguem as camadas `routers/` → `services/` → `clients/` ou `repositories/`. Cada camada tem um papel no [[Tratamento de erros|tratamento de erros]], e a ordem dos passos dentro de um service segue as regras de [[Falha parcial]]. Tudo ✅, conferido no código em 2026-11-12.

## Uma tradução por andar

| Andar | O que faz com o erro | No código |
|---|---|---|
| Repository | traduz o erro do banco para um do domínio | `integrity_error` troca o `UniqueViolation` do [[Postgres]] por `TitleTaken` (`apps/ichiro/src/ichiro/repositories/notes.py:25`) |
| Client | traduz a resposta da outra API para um erro do domínio | 409 do `ichiro` → `TitleTaken` (`apps/lonzo/src/lonzo/clients/ichiro.py:210`); `AuthenticationError` da Anthropic → `InvalidApiKey`, com `from error` (`clients/anthropic.py:92`) |
| Service | lança o erro da regra | `check_model` lança `InvalidSettings` (`services/settings.py:101`) |
| Router | não pega nada | o erro passa direto |
| Handler | traduz o erro do domínio para status HTTP | tabela `STATUS` (`apps/lonzo/src/lonzo/core/handlers.py:22`): `TitleTaken` 409, `InvalidSettings` 422, `APIError` 502; `httpx2.HTTPError` (o `ichiro` fora do ar) → 502 (`:51`) |

- O que não está em nenhuma tabela é bug: o [[FastAPI]] responde 500 e o traceback vai para o log.
- `TitleTaken` existe nos dois serviços: no `ichiro` nasce do banco, no `lonzo` nasce do 409 do `ichiro`. Cada serviço fala a língua do próprio domínio.

## Ordem no `save_settings`

`apps/lonzo/src/lonzo/services/settings.py:123`, na ordem em que roda:

| Linha | Passo | Se falhar aqui, sobra |
|---|---|---|
| `:130` | `load_stored()` lê o que está salvo | nada |
| `:131-137` | calcula `changed`, sem rede | nada |
| `:139-141` | só se algo mudou: `list_models` na API da Anthropic, depois `check_model` | nada; a chave recusada vira 422 |
| `:146-148` | cifra a chave nova, local | nada |
| `:150-160` | `async with transaction()`: um `upsert` só | nada; o `ROLLBACK` desfaz |

- A chamada externa (lenta, pode cair) fica **antes** da [[Transação|transação]]: a conexão do pool só é pega para o `upsert`.
- A checagem vem antes da escrita: chave ou modelo inválido nunca chegam ao banco.
- Uma escrita, num banco só: não existe falha parcial neste service.

## Revisar se...

- Um service passar a escrever em dois serviços (`ichiro` e banco do `lonzo`) no mesmo pedido: aí a ordem decide a sobra, e pode precisar de idempotência ou compensação ([[Falha parcial]]).
- O client do `ichiro` ganhar repetição automática: só para pedidos idempotentes (`GET`, `PUT`), nunca para `POST /notes`.
