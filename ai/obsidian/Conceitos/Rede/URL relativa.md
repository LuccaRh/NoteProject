---
tags: [noteproject, conceito, cliente-api]
---
# URL relativa

O mesmo código do front roda em lugares diferentes: `http://localhost:5173` no desenvolvimento, `https://<domínio>` em produção. Se cada `fetch` levasse o endereço inteiro, o código teria de mudar em cada lugar.

URL relativa é a URL sem o começo: o código escreve só o caminho (`/api/notes`), e o [[Navegador|navegador]] completa com a URL da página aberta, a da barra de endereço.

| Página aberta em | O código pede | O navegador pede |
|---|---|---|
| `http://localhost:5173/` | `/api/notes` | `http://localhost:5173/api/notes` |
| `https://exemplo.com/` | `/api/notes` | `https://exemplo.com/api/notes` |
| `https://exemplo.com/docs/a` | `b` (sem `/`) | `https://exemplo.com/docs/b` |
| qualquer uma | `http://localhost:8000/notes` | o mesmo: URL completa não é completada |

- Começa com `/`: herda esquema, host e [[Porta|porta]] da página (a origem, no sentido do [[CORS]]) e troca o caminho inteiro.
- Sem `/` no começo: troca só o último pedaço do caminho, como um arquivo na mesma pasta. Para chamar uma api, quase sempre se quer o `/`.
- Como herda a origem, o pedido relativo é sempre da mesma origem: o navegador não confere [[CORS]].

> [!example] No NoteProject
> O cliente da api chama `/api/notes`; no desenvolvimento e em produção quem atende é o [[Reverse proxy|Caddy]].

Docs: [MDN — What is a URL (absolute vs relative)](https://developer.mozilla.org/en-US/docs/Learn_web_development/Howto/Web_mechanics/What_is_a_URL#absolute_urls_vs._relative_urls).
