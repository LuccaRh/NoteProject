---
id: chimchar/add-browser-login-with-a-session-cookie
nome: Tela de login e botão de sair (issue #48)
areas: [ui, cliente-api, auth]
---
## Pedido (o que a branch entrega; cada item verificável)
1. `auth/api.ts`: `isLoggedIn`, `logIn`, `logOut` em `/api/auth` (o cookie é httpOnly: o front
   nunca o lê, o navegador manda sozinho).
2. Sem sessão, um pop-up de login (email e senha) aparece antes da árvore e não fecha com Esc;
   senha errada → "Wrong email or password".
3. Botão "Log out" na barra: salva o pendente, encerra a sessão e volta ao login.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- `index.html`, `style.css` (o `.dialog` ganha `input`), `main.ts`.
- O Lucca pediu o código pronto (2026-11-03), mesmo nas áreas `aprender`.

## Fora (vira outra branch)
- Sessão que expira com a página aberta (30 dias): hoje vira "Server unreachable".
- Cadastro de usuário (o Lucca faz depois).
