---
id: caddy/add-browser-login-with-a-session-cookie
nome: Caddy manda /api/auth ao nujabes e só deixa notas e chat passarem com sessão (issue #48)
areas: [infra, auth]
---
## Pedido (o que a branch entrega; cada item verificável)
1. `/api/auth/*` → `nujabes:8000`, sem o `/api`.
2. `/api/notes/*` e `/api/chat/*` passam antes por `forward_auth` no `nujabes`
   (`/auth/session`): 401 volta ao navegador; 200 segue com o `X-User-Id` dele. Um `X-User-Id`
   mandado pelo navegador é apagado (conferido no `caddy adapt`: `delete` antes do `set`).

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- Decisão (2026-11-03): `forward_auth` em vez de dependência em cada serviço.

## Fora (vira outra branch)
- O serviço `nujabes`: `nujabes/...`; RLS: `ichiro/...`; repasse: `lonzo/...`; tela: `chimchar/...`.
