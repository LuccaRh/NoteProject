---
tags: [noteproject, plano, infra]
---
# Um repo ou vários

O NoteProject vai ter vários serviços: o editor, o servidor (M0–M1), o sync (M4), o [[O daemon notesd|`notesd`]] do app desktop e a infra ([[Docker Compose|compose]], [[Reverse proxy|Caddy]], [[Terraform]]). Cada um pode ter um repo próprio ou todos podem ficar num só (*monorepo*).

## Como funciona com vários repos

- Um repo por serviço, cada um publicando uma imagem com versão (`api:1.4.2`).
- Um repo de entrega com o `docker-compose.yml` que fixa a versão de cada imagem. Atualizar = trocar a tag no [[Docker Compose|compose]].
- Faz sentido com vários devs e times, cada serviço com seu ritmo de release.

## Opções

| Critério | Um repo (monorepo) | Vários repos |
|---|---|---|
| quem mantém | uma pessoa ✓ | vários times ✓ |
| mudança que cruza serviços (protocolo de sync muda cliente e servidor) | um commit, um PR ✓ | PRs coordenados em repos diferentes |
| [[CI]] | um workflow com filtro por pasta | um por repo, mais config repetida |
| versão independente por serviço | por tag de imagem, mesmo no mesmo repo | natural ✓ |
| permissão por serviço | não | sim ✓ |
| `ai/np contexto` e o workspace de IA | um só ✓ | um por repo |

## Escolha: um repo

- Uma pessoa só, e as mudanças importantes (sync, auth) mexem no cliente e no servidor ao mesmo tempo.
- A separação em serviços fica no deploy, não no repo: uma pasta por serviço e uma imagem por serviço.

```
apps/chimchar  editor (Vite + CodeMirror)
apps/ichiro    API de notas: /notes, /notes/search, build do front (M0–M1)
apps/auth      API de login e sessões (M2)
apps/worker    worker de IA: pega pedidos da fila e chama o modelo (depois da v1)
apps/sync      sync ao vivo (M4)
apps/notesd    notesd, daemon do app desktop (Desktop app)
infra/         compose, Caddyfile, Terraform: o papel do repo de entrega
```

- A pasta `infra/` faz o papel do repo de entrega: o [[Docker Compose|compose]] de produção aponta para as imagens no [[CD|GHCR]] com tag.
- Cada API tem a própria pasta, imagem e [[Container|container]]; nada de uma API geral para tudo. O [[Reverse proxy|Caddy]] manda cada caminho (`/api/notes`, `/api/auth`) para a API dela; o caminho nomeia o recurso, não o serviço, e o front não muda quando uma rota troca de serviço ([[Reverse proxy#Prefixo nomeia o recurso|prefixo por recurso]]).
- Cada serviço Python (`ichiro`, `auth`, `worker`, `sync`) é um projeto uv próprio com a mesma forma: `pyproject.toml`, `src/<serviço>/` e `tests/`, criado com `uv init --python 3.14` na pasta do serviço; o porquê da estrutura `src/` está em [[API de notas]].
- Em aberto: como `ichiro` confere o login feito em `auth` (tabela de sessões no mesmo [[Postgres]], pedido ao `auth` ou token assinado) e onde fica o código Python que as APIs compartilham.

## Revisar se...

- Outra pessoa ou time assumir um serviço.
- Uma parte virar projeto público à parte (plugin do Neovim, app mobile com outro ciclo de release).
- O [[CI]] ficar lento mesmo com filtro por pasta (`paths:` no workflow).
