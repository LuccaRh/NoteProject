---
tags: [noteproject, plano, infra, servidor]
---
# Roadmap

A ordem segue o [[Objetivo do app]]: aprender vem primeiro, e a v1 (ler notas no navegador) fica pronta no fim do M3. A ordem:

1. **[[Navegador]]**: servidor, banco, login e infra (M0–M4), numa sequência só com a [[Trilha de infra]] e a [[Ordem de implementação]].
2. **App desktop**: app instalado com o [[O daemon notesd|`notesd`]], que funciona offline.
3. **Celular**: app do celular.

Para 2026-11-06, a [[Entrega de 2026-11-06|entrega]] puxa notas e IA em localhost para antes do M2. Ideias sem lugar na fila: Neovim/CLI ([[Features]]) e ink; as de [[Features]] estão ordenadas em [[Prioridade das features]]. As tarefas ficam como issues no GitHub ([[Tarefas no GitHub]]), agrupadas em milestones.

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
| **M0 Server skeleton** | #10–#13 | `apps/ichiro` em [[Docker Compose\|compose]] com [[Postgres]] e migrations, `/health` respondendo |
| **M1 Notes in the browser** | #46, #62, #16, #56, #6–#9 | o editor abre por `https://` local, pelo [[Reverse proxy\|Caddy]], e cria, edita e busca notas no [[Postgres]]; [[Pastas, campos e views\|pastas, campos e views]] |
| **M2 Login and TLS** | #48, #17 | login por cookie de sessão, `/api/auth` no [[Reverse proxy\|Caddy]], [[CI]] do servidor verde |
| **M3 Online on AWS** | #18–#25, #47 | domínio com [[TLS\|HTTPS]], deploy por merge, [[Backup\|backup]] restaurado uma vez |
| **M4 Live edits** | #26, #27, #30 | edição numa aba aparece na outra, pelo [[WebSocket]] |
| **Desktop app** | #14, #15, #28, #29 | sem data: app instalado com o [[O daemon notesd\|`notesd`]], [[Token por dispositivo\|token por dispositivo]] e [[Sync por versão\|sync depois de offline]] |
| **Mobile app** | — | sem data: app do celular, depois do desktop |
| **Editor** | #5, #31–#33, #37 | sem data; acompanha as outras |
| **AI in the app** | #35, #42, #36, #34 | sem data, depois da v1 (fim do M3): worker em `apps/worker`, [[Workspace no app\|workspace]] de cada pessoa |

### M0 — esqueleto do servidor (no PC, custo zero)
#10 `apps/ichiro` com `/health` → #11 [[Docker Compose|compose]] → #12 [[Postgres]] + [[Migration|migrations]] (`users`, `notes` com `parent_id`, `fields`, `version`) → #13 `.env` fora do git.

### M1 — notas no navegador
1. #46 rotas `/notes` no [[Postgres]], e #56 `/notes/search` com a busca full-text; no front, #62 o cliente da API e a lista de notas, com o proxy do Vite apontando para o servidor (`:8000`).
2. #16 [[Reverse proxy|Caddy]] com [[TLS]] local no compose de dev: `/api/notes` → `ichiro`, o resto → Vite; sai o proxy do Vite.
3. #6 pastas, #7 campos (JSONB), #8 [[Pastas, campos e views|views]]: modelo de dados, à mão.
4. #9 sidebar com pastas e views: delegada.

### M2 — login e TLS
#48 cookie de sessão, com `/api/auth` no [[Reverse proxy|Caddy]] → #17 [[CI]] do servidor com Postgres.

### M3 — no ar na AWS
#18 conta + Budget → #19 Terraform → #20 host com SSM → #21 domínio → #22 HTTPS → #47 imagem do [[Reverse proxy|Caddy]] com o build do front → #23 deploy por [[OIDC]] → #24 [[Backup|backup]] em [[S3]] → #25 alarme. Detalhe de cada peça em [[Trilha de infra]].

### M4 — edição ao vivo
#26 decidir como a edição chega no documento do servidor ([[WebSocket]] com [[Yjs]] ou `PATCH` virando update) → #27 endpoint [[WebSocket]] → #30 [[WebSocket]] atrás do [[Reverse proxy|Caddy]].

## Por que essa ordem

- **Servidor antes da tela**: a lista de notas só tem o que mostrar quando o servidor responde `/notes`. O banco vem cedo porque pastas e campos mudam o schema.
- **Login antes da AWS**: nada vai ao ar sem auth e sem [[TLS]].
- **AWS (M3) antes da edição ao vivo (M4)**: um servidor pequeno vai ao ar cedo, e problemas de rede, [[TLS]] e deploy aparecem com pouco código *(geral: "walking skeleton")*. A `t4g.small` é grátis até 31/12/2026 ([[Custo zero — créditos e free tier]]).
- **Navegador → desktop → celular**: o navegador não instala nada e já exercita servidor, login e infra. O desktop soma o uso offline: o [[O daemon notesd|`notesd`]] é um cliente a mais do mesmo servidor. O celular vem por último, reaproveitando o sync do desktop.

## Revisar se...

- Os créditos da AWS acabarem antes de M3: M4 roda inteiro no PC, então a ordem pode inverter.
- O uso offline virar necessidade antes do fim de M4: Desktop sobe na fila.
- A decisão #26 trocar y-py por um serviço Node (`y-websocket`): M4 ganha um serviço novo.
