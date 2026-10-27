---
tags: [noteproject, conceito, infra]
---
# OIDC

Um deploy automático precisa entrar na nuvem a partir do [[CI|GitHub Actions]]. O jeito antigo é guardar uma chave da AWS nos segredos do GitHub: ela não expira, e quem a vazar entra.

- **OIDC** (*OpenID Connect*): a cada execução, o GitHub emite um token assinado que diz "sou o workflow X do repo Y, na branch Z".
- A AWS confere a assinatura e, se bater com a regra, entrega credenciais temporárias de uma role do [[IAM]].

1. O workflow pede o token ao GitHub.
2. Troca o token por credenciais da role na AWS.
3. As credenciais expiram sozinhas.

- Nenhuma chave guardada; a regra pode aceitar só uma branch de um repo.

> [!example] No NoteProject
> O deploy por merge entra na AWS assim ([[Infra — deploy e operação]]).

Doc: [GitHub — OpenID Connect](https://docs.github.com/en/actions/concepts/security/openid-connect).
