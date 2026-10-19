---
tags: [noteproject, plano, infra, servidor]
---
# Roadmap

A ordem segue o [[Objetivo do app]]: aprender vem primeiro, e a v1 (ler notas no navegador) fica pronta no fim do M3. A ordem:

1. **[[Navegador]]**: servidor, banco, login e infra (M0–M4), numa sequência só com a [[Trilha de infra]] e a [[Ordem de implementação]].
2. **App desktop**: app instalado com o [[O daemon notesd|`notesd`]], que funciona offline.
3. **Celular**: app do celular.

Ideias sem lugar na fila: Neovim/CLI ([[Features]]) e ink. As tarefas ficam como issues no GitHub ([[Tarefas no GitHub]]), agrupadas em milestones.

![[plano-roadmap.drawio.svg]]
*Trilha principal escrita à mão (M0→M4); trilha do editor delegada, em paralelo; depois desktop e celular.*

## Duas trilhas

| Trilha | Áreas | Quem escreve | Label |
|---|---|---|---|
| principal | dados, servidor, auth, infra, sync | à mão, conceito antes (`/aprender`) | `backend`, `infrastructure` |
| editor | editor, ui, cliente-api | gerado, revisado no PR | `frontend` |

- A principal anda na ordem M0 → M4. A do editor entra quando a principal espera (revisão, leitura, deploy rodando).
- Issue que pede decisão (o texto diz "Decide") precisa dela escrita no vault antes do código: lib nova, schema, serviço novo.

## Milestones

| Milestone | Issues | Fecha quando |
|---|---|---|
| **M0 Server skeleton** | #10–#13 | `apps/notes` em [[Container e Docker Compose\|compose]] com [[Postgres e migrations\|Postgres]] e migrations, `/health` respondendo |
| **M1 Notes in the browser** | #46, #47, #6–#9 | o editor abre pela URL do servidor e cria, edita e busca notas no [[Postgres e migrations\|Postgres]]; [[Pastas, campos e views\|pastas, campos e views]] |
| **M2 Login and TLS** | #48, #16, #17 | login por [[Autenticação\|cookie de sessão]], [[Reverse proxy\|Caddy]] com [[TLS e HTTPS\|TLS]] local, [[CI e CD\|CI]] do servidor verde |
| **M3 Online on AWS** | #18–#25 | domínio com [[TLS e HTTPS\|HTTPS]], deploy por merge, [[Backup e restore\|backup]] restaurado uma vez |
| **M4 Live edits** | #26, #27, #30 | edição numa aba aparece na outra, pelo [[WebSocket]] |
| **Desktop app** | #14, #15, #28, #29 | sem data: app instalado com o [[O daemon notesd\|`notesd`]], [[Token por dispositivo\|token por dispositivo]] e [[Sync por versão\|sync depois de offline]] |
| **Mobile app** | — | sem data: app do celular, depois do desktop |
| **Editor** | #5, #31–#33, #37 | sem data; acompanha as outras |
| **AI in the app** | #35, #42, #36, #34 | sem data, depois da v1 (fim do M3): worker em `apps/worker`, [[Workspace no app\|workspace]] de cada pessoa |

### M0 — esqueleto do servidor (no PC, custo zero)
#10 `apps/notes` com `/health` → #11 [[Container e Docker Compose|compose]] → #12 [[Postgres e migrations|Postgres + migrations]] (`users`, `notes` com `parent_id`, `fields`, `version`) → #13 `.env` fora do git.

### M1 — notas no navegador
1. #46 rotas `/notes` e `/search`, com a busca full-text do [[Postgres e migrations|Postgres]]; no front, o cliente da API e a lista de notas, com o proxy do Vite apontando para o servidor (`:8000`).
2. #47 o servidor serve o build do front: uma URL só, nada instalado.
3. #6 pastas, #7 campos (JSONB), #8 [[Pastas, campos e views|views]]: modelo de dados, à mão.
4. #9 sidebar com pastas e views: delegada.

### M2 — login e TLS
#48 [[Autenticação|cookie de sessão]] → #16 [[Reverse proxy|Caddy]] com [[TLS e HTTPS|TLS]] local → #17 [[CI e CD|CI]] do servidor com Postgres.

### M3 — no ar na AWS
#18 conta + Budget → #19 Terraform → #20 host com SSM → #21 domínio → #22 HTTPS → #23 deploy por [[OIDC]] → #24 [[Backup e restore|backup]] em [[S3 — armazenamento de objetos|S3]] → #25 alarme. Detalhe de cada peça em [[Trilha de infra]].

### M4 — edição ao vivo
#26 decidir como a edição chega no documento do servidor ([[WebSocket]] com [[CRDT e Yjs|Yjs]] ou `PATCH` virando update) → #27 endpoint [[WebSocket]] → #30 [[WebSocket]] atrás do [[Reverse proxy|Caddy]].

## Por que essa ordem

- **Servidor antes da tela**: o editor e a sidebar já existem e chamam `/api`; falta quem responda. O banco vem cedo porque pastas e campos mudam o schema.
- **Login antes da AWS**: nada vai ao ar sem auth e sem [[TLS e HTTPS|TLS]].
- **AWS (M3) antes da edição ao vivo (M4)**: um servidor pequeno vai ao ar cedo, e problemas de rede, [[TLS e HTTPS|TLS]] e deploy aparecem com pouco código *(geral: "walking skeleton")*. A `t4g.small` é grátis até 31/12/2026 ([[Custo zero — créditos e free tier]]).
- **Navegador → desktop → celular**: o navegador não instala nada e já exercita servidor, login e infra. O desktop soma o uso offline: o [[O daemon notesd|`notesd`]] é um cliente a mais do mesmo servidor. O celular vem por último, reaproveitando o sync do desktop.

## Revisar se...

- Os créditos da AWS acabarem antes de M3: M4 roda inteiro no PC, então a ordem pode inverter.
- O uso offline virar necessidade antes do fim de M4: Desktop sobe na fila.
- A decisão #26 trocar y-py por um serviço Node (`y-websocket`): M4 ganha um serviço novo.
