---
tags: [noteproject, conceito, ui]
---
# Servidor de desenvolvimento

O navegador só sabe pedir um caminho a um endereço e uma [[Porta|porta]] (`GET /` em `localhost:5173`). Alguém precisa estar escutando ali e responder com os arquivos do front. No desenvolvimento, esse alguém é um programa como o Vite: o servidor de desenvolvimento.

## O que ele responde

| Pedido | Resposta |
|---|---|
| `GET /` | o `index.html` da pasta do projeto (convenção de servidor web: `/` vira `index.html`) |
| `GET /src/main.ts` | o arquivo convertido para JavaScript na hora, sem os tipos |
| `GET /api/...` | não responde: repassa à api ([[Proxy de desenvolvimento]]) |

- O navegador nunca sabe que existe um `index.html`: ele pede `/`, e o servidor escolhe o arquivo.
- Depois de ler o HTML, cada `<script src>` e `<link href>` vira um pedido novo à mesma porta.

## Content-Type decide, não a extensão

A resposta traz o cabeçalho `Content-Type`, e é ele que diz ao navegador o que fazer: `text/html` ele desenha, `text/javascript` executa quando veio de um `<script>` e mostra como texto quando a URL é aberta direto. Um arquivo `.ts` pode chegar como `text/javascript`, porque o servidor já o converteu.

## Desenvolvimento × produção

| | Servidor de desenvolvimento | Produção |
|---|---|---|
| Comando | `vite` (`npm run dev`) | `vite build` gera a pasta `dist/` uma vez ([[Build do front\|build]]) |
| Conversão | a cada pedido, arquivo por arquivo | antes, tudo junto e compactado |
| Ao salvar | a página recarrega sozinha | nada muda até o próximo build |
| Quem serve | o próprio Vite | um [[Arquivo estático\|servidor de arquivos]] ou o [[Reverse proxy\|reverse proxy]] |

> [!warning] Erros comuns
> - Achar que ver o código no navegador é falha: todo código de front chega ao navegador para rodar, em qualquer site (aba **Sources** do DevTools). Segredo (senha, chave de API) fica no back, nunca no front.
> - Expor o servidor de desenvolvimento na internet: ele serve os arquivos-fonte e não foi feito para isso; em produção vai o build.

> [!example] No NoteProject
> O Vite escuta na `5173` e serve o `apps/chimchar/` ([[Como ler o front]]).

Docs: [Vite — por que o Vite](https://vite.dev/guide/why).
