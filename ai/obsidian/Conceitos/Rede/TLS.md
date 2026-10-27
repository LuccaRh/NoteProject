---
tags: [noteproject, conceito, infra]
---
# TLS

Entre o cliente e o servidor, a mensagem passa por redes de outros (Wi-Fi, provedor). Sem proteção, qualquer um no caminho lê o token e os dados, ou troca o conteúdo.

- **TLS**: camada que cifra a conexão e prova que o servidor é quem diz ser.
- **HTTPS**: HTTP por dentro de TLS.
- **Certificado**: documento assinado por uma autoridade (CA) que liga um [[Domínio|domínio]] a uma chave. O cliente confia na CA, logo confia no servidor.
- **Let's Encrypt**: CA grátis e automática; confere que quem pede controla o domínio e emite certificados de curta duração, renovados sozinhos.

| Onde | Certificado | Quem confia |
|---|---|---|
| na própria máquina | CA local (o [[Reverse proxy\|Caddy]] cria uma) | só a máquina que instalou a CA |
| na internet | Let's Encrypt | qualquer navegador |

- O certificado é de um nome, não de um IP: HTTPS de verdade precisa do domínio.

> [!example] No NoteProject
> Certificado local no PC primeiro, Let's Encrypt na AWS depois ([[Infra — deploy e operação]]).

Doc: [Let's Encrypt — como funciona](https://letsencrypt.org/how-it-works/).
