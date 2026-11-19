---
tags: [noteproject, workspace]
---
# Desenvolvimento com Claude Code

O projeto foi feito junto com o Claude Code, dentro de um "workspace de IA" montado no próprio repo: regras, ferramentas e notas que deixam a sessão previsível e barata. Detalhe em [[Como usar]].

![[workspace.drawio.svg]]
*O workspace de IA: `CLAUDE.md`, skills, hooks e a CLI `ai/np` em volta do código.*

## Divisão de trabalho

- Áreas de aprendizado (sync, auth, infra, chamadas do front à API): o conceito vem primeiro e o código é escrito à mão, com a sessão revisando.
- Backend de dados e front: a sessão escreve, com proposta de desenho antes de decisão de arquitetura (lib nova, modelo de dados, serviço novo).
- "Funciona" só depois de rodar `make check` ou `curl` no serviço.

## Regras viram código

| Mecanismo | Exemplo |
|---|---|
| lint do workspace (`ai/np lint`, W01–W25) | camadas, commit por camada, docstring, 80 colunas, prompt em `.md` |
| ruff / mypy strict / tsc | estilo e tipos |
| hook `commit-msg` do git | mensagem em inglês, imperativo, ≤ 72, sem prefixo |
| hooks do Claude Code | barram ler arquivo grande inteiro; avisam quando o contexto cresce |

Instrução escrita que pode ser esquecida virou checagem automática.

## Fluxo de uma tarefa

1. Issue no GitHub, na milestone (M0–M4, Editor, AI in the app...).
2. Branch `<serviço>/<kebab-case>`, um serviço por branch; com `ai/kb/escopos/<branch>.md` (pedido, contexto, fora).
3. `ai/np contexto <área>` lista só o que ler: contexto curto, sem varrer o repo.
4. Commits pequenos e atômicos, de baixo para cima (repository → service → router → teste), cada um passando no `make check`; versão do serviço subida num commit próprio.
5. PRs **empilhados**: cada branch sai da ponta da anterior; base do PR = a branch de baixo; `git rebase --update-refs` leva a pilha junto.
6. Notas do vault (este Obsidian) no último commit `[docs]` da branch.

## Fontes da verdade

- Estado atual = o código; porquê = o vault; API de uma lib = o código instalado (`.d.ts`, `site-packages`), nunca a memória do modelo. O que se descobre de uma lib vira card em `ai/kb/libs/`.

## Se perguntarem

- **"Você usou IA para escrever o código?"** Sim, com divisão clara: as partes de aprendizado escritas à mão, o resto gerado e revisado; regras de arquitetura garantidas por lint e testes, não por confiança.
- **"Como garante qualidade do código gerado?"** mypy strict, testes com banco real, lint de arquitetura, commits pequenos revisáveis e PR por serviço.
