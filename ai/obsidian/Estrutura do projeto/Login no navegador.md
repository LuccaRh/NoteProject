---
tags: [noteproject, auth, servidor, dados]
---
# Login no navegador

Com o app aberto na internet, as notas precisam de dono: cada pedido tem de dizer de quem é, e cada usuário só pode ver o que é dele. O login resolve as duas partes em peças separadas: o serviço `nujabes` descobre quem é o usuário, e o [[Row-Level Security|RLS]] do [[Postgres]] decide o que ele vê.

⏳ Tudo isto está em seis branches prontas da #48, ainda sem PR nem merge.

![[login-no-navegador.drawio.svg]]
*Em cima, o login, feito uma vez; embaixo, o que acontece em cada pedido de notas ou de chat.*

## As peças

| Peça | Papel |
|---|---|
| `chimchar` | abre o pop-up de login se não há sessão; botão de log out na barra lateral |
| [[Reverse proxy\|Caddy]] | deixa `/api/auth` passar direto; nas outras rotas de API, faz o [[Forward auth\|forward auth]] |
| `nujabes` | serviço novo: confere a senha, abre, acha e encerra [[Sessão de login\|sessões]]; banco próprio |
| `ichiro` e `lonzo` | leem o `X-User-Id` e gravam o id na [[Transação\|transação]] |
| [[Postgres]] | a *policy* do [[Row-Level Security\|RLS]] filtra as linhas pelo id da transação |

## Entrar

1. O pop-up manda `POST /api/auth/login` com email e senha, protegidos pelo [[TLS]].
2. O `nujabes` confere a senha com `crypt()` do pgcrypto ([[Hash de senha]]). Se não bate, responde 401.
3. Sorteia um token de 32 bytes e grava na tabela `sessions` o hash SHA-256 dele, com o `user_id` e a validade de 30 dias.
4. Responde 204 com `Set-Cookie: session=<token>` ([[Cookie]]) com `HttpOnly`, `Secure`, `SameSite=Lax` e `Max-Age` de 30 dias.

O cookie guarda só o token: nem senha, nem id do usuário. A senha passa uma vez, nesse pedido.

## Cada pedido depois

1. O navegador manda o cookie sozinho, e por isso o `notes/api.ts` não mudou.
2. O Caddy pergunta ao `nujabes` em `/auth/session`, repassando o cookie.
3. O `nujabes` procura o hash do token. Sem sessão válida, responde 401, e o Caddy devolve isso ao navegador.
4. Com sessão, responde 200 e `X-User-Id: <id>`. O Caddy troca qualquer `X-User-Id` que tenha vindo do navegador por esse e repassa o pedido; o navegador não guarda esse cabeçalho, que nasce de novo a cada pedido ([[Forward auth#O cabeçalho de identidade|forward auth]]).
5. O middleware `read_user` do `ichiro` guarda o id numa [[ContextVar]], uma variável própria de cada pedido. Sem id válido, responde 401, salvo em `/health`.
6. O `transaction()` do `db.py` roda `set_config('app.user_id', id, true)`; o `true` limita o valor à transação.
7. A *policy* junta `owner_id = app.user_id` a toda consulta. O SQL dos repositories fica igual, e o `INSERT` preenche o `owner_id` pelo `DEFAULT` da coluna.

O `lonzo` segue os mesmos passos e, quando chama o `ichiro`, um *event hook* do `httpx2` põe o `X-User-Id` em cada chamada. Assim as ferramentas do chat só alcançam as notas do mesmo usuário. As mensagens seguem a conversa: a *policy* de `messages` confere se a conversa dela é visível.

## Sair

`POST /api/auth/logout` apaga a linha da sessão e manda um `Set-Cookie` expirado. O token deixa de valer no servidor, mesmo que alguém tenha copiado o cookie.

## Por que assim

| Escolha | Motivo |
|---|---|
| `nujabes` separado | as senhas e sessões ficam num banco que `ichiro` e `lonzo` nem acessam |
| [[Forward auth\|forward auth]] no Caddy | a checagem fica num lugar só; rota nova atrás do prefixo já nasce protegida |
| `crypt()` no SQL | sem lib nova em Python, e usuário entra com um `INSERT` direto no banco |
| usuário de banco `ichiro` sem `BYPASSRLS` | superusuário ignora a *policy* ([[RLS ou filtro em cada consulta]]) |

## Criar um usuário

Ainda não há cadastro. No banco `nujabes`:

```sql
INSERT INTO users (email, password_hash)
VALUES ('me@example.com', crypt('senha', gen_salt('bf')));
```

## Limites

- Sessão que vence com a página aberta só mostra erro nas chamadas; o pop-up volta ao recarregar.
- Sem limite de tentativas no login, e linhas vencidas de `sessions` não são apagadas.
- O desenho vale só para o navegador: o app desktop usa [[Token por dispositivo|token por dispositivo]].
