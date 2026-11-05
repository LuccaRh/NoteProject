---
id: chimchar/disable-the-login-button-until-the-form-is-valid
nome: Botão de login desativado até o formulário valer (issue #126)
areas: [ui]
---
## Pedido (o que a branch entrega; cada item verificável)
1. O botão "Log in" fica desativado até ter email bem formado e senha; volta a valer depois de
   uma senha errada.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- `auth/login-dialog.ts`. A checagem é a do navegador (`checkValidity`), que aceita `a@b`.

## Fora (vira outra branch)
- Dizer na tela o que falta no campo.
- Sessão que expira com a página aberta.
