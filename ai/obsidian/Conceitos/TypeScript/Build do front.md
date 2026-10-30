---
tags: [noteproject, conceito, ui]
---
# Build do front

O navegador só roda JavaScript e não sabe achar uma lib pelo nome (`import ... from 'codemirror'`). No desenvolvimento, o [[Servidor de desenvolvimento|servidor de desenvolvimento]] resolve isso a cada pedido. Em produção, a conversão é feita **uma vez**, antes: o build, que gera uma pasta de [[Arquivo estático|arquivos estáticos]] prontos para qualquer servidor entregar.

## O que o build faz

`vite build` (`npm run build`) lê o código-fonte e grava o resultado em `dist/` (de *distribution*):

| Passo | O que acontece |
|---|---|
| TypeScript → JavaScript | os tipos somem; sobra JS que o navegador roda |
| resolver os imports | `'codemirror'` vira o código da lib, tirado do `node_modules` |
| juntar (bundle) | dezenas de arquivos viram poucos: em geral um `.js` e um `.css` |
| compactar (minify) | tira espaços e encurta nomes: o arquivo fica menor |
| nome com hash | `index-vMr1w5fw.js`: o hash muda quando o conteúdo muda |
| `index.html` | copiado com os `<script>` e `<link>` já apontando para esses nomes |

```
dist/
  index.html
  favicon.svg
  assets/index-vMr1w5fw.js     ← todo o código do front + libs
  assets/index-D4D3czfd.css
```

O código-fonte fica no git e não vai para produção: o que sai para o servidor é só o `dist/`.

## Onde o front roda

No navegador de quem abre a página. O servidor só guarda e entrega o `dist/`:

1. O navegador pede `/` e recebe o `index.html`.
2. Lê o HTML e pede o `.js` e o `.css` citados nele.
3. Roda o `.js` na própria máquina: a tela do app aparece.
4. Dali em diante, o JS pede só dados à api (`/api/...`), já sem baixar o app de novo.

- Na primeira visita, o navegador baixa o `.js` inteiro (centenas de KB num editor).
- Depois guarda em cache. Como o nome tem o hash, um build novo gera um nome novo, e o navegador baixa só o que mudou; o mesmo nome pode ficar em cache por muito tempo sem risco de versão velha *(geral)*.

> [!warning] Erros comuns
> - Achar que em produção existe um "serviço do front" rodando: depois do build, o front é uma pasta de arquivos. Node e Vite não estão no servidor.
> - Esquecer o build depois de mudar o código: o servidor continua entregando o `dist/` antigo.

> [!example] No NoteProject
> O `dist/` do editor tem um `.js` de ~500 KB, servido pelo [[Reverse proxy|Caddy]] em produção ([[Navegador]]).

Docs: [Vite — Building for Production](https://vite.dev/guide/build).
