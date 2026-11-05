---
tags: [noteproject, plano, auth, servidor, dados]
---
# #48 Add browser login with a session cookie

Issue da [[M2 Login and TLS]]: nasce o serviço `apps/nujabes` (versão `0.1.0`), com banco próprio, que faz login, logout e confere a sessão de cada pedido por um [[Cookie|cookie]] httpOnly. O Caddy barra quem não tem sessão, e `ichiro` (`0.16.0`) e `lonzo` (`0.8.0`) passam a filtrar as linhas por dono com [[Row-Level Security|RLS]]; o `chimchar` (`0.11.0`) ganha o pop-up de login e o botão de log out. São seis branches, uma por serviço, ainda sem PR: `postgres`, `nujabes`, `caddy`, `ichiro`, `lonzo` e `chimchar`. Passou por autenticação, Postgres e banco, rede, Python, front, testes e as notas do vault.

## Autenticação

- O caminho inteiro está em [[Login no navegador]], com o desenho.
- A senha é conferida por `crypt()` do pgcrypto, sem lib nova em Python ([[Hash de senha]]).
- O token sai de `secrets.token_urlsafe(32)`, e a tabela `sessions` guarda só o hash SHA-256 dele ([[Sessão de login]]).
- Cookie `session` com `HttpOnly`, `Secure`, `SameSite=Lax` e 30 dias.
- Usuário entra por `INSERT` direto no banco: o cadastro fica para depois.

## Postgres e banco

- `postgres/init` cria o banco `nujabes` e o usuário `ichiro` com `NOSUPERUSER NOBYPASSRLS`. O Alembic segue conectando como superusuário.
- A *policy* compara `owner_id` com `nullif(current_setting('app.user_id', true), '')::uuid`. Sem usuário, o valor é `NULL`, e nenhuma linha passa.
- `ENABLE` + `FORCE ROW LEVEL SECURITY`: sem o `FORCE`, o dono da tabela escapa da *policy*.
- O `set_config(..., true)` vale só dentro da [[Transação|transação]], então uma conexão devolvida ao pool não leva o usuário anterior.
- O título único passou a ser por dono: `(owner_id, parent_id, title)`.
- A *policy* de `messages` usa um `EXISTS` em `conversations`, que já vem filtrada para o usuário.
- As [[Migration|migrations]] recusam rodar com linhas antigas sem um dono: `alembic -x owner=<id> upgrade head`.

## Rede

- [[Forward auth]]: um trecho `(logged_in)` no `Caddyfile`, importado nas rotas de `ichiro` e `lonzo`.
- `copy_headers` apaga o `X-User-Id` vindo do cliente antes de gravar o do `nujabes`, conferido no JSON do `caddy adapt` e com `curl` forjando o cabeçalho.

## Python

- Middleware `read_user` guarda o id numa `ContextVar`, que chega às rotas `def` (no threadpool) e aos geradores do [[Server-sent events|SSE]]; conferido num app mínimo.
- O `lonzo` repassa o usuário ao `ichiro` num *event hook* assíncrono do `httpx2`, sem mudar cada chamada.

## Front

- `src/auth/api.ts`: `isLoggedIn`, `logIn` e `logOut`. `src/auth/login-dialog.ts`: o pop-up, que o Escape não fecha.
- `start()` em `main.ts` espera o login antes de carregar a árvore. O log out salva a nota aberta, encerra a sessão e recarrega a página.

## Testes

- `make check`: `ichiro` 45, `lonzo` 48, `nujabes` 10, `chimchar` com tsc e build.
- Os testes de isolamento usam dois usuários. Conectando o `ichiro` como superusuário, 3 deles falham, e isso prova que testam o RLS.
- De ponta a ponta no `https://notes.localhost`: 401 sem login, com cabeçalho forjado e com senha errada; login mostra as notas; outro usuário vê 0; log out volta ao 401. Pop-up conferido no Playwright.
- O CI no GitHub ainda não rodou: as branches não foram enviadas.

## Notas do vault

- Novas: [[Login no navegador]], [[Cookie]], [[Sessão de login]], [[Hash de senha]], [[Forward auth]], [[Row-Level Security]], [[RLS ou filtro em cada consulta]] e [[Criar um serviço Python]].
- Mapa das [[00 Mapa — Issues feitas|issues feitas]]: figura com o `nujabes` e o `forward_auth`.
