---
tags: [noteproject, conceito, infra]
---
# Build multi-stage

Algumas imagens precisam de uma ferramenta só para **gerar** os arquivos, e não para rodar. O [[Build do front|build do front]] é o caso típico: o Node e o `node_modules` (centenas de MB) servem para produzir o `dist/`, e depois só o `dist/` interessa. Um [[Dockerfile]] de um estágio só levaria tudo isso para a imagem final.

O multi-stage resolve com vários `FROM` no mesmo Dockerfile. Cada `FROM` começa um estágio novo, e só o último vira a imagem; os anteriores são descartados depois do build.

```dockerfile
# Estágio 1: gera o dist/ (Node só existe aqui)
FROM node:22-alpine AS web
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Estágio 2: a imagem final, sem Node
FROM caddy:2
COPY --from=web /app/dist /srv/web
COPY Caddyfile /etc/caddy/Caddyfile
```

- `AS web` dá nome ao estágio.
- `COPY --from=web` copia de dentro do estágio `web`, e não do host. É o mesmo `COPY --from` que copia de outra imagem ([[Dockerfile]], "As instruções"), apontado para um estágio do próprio arquivo.
- A imagem final tem só o servidor e a pasta pronta. O cache de camadas vale em cada estágio: mudar o código refaz o `npm run build`, mas o `npm ci` vem do cache.

| | Um estágio | Multi-stage |
|---|---|---|
| Node na imagem final | sim | não |
| Tamanho | Node + `node_modules` + `dist/` | só o servidor + `dist/` |
| Onde o build roda | dentro da imagem, de qualquer jeito | no estágio descartável |

## Por volume, em vez de imagem

A outra forma de pôr o `dist/` no disco do servidor é gerar a pasta no host e montá-la como [[Volume do Docker|volume]] (`./dist:/srv/web`). A imagem fica só com o servidor, mas a máquina precisa de Node para rodar o build antes de subir o container, e a versão que roda depende do que estava na pasta naquele momento. Com o multi-stage, a imagem já sai completa e versionada: basta baixá-la e subir.

> [!warning] Erros comuns
> - Copiar o `node_modules` do host com `COPY . .`: entra a versão do host (às vezes de outro sistema). Um `.dockerignore` com `node_modules` e `dist` evita.
> - Achar que o estágio 1 roda quando o container sobe: tudo dele acontece no `docker build`; o container só tem o resultado.

> [!example] No NoteProject
> A imagem do [[Reverse proxy|Caddy]] de produção leva o `dist/` do editor assim ([[Infra — deploy e operação]]).

Docs: [Docker — Multi-stage builds](https://docs.docker.com/build/building/multi-stage/).
