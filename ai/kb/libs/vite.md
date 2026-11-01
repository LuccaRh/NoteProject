---
pacote: vite
versao: 8.1.5
fonte: apps/chimchar/node_modules/vite/dist/node/index.d.ts
areas: [ui, infra]
---
# vite — servidor de desenvolvimento atrás de proxy

Card destilado do código instalado (fonte acima, linhas citadas). Versão mudou → `./np lint`
avisa; reconfira as linhas antes de confiar no card.

## `server` (ServerOptions)

| Opção | Linha | Faz |
|---|---|---|
| `host` | :612 | onde escuta; `'0.0.0.0'` aceita conexão de fora do container |
| `allowedHosts` | :624 | nomes de `Host` que o Vite aceita; `localhost`, `*.localhost` e IPs já valem por padrão; `true` libera tudo (risco de DNS rebinding) |

- Atrás de um reverse proxy, o `Host` que chega é o nome que o navegador usou: com um domínio
  `*.localhost`, não precisa mexer em `allowedHosts`.

## WebSocket do reload (`server.ws`, WsOptions :1158)

| Opção | Linha | Faz |
|---|---|---|
| `server.ws.clientPort` | :1162 | porta que o navegador usa para o WebSocket do reload, quando difere da do Vite (proxy na 443) |
| `server.hmr.*` | :1166–1183 | `@deprecated`: use `server.ws.*` (no Vite 8 o nome mudou) |

- Sem `clientPort`, o cliente servido em `/@vite/client` monta o WebSocket com a porta da
  própria página (`hmrPort = null` → `importMetaUrl.port`): atrás do Caddy na 443, o reload
  já passa pelo proxy (conferido: handshake 101 em `https://notes.localhost/`).
