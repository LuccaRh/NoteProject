---
id: lonzo/add-browser-login-with-a-session-cookie
nome: Chat preso às notas e conversas do usuário (issue #48)
areas: [ia, auth]
---
## Pedido (o que a branch entrega; cada item verificável)
1. Middleware lê o `X-User-Id` do Caddy numa contextvar; sem ele, 401 (menos `/health`).
2. Toda chamada ao `ichiro` leva o `X-User-Id` (event hook do `httpx2`): as ferramentas do chat
   ficam presas às notas do usuário pelo RLS do `ichiro`.
3. Migration: `owner_id` em `conversations`, policies em `conversations` e `messages`, `FORCE`
   (o `lonzo` é dono das tabelas). Conversas que já existem: `alembic -x owner=<id> upgrade head`.
4. Testes: um usuário não lista nem abre a conversa do outro; sem usuário → 401.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- Nota `Estrutura do projeto/RLS ou filtro em cada consulta`; card `httpx2` (event hooks).

## Fora (vira outra branch)
- `forward_auth` no `/api/chat`: `caddy/...`. Uma chave da Anthropic por usuário.
- Migration futura que mexa em linhas do `lonzo` roda sob o RLS (sem usuário, vê nada).
