---
tags: [noteproject, conceito, rede, auth]
---
# Cookie

HTTP não guarda memória entre um pedido e o seguinte: cada pedido chega ao servidor sem nada que o ligue ao anterior. O cookie resolve isso com um pedaço de texto que o servidor pede para o navegador guardar e que o navegador devolve sozinho nos pedidos seguintes ao mesmo site.

## O ciclo

1. O servidor responde com o cabeçalho `Set-Cookie: nome=valor; atributos`.
2. O navegador guarda o par `nome=valor`, ligado àquele site.
3. Todo pedido seguinte ao site leva o cabeçalho `Cookie: nome=valor`, sem código nenhum na página.
4. Para apagar, o servidor manda um `Set-Cookie` com o mesmo nome, já expirado.

## Atributos

| Atributo | O que faz |
|---|---|
| `HttpOnly` | o JavaScript da página não lê o cookie; um script injetado não consegue roubá-lo |
| `Secure` | o navegador só manda o cookie por HTTPS ([[TLS]]) |
| `SameSite=Lax` | pedido `POST` que parte de outro site não leva o cookie; clicar num link que traz para cá leva |
| `Max-Age` | segundos até o navegador apagar o cookie; sem ele, o cookie some ao fechar o navegador |
| `Path` | em quais caminhos do site o cookie vai; `/` cobre todos |

- O conteúdo é texto comum: quem tem acesso ao navegador consegue ler. Dado sensível não entra nele.
- Cookie de login vale como credencial: quem copia o valor entra como o dono, até ele expirar.
- Entre origens diferentes, o cookie só vai com permissão explícita do [[CORS]]; na mesma origem, vai sozinho.
- Um app fora do navegador não tem esse mecanismo automático, e por isso costuma usar um [[Token por dispositivo|token por dispositivo]].

> [!example] Um uso
> O [[Login no navegador]] guarda num cookie só o token da [[Sessão de login|sessão]].
