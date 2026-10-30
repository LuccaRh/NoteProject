---
tags: [noteproject, conceito, infra]
---
# Arquivo estático

Todo conteúdo que chega ao navegador é a resposta de um pedido HTTP. O que muda é como o servidor monta essa resposta: lendo um arquivo pronto do disco ou rodando código na hora. Arquivo estático é o primeiro caso.

| | Estático | Dinâmico |
|---|---|---|
| De onde vem a resposta | um arquivo no disco, mandado como está | código que roda a cada pedido (consulta o banco, monta o JSON) |
| Igual para todo mundo | sim, até o arquivo mudar | depende de quem pede e de quando |
| Exemplos | `index.html`, `.js`, `.css`, imagens | `GET /notes`, `POST /login` |
| Quem responde | qualquer servidor de arquivos | o programa da api ([[FastAPI]], por exemplo) |

## Servidor de arquivos

Um servidor de arquivos escuta numa [[Porta|porta]] e liga o caminho da URL a um caminho numa pasta:

| Pedido | Arquivo lido (pasta `/srv/web`) |
|---|---|
| `GET /` | `/srv/web/index.html` (convenção: `/` vira `index.html`) |
| `GET /assets/index-vMr1w5fw.js` | `/srv/web/assets/index-vMr1w5fw.js` |
| `GET /nao-existe.png` | nenhum: responde 404 |

- É **um pedido por arquivo**. O servidor não manda "o site inteiro": manda o `index.html`, e o navegador, ao ler cada `<script src>` e `<link href>`, faz um pedido novo para cada um.
- Junto do arquivo vai o `Content-Type`, escolhido pela extensão, que diz ao navegador o que fazer com ele ([[Servidor de desenvolvimento]], "Content-Type decide").
- O servidor não entende o conteúdo: não converte TypeScript nem roda o JS. Quem roda o JS é o navegador, depois de baixar.

Qualquer programa que faça essa ligação serve: `python -m http.server 8080` dentro da pasta já basta para testar. O Live Server do VS Code é o mesmo servidor de arquivos, com um script a mais injetado no HTML que recarrega a página quando o arquivo é salvo *(geral)*.

> [!warning] Erros comuns
> - Abrir o `index.html` com duplo clique (`file://`): sem servidor, o navegador bloqueia os `<script type="module">` e os caminhos `/assets/...` não acham nada.
> - Esperar que o servidor de arquivos converta `.ts`: ele manda o arquivo como está. Por isso o front passa antes pelo [[Build do front|build]].

> [!example] No NoteProject
> Em produção o [[Reverse proxy|Caddy]] é o servidor de arquivos do build do editor ([[Navegador]]).

Docs: [Caddy file_server](https://caddyserver.com/docs/caddyfile/directives/file_server), [Python http.server](https://docs.python.org/3/library/http.server.html).
