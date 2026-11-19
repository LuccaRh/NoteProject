---
tags: [noteproject, auth, infra]
---
# Login e gateway

Antes do login, qualquer um com acesso ao servidor via tudo. O login entrou como um serviço próprio, o `nujabes`, e o [[Reverse proxy|Caddy]] confere a sessão antes de deixar o pedido chegar a notas ou chat. Caminho completo, com desenho, em [[Login no navegador]].

![[login-no-navegador.drawio.svg]]
*Login grava o cookie; cada pedido depois passa pelo `forward_auth` do Caddy, que pergunta ao `nujabes` quem é o dono.*

## O `nujabes`

| Rota | Faz |
|---|---|
| `POST /auth/login` | confere email e senha; cria sessão; devolve o token num [[Cookie\|cookie]] |
| `GET /auth/session` | 200 com `X-User-Id` se o cookie é de uma sessão aberta; 401 se não |
| `POST /auth/logout` | apaga a sessão e o cookie |

- Senha: `crypt(senha, gen_salt('bf'))` do `pgcrypto` = bcrypt, com salt e custo ([[Hash de senha]]). Login confere com `password_hash = crypt(:senha, password_hash)`.
- Token: `secrets.token_urlsafe(32)` (256 bits). No banco só fica `digest(token, 'sha256')`: a tabela vazada não loga ninguém.
- Hash rápido (SHA-256) basta no token porque ele já é aleatório e longo; senha precisa de hash lento porque é curta e adivinhável.
- Sessão dura 30 dias (`expires_at` com default `now() + interval '30 days'`); [[Sessão de login]] guardada no servidor, então logout invalida na hora.
- Cookie `HttpOnly` (JS não lê, protege de XSS), `Secure` (só HTTPS), `SameSite=Lax` (não vai em `POST` vindo de outro site, protege de CSRF).
- Usuário é criado à mão no psql; não existe cadastro.

## O Caddy como gateway

```caddy
(logged_in) {
    forward_auth nujabes:8000 {
        uri /auth/session
        copy_headers X-User-Id
    }
}
@ichiro path /api/notes /api/notes/*
handle @ichiro {
    import logged_in
    uri strip_prefix /api
    reverse_proxy ichiro:8000
}
```

- [[Forward auth]]: para cada pedido de notas ou chat, o Caddy faz um subpedido ao `nujabes` com os cookies. 401 volta ao navegador; 200 segue com o `X-User-Id`.
- `copy_headers` sobrescreve um `X-User-Id` que o navegador tenha mandado: o cliente não consegue se passar por outro.
- `strip_prefix /api`: os serviços não sabem do `/api`; `/api/notes/x` chega como `/notes/x`.
- `/api/*` sem dono → 404, nunca o front.
- Os serviços só leem o cabeçalho (middleware `read_user`, 401 sem um UUID válido, exceto `/health`).

## Se perguntarem

- **"Por que sessão no banco e não JWT?"** Logout e revogação imediatos, sem lista negra; o custo (uma consulta por pedido no `nujabes`) é irrelevante nessa escala. JWT vale quando muitos serviços precisam validar sem ir a um lugar central.
- **"Qual a fraqueza?"** Os serviços confiam no `X-User-Id`: quem estiver dentro da rede do compose pode forjá-lo. Mitigação: só o Caddy tem porta exposta; melhoria: o gateway assinar o usuário (JWT curto ou mTLS entre serviços).
- **"Rate limit no login?"** Ainda não tem; bcrypt deixa cada tentativa cara, mas falta limitar por IP.
- **"E o app desktop?"** Sem cookie de navegador: [[Token por dispositivo|token por dispositivo]] no plano.
