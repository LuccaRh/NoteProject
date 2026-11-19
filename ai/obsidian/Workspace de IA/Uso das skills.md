---
tags: [noteproject, workspace]
---
# Uso das skills

As skills do workspace (lista em [[Como usar]]) foram criadas sem saber quais iam pegar. A contagem de uso mostra onde está o trabalho da sessão e qual skill ficou parada.

## Contagem (2026-10-15 a 2026-11-09)

Contadas nos 201 históricos de sessão (`~/.claude/projects/-home-lucca-Documents-NoteProject/*.jsonl`): chamadas da sessão (ferramenta `Skill`) mais os comandos digitados com `/`. O número é aproximado, porque uma sessão retomada ou compactada pode repetir a mesma chamada.

| # | Skill | Usos | Quem chama | O que faz |
|---|---|---|---|---|
| 1 | `/nota` | 70 | sessão | escreve ou atualiza páginas do vault (arquitetura, decisão) pelas [[Regras de página]], com desenho embutido |
| 2 | `/commit` | 54 | 46 sessão, 8 usuário | commits atômicos no formato do repo (inglês, imperativo, uma camada por commit, tag `[docs]`/`[ai-workspace]` fora do app); cada um passa no `make check`; conserto vira fixup; sem push |
| 3 | `/tarefa` | 49 | sessão | começa ou continua uma funcionalidade: branch da issue, escopo (Pedido / Contexto / Fora), contexto só da área, passos pequenos conferidos pelo `make check` |
| 4 | `/perguntas` | 38 | usuário | removida do workspace |
| 5 | `/lacunas` | 29 | 26 usuário, 3 sessão | lista, numerado, o que a conversa explicou e falta no vault |
| 6 | `/diagrama` | 27 | sessão | desenho draw.io a partir de YAML, conferido no PNG e embutido na nota |
| 7 | `/destrinchar` | 23 | 19 sessão, 4 usuário | acha o elo que falta numa confusão, com perguntas curtas |
| 8 | `/foco` | 8 | sessão | removida (commit `bb691cd`) |
| 9 | `/aprender` | 4 | — | conceito de sistemas do zero, ligado ao projeto, com exercício |
| 10 | `/escrita` | 3 | sessão | tira a cara de IA de README, PR e texto público |
| 11 | `/duvida` | 0 | — | trata `[!duvida]`, `[fix]`, `[coment]` nas notas |

Skills de fora do workspace (plugins e embutidas): `playwright-skill` 8, `claude-api` 8, `frontend-design` 4, `dataviz` 2, `pptx` 2.

## O que a contagem mostra

- A ordem do dia a dia é `/tarefa` → `/commit` → `/nota`, como no [[Esqueleto de tarefas]]; a nota entra no commit `[docs]`, o último da branch.
- Documentação pesa mais que código: `/nota` e `/diagrama` somam 97 usos, contra 49 do `/tarefa`.
- `/aprender` teve 4 usos; desde 2026-11-02 dados e servidor (backend de APIs) ficam com a sessão.
- `/duvida` nunca rodou.
- Fora das skills, o comando mais usado é `/clear` (184), um por tarefa nova.
