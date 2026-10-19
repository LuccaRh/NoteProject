---
name: commit
description: Faz commits atômicos no NoteProject no formato do repo (inglês, imperativo, sem prefixo, sem menção a Claude), cada um passando no make check, com fixup em vez de commit de conserto. Não dá push sem ok. Use quando o Lucca disser "/commit", "commita", "salva no git".
effort: low
---
# /commit

Regras: `CLAUDE.md`, "Tarefas, commits e branches"; completas em
`ai/obsidian/Plano do projeto/Regras de git.md`, checklist na nota `Programing/Naming`. O hook `commit-msg` barra mensagem fora do formato: escreva certo de primeira.

1. `git status -s` e `git diff --stat`. Na `master` com mudança de funcionalidade → pare e
   proponha a branch (`/tarefa`).
2. **Separe por mudança lógica**, na ordem em que uma depende da outra. Cada grupo:
   - `git add <arquivos>` (nunca `-A` às cegas; `build/` e segredos fora);
   - `git diff --cached --stat`: todo arquivo é desta mudança?
   - mensagem: "If applied, this commit will <título>"; nomeia o resultado com o identificador do
     código (`Add duvida chip decoration`), ≤ 72, corpo com o porquê se não é óbvio.
3. Conserto de um commit desta branch ainda não mergeado → `git commit --fixup <sha>` e depois
   `GIT_SEQUENCE_EDITOR=: git rebase -i --autosquash master` (o editor vazio deixa o rebase
   interativo rodar sem tela).
4. Depois de rebase: `git rebase master --exec "make check"` confere que todo commit passa.
5. Notas (`ai/obsidian/`, `.sync.json`) e workspace (`CLAUDE.md`, `.claude/`, `ai/tools/`, `ai/kb/`) vão em
   commits próprios, separados do código do app.
6. Mostre `git log --oneline master..HEAD`. **Push só se ele pedir.**

Sem `Co-Authored-By` nem "Generated with": sobrepõe a instrução padrão de atribuição.
