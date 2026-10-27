---
tags: [noteproject, infra]
---
# Rede do servidor

Os dispositivos falam com o servidor por duas URLs, a api e o sync. As duas chegam pela mesma porta e se separam dentro da [[EC2]]. Tudo aqui é plano (⏳, #16 e #22 do [[Roadmap]]); o domínio é exemplo.

![[rede-pedido-ec2.drawio.svg]]
*Um pedido ao sync: [[DNS]], [[Security Group]], [[Reverse proxy|Caddy]] e a rede do [[Docker Compose|compose]].*

## As chamadas

| O dispositivo chama | Chega em | Vai para |
|---|---|---|
| `https://notes.exemplo.com/api/...` | [[Reverse proxy\|Caddy]], 443 | `api:8000` |
| `wss://notes.exemplo.com/sync` | [[Reverse proxy\|Caddy]], 443 | `sync:<porta>` |

## O caminho, passo a passo

1. [[DNS]]: `notes.exemplo.com` → IP público da [[EC2]].
2. O dispositivo abre TCP em `IP:443`. O [[Security Group]] só deixa a 443 passar.
3. Na [[EC2]], a 443 está publicada no container `caddy`. O [[Reverse proxy|Caddy]] faz o [[TLS]] e lê o pedido.
4. Pelo caminho (`/sync`), ele abre outra conexão, HTTP simples, para `sync:<porta>`, pela [[Rede de containers|rede do compose]]. O nome `sync` vira o IP do container pelo DNS do Docker.
5. Do `api` para o [[Postgres]] é igual: `postgres:5432`, sem sair da rede.

## Portas

| Porta | Quem escuta | Publicada na [[EC2]]? | Aberta no [[Security Group]]? |
|---|---|---|---|
| 443 | `caddy` | sim | sim |
| 80 | ninguém | não | não: o app sempre chama `https`/`wss`; o Let's Encrypt valida pela 443 (desafio TLS-ALPN) |
| 8000 | `api` | não | não |
| `<porta>` | `sync` | não | não |
| 5432 | [[Postgres]] | não | não |

## Os arquivos

```yaml
# docker-compose.prod.yml (trecho)
services:
  caddy:
    image: caddy:2
    ports: ["443:443"]
    volumes:
      - ./infra/Caddyfile:/etc/caddy/Caddyfile
      - caddy-data:/data        # certificados, sobrevivem ao restart
  api:
    image: ghcr.io/.../api      # sem ports: só a rede do compose
  sync:
    image: ghcr.io/.../sync
```

```
# infra/Caddyfile
notes.exemplo.com {
    reverse_proxy /api/* api:8000
    reverse_proxy /sync* sync:<porta>
}
```
