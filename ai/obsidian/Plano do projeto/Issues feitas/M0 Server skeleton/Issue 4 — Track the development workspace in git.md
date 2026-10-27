---
tags: [noteproject, plano, workspace]
---
# #4 Track the development workspace in git

Issue do [[M0 Server skeleton]]. Põe o workspace de IA (`CLAUDE.md`, `.claude/`, `ai/`) no git, separado do código do app. Passou por git: commit atômico, fixup, tags e arquivo gerado.

## Git

- Commit atômico: uma mudança por commit, e cada um passa no `make check` ([[Regras de git]]).
- Conserto de commit ainda não enviado vai por `fixup!` + rebase no original, não por commit novo.
- A tag no título (`[docs]`, `[ai-workspace]`) separa o que é do workspace do que é do app.
- Arquivo gerado (`ai/build/`) fica fora do git: o que se recria a partir do código não se versiona.
