---
tags: [noteproject, plano]
---
# Plano do projeto — mapa

Como o projeto anda: em que ordem, onde ficam as tarefas e como cada mudança entra no git. A arquitetura (o que construir) fica em [[00 Mapa — Estrutura do projeto|Estrutura do projeto]].

| Página                | Ideia                                                                                                     |
| --------------------- | --------------------------------------------------------------------------------------------------------- |
| [[Objetivo do app]]   | aprender > uso diário com IA > vários aparelhos > várias pessoas; v1 = ler notas no navegador, servidor na AWS |
| [[Roadmap]]           | navegador → app desktop → celular; no navegador, M0 servidor → M1 notas → M2 login → M3 AWS → M4 ao vivo; editor em paralelo |
| [[Entrega de 2026-11-06]] | notas e IA em localhost até 2026-11-06: sequência das issues, o que a IA faz, o que fica fora |
| [[Prioridade das features]] | as ideias de [[Features]] numa fila só, por urgência: risco, v1, uso diário |
| [[Tarefas no GitHub]] | issue = branch = PR; milestone = etapa; labels por lado (backend, frontend, infrastructure, ai-workspace) |
| [[Regras de git]]     | branch, commit, mensagem, PR e merge                                                                      |
| [[Um repo ou vários]] | monorepo com `apps/` e `infra/`, e não um repo por serviço                                                |
| [[00 Mapa — Issues feitas\|Issues feitas]] | uma página por milestone: o que cada issue entregou e o que ficou aprendido |

Detalhe das trilhas: [[Trilha de infra]] (infra peça por peça) e [[Ordem de implementação]] (editor e IA).
