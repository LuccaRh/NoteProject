---
tags: [noteproject, plano, workspace]
---
# Regras de git

O histórico serve para alguém (inclusive o próprio autor, meses depois) entender o que mudou e por quê, e para dar `revert` ou `rebase` sem medo. Estas regras partem do [[Naming#Commit naming|Commit naming]] e acrescentam o que é do NoteProject (issues, `make check`).

## Branch

- **Branch = uma funcionalidade = uma issue** ([[Tarefas no GitHub]]). Inglês, kebab-case, sem prefixo (`feat/`), nomeia o propósito: `add-postgres-with-migrations`.
- Sai da `master` atualizada: `git fetch && git switch master && git pull --ff-only`.
- Nada de várias branches mudando a mesma coisa de jeitos diferentes. Na dúvida entre dois jeitos: uma branch para cada, mergeia a escolhida e apaga a outra.

## Commit

- **Commit = uma mudança nova.** Conserto de commit ainda não mergeado entra nele (`--fixup` + `rebase --autosquash`); a branch mostra só a versão final. "Mergeado" = já enviado ao remoto: o que só está na `master` local também é consertado no commit de origem (rebase), inclusive troca de nome, de língua ou de config. Mudar o que já está na `master` remota é mudança nova.
- **Atômico e cronológico**: uma mudança lógica por commit, na ordem em que uma depende da outra, e **todo commit passa no `make check`** (conferir com `git rebase master --exec "make check"`).
- **Ordem dentro da branch** (cada camada depende só das de baixo): schema/[[Postgres e migrations|migration]] → regra (`repo.py`, serviço) → rota da API → cliente/front → docs e notas.
- Arquivo com duas mudanças → `git add -p`. Notas e workspace em commits próprios, separados do app.
- Autor = git user próprio; nunca mudar `user.name`/`user.email`.

## Mensagem

Formato (o hook `commit-msg` barra o que fugir dele):

- inglês, imperativo, maiúscula, sem ponto final, ≤ 72 caracteres (mirar ~50), sem prefixo (`feat:`, `fix:`);
- (2026-10-21) **commit do app só com título**; corpo (separado por linha em branco, com o **porquê**) só nos commits `[docs]` e `[ai-workspace]`;
- descreve o estado final, não o processo: nada de `wip`, `fix`, `update`, "for now", "stop doing X";
- sem número de issue na mensagem: a ligação com a issue fica no PR.

Tags (2026-10-19), no começo do título dos commits fora do app:

| Tag | O que entra | Regra |
|---|---|---|
| `[docs] ` | notas do vault e fontes das figuras (`ai/kb/diagramas/`) | um por branch; na `master`, um por push |
| `[ai-workspace] ` | `CLAUDE.md`, `.claude/`, o resto de `ai/` | as normais |
| sem tag | código do app, README, Makefile | as normais |

- `[docs]` não segue o "uma mudança, um commit": é o que mudou nas notas durante a branch. Título `[docs] Add <assuntos>` ou `[docs] Update <assuntos>`.
- Só os commits com tag levam `Co-Authored-By: Claude`; os do app, nunca.

## Língua e data

- **Código em inglês**: tudo em `apps/`, `Makefile`, compose, CI e README (comentário, docstring, mensagem de erro, texto da interface, dado de teste), além de commit, branch, issue e PR. Português só no workspace (`ai/`, `.claude/`, `CLAUDE.md`) e no vault. O lint W09 confere.
- **Data real**: a data do commit é a hora em que ele foi feito. Nada de `--date` nem de `GIT_AUTHOR_DATE`/`GIT_COMMITTER_DATE`; reescrever história (rebase) também usa a hora do momento (`--reset-author-date`).

Checklist do [[Naming#Commit naming|Commit naming]]:

| Pergunta | ✗ | ✓ |
|---|---|---|
| "If applied, this commit will …" lê certo? | `Added token check` | `Reject requests without a device token` |
| nomeia o resultado, não o mecanismo? | `Add dict for query params` | `Filter notes by folder` |
| usa o identificador do código? | `Add id of parent` | `Add parent_id to notes` |
| tem "and"? então são dois commits | `Add Postgres and Caddy` | dois commits |
| o verbo bate? `Add/Remove` = código; `Stop/Start/Allow/Prevent` = comportamento | `Remove token from log` (ainda existe) | `Stop logging device tokens` |

## PR e merge

- Título e corpo em inglês; corpo com `Closes #N` e passa pela `/escrita` (texto público).
- Antes do push: `git log --oneline master..HEAD` revisado. Push e PR só com ok; force só quando pedido, sempre `--force-with-lease`.
- Merge com **merge commit** (não squash): os commits atômicos ficam, e `git log --first-parent master` lê como uma linha por funcionalidade.
- Nada de Claude/Anthropic/IA em mensagem, branch, issue ou PR; sem `Co-Authored-By` nem "Generated with".

## Revisar se...

- Outra pessoa entrar no projeto: só os próprios commits podem ser reescritos.
- O histórico com merge commits ficar confuso: trocar por *rebase and merge*.
