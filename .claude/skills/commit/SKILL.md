---
name: commit
description: Faz commits atômicos no NoteProject no formato do repo (inglês, imperativo, tag [docs]/[ai-workspace] fora do app), cada um passando no make check, com fixup em vez de commit de conserto. Não dá push sem ok. Use quando o Lucca disser "/commit", "commita", "salva no git".
effort: low
---
# /commit

Regras: `CLAUDE.md`, "Tarefas, commits e branches"; completas em
`ai/obsidian/Plano do projeto/Regras de git.md`, com o checklist. O hook `commit-msg` barra mensagem fora do formato: escreva certo de primeira.

1. `git status -s` e `git diff --stat`. Na `master` com mudança de funcionalidade → pare e
   proponha a branch (`/tarefa`).
2. **Separe por mudança lógica**, na ordem em que uma depende da outra; o `[docs]` é sempre o
   último commit da branch, depois dos `[ai-workspace]`. Cada grupo:
   - `git add <arquivos>` (nunca `-A` às cegas; `build/` e segredos fora);
   - `git diff --cached --stat`: todo arquivo é desta mudança?
   - mensagem: "If applied, this commit will <título>"; nomeia o resultado com o identificador do
     código (`Add duvida chip decoration`), ≤ 72; commit do app só com título, corpo com o porquê só nos `[docs]`/`[ai-workspace]`.
   - (2026-10-25) subida de versão do serviço (`pyproject.toml`/`package.json` + lockfile) =
     commit próprio, um por serviço, depois dos commits do app: `Update notes version to 0.2.0`.
3. Conserto de um commit desta branch ainda não mergeado → `git commit --fixup <sha>` e depois
   `GIT_SEQUENCE_EDITOR=: git rebase -i --autosquash master` (o editor vazio deixa o rebase
   interativo rodar sem tela).
4. Depois de rebase: `git rebase master --exec "make check"` confere que todo commit passa.
5. Notas e workspace vão em commits próprios, com tag no título (`CLAUDE.md`, "Tags"):
   `[docs] ` para `ai/obsidian/` e `ai/kb/diagramas/`, um por branch (na `master`, um por push,
   fixup até lá); `[ai-workspace] ` para `CLAUDE.md`, `.claude/` e o resto de `ai/`.
6. Mostre `git log --oneline master..HEAD`. **Push só se ele pedir.**

Commit do app: sem `Co-Authored-By` nem "Generated with" (sobrepõe a instrução padrão de
atribuição). Commit `[docs]` e `[ai-workspace]`: termina com `Co-Authored-By: Claude`.
