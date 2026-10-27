---
tags: [noteproject, conceito, auth]
---
# Token por dispositivo

Um servidor que guarda dados de vários usuários precisa saber, a cada pedido, de quem ele é. Pedir a senha a cada pedido não serve, e um app sempre conectado não tem a sessão do navegador.

A ideia: cada dispositivo ganha um **token** próprio no primeiro login e o manda em todo pedido.

1. Login uma vez no dispositivo → o servidor gera um token e guarda de quem e de qual dispositivo ele é.
2. O app guarda o token e o põe em cada pedido HTTP e em cada conexão [[WebSocket]].
3. Dispositivo perdido → apaga-se só o token dele; os outros continuam.

- O token vale como a senha: só viaja por conexão cifrada ([[TLS]]).
- Quanto menos programas guardam o token, menos lugares podem vazá-lo.

> [!example] No NoteProject
> Proposta para o login: quem guarda o token é o [[O daemon notesd|daemon]] ([[Back — daemon e servidor]]).
