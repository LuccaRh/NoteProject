---
tags: [noteproject, plano, workspace]
---
# Tarefas no GitHub

As tarefas do [[Roadmap]] ficam no GitHub do repo (`LuccaRh/NoteProject`). Assim a tarefa, a branch e o PR ficam ligados e o histórico mostra o que fechou o quê. O vault continua com o *porquê* (decisões, conceitos).

## As peças

| Peça | O que é | Neste projeto |
|---|---|---|
| **Issue** | uma tarefa, com título, texto, labels e comentários | uma issue = uma branch = um PR |
| **Milestone** | recurso do próprio repo: um nome que agrupa issues e PRs, com barra de progresso e data opcional | uma etapa do roadmap (M0–M4, Editor, AI in the app, Desktop app, Mobile app) |
| **Label** | etiqueta colorida para filtrar | o lado: `backend`, `frontend`, `infrastructure`, `ai-workspace` (e `bug`) |
| **Project** | quadro (kanban) por cima das issues, recurso à parte | colunas Todo / In progress / Done |

- Milestone não é um serviço nem um app: é só um campo da issue, como a label. A página *Milestones* do repo (`/milestones`) mostra quantas issues de cada etapa já fecharam.
- O Project é opcional. Com milestone e label já dá para listar por etapa; o quadro só deixa visível o que está em andamento.

## O ciclo de uma tarefa

1. Pegar a próxima issue aberta da milestone atual: `gh issue list -m "M1 Minimal server"`.
2. Branch com o nome da issue em kebab-case, saindo da `master` atualizada (`/tarefa`). O escopo (`ai/kb/escopos/<branch>.md`) cita o número da issue.
3. Commits seguindo as [[Regras de git]].
4. PR com só `Issue #N` no corpo (2026-10-26). A issue não fecha sozinha: quem fecha é o Lucca.
5. Issue sem PR (feita por outro caminho) quem fecha é o Lucca, à mão; a sessão só avisa que está pronta (2026-10-19).

## Labels

| Label | Uso |
|---|---|
| `backend` | [[O daemon notesd\|`notesd`]], servidor, modelo de dados, auth, sync: escrita à mão, conceito antes (`/aprender`) |
| `frontend` | editor e interface: gerado e revisado no PR |
| `infrastructure` | [[Container e Docker Compose\|containers]], deploy, [[CI e CD\|CI]], nuvem: escrita à mão |
| `ai-workspace` | guia, skills, ferramentas de `ai/` e notas do vault |
| `bug` | algo que não funciona como deveria |

- Quem escreve sai do lado: `backend` e `infrastructure` são das áreas de aprender.
- Issue sem milestone = ideia (o antigo `Features.md`), fora do roadmap por enquanto.

## Comandos

```sh
gh issue list -m "M1 Minimal server"        # o que falta na etapa
gh issue list -l backend                        # só o back
gh issue view 12                             # detalhe de uma issue
gh issue create -t "..." -m "M1 Minimal server" -l infrastructure
```

Ideia nova: issue sem milestone (`gh issue list --search no:milestone`). Ela só ganha milestone quando entra no [[Roadmap]].
