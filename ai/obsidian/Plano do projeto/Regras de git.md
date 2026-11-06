---
tags: [noteproject, plano, workspace]
---
# Regras de git

O histórico serve para alguém (inclusive o próprio autor, meses depois) entender o que mudou e por quê, e para dar `revert` ou `rebase` sem medo. Estas regras partem das convenções comuns de mensagem de commit e acrescentam o que é do NoteProject (issues, `make check`).

## Branch

- **Branch = uma funcionalidade = uma issue** ([[Tarefas no GitHub]]). Inglês, kebab-case, sem prefixo de tipo (`feat/`), nomeia o propósito.
- (2026-10-25) **Prefixo = o serviço**: `<serviço>/<kebab>`, como `notes/expose-the-notes-api-on-the-server`. Serviço = pasta de `apps/` (`ichiro`, `chimchar`), ou `postgres` (o container do compose; a config dele vai numa pasta própria). Branch sem serviço usa o lado do projeto: `infra/` para issue `infrastructure` sem container (CI, Terraform, AWS: #17–#21, #23) e `workspace/` para issue `ai-workspace`; container novo (Caddy) ganha o próprio nome. Colchete não serve: o git não aceita `[` em nome de branch.
- (2026-10-25) **Um serviço por branch**: issue que mexe em vários serviços vira um PR por serviço, todos com a mesma issue. Alembic e migrations são código do `ichiro`. Commits `[docs]` e `[ai-workspace]` entram em qualquer branch. O lint W13 confere.
- Sai da `master` atualizada: `git fetch && git switch master && git pull --ff-only`. Com branch em aberto, sai da ponta da pilha.
- (2026-11-05) **Branches empilhadas**: com branch ou PR em aberto, a branch nova sai da ponta da última e todas formam uma fila só sobre a `master`, para dar stack. Mudou uma branch de baixo → `git rebase --update-refs` na ponta leva as de cima junto; depois de merge, a pilha é rebaseada na `master`.
- Nada de várias branches mudando a mesma coisa de jeitos diferentes. Na dúvida entre dois jeitos: uma branch para cada, mergeia a escolhida e apaga a outra.
- (2026-10-23) **Branch que mexe num serviço sobe a versão dele**: `apps/<serviço>/` mexido → a minor do `pyproject.toml` (ou `package.json`) sobe um em relação à `master` (`0.1.0` → `0.2.0`), e o lockfile vai junto (`uv lock`, `npm install`). A versão diz em qual issue o serviço está. O lint W11 confere.
- (2026-10-25) **Versão num commit só dela**: um por serviço, depois dos commits do app da branch, com o manifesto e o lockfile e nada mais: `Update notes version to 0.2.0`. O `revert` de uma mudança não mexe na versão, e o histórico mostra quando cada serviço subiu.

## Commit

- **Commit = uma mudança nova.** Conserto de commit ainda não mergeado entra nele (`--fixup` + `rebase --autosquash`); a branch mostra só a versão final. "Mergeado" = já enviado ao remoto: o que só está na `master` local também é consertado no commit de origem (rebase), inclusive troca de nome, de língua ou de config. Mudar o que já está na `master` remota é mudança nova.
- **Atômico e cronológico**: uma mudança lógica por commit, na ordem em que uma depende da outra, e **todo commit passa no `make check`** (conferir com `git rebase master --exec "make check"`).
- (2026-11-02) **Commit pequeno**: dependência, config (compose), módulo novo, o uso dele na rota, handler de erro e testes novos vão em commits separados. A #74 teve 12 commits no app; a #73, depois de refeita, 13. Commit que junta rota, cliente e testes, ou várias camadas, está grande demais.
- (2026-11-02) **Teste em commit próprio**: o teste novo, com o fake que só ele usa, vai num commit `Test ...` logo depois do código que ele testa. No commit do código fica só o ajuste de teste antigo que a mudança quebraria (import, override de dependência), senão ele não passa no `make check`.
- **Ordem dentro da branch** (cada camada depende só das de baixo): schema/[[Migration|migration]] → regra (`repo.py`, serviço) → rota da API → cliente/front → `[ai-workspace]` → `[docs]`. (2026-10-27) O `[docs]` é sempre o último commit da branch.
- (2026-10-30) **README vai no `[docs]` da branch**, junto com as notas: o commit do app fica só com o código e a config.
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
| `[docs] ` | notas do vault, fontes das figuras (`ai/kb/diagramas/`) e o `README.md` | um por branch; a `master` só recebe PR (2026-11-06, ruleset `Master Rules`) |
| `[ai-workspace] ` | `CLAUDE.md`, `.claude/`, o resto de `ai/` | as normais |
| sem tag | código do app, Makefile | as normais |

- `[docs]` não segue o "uma mudança, um commit": é o que mudou nas notas durante a branch. Título `[docs] Add <assuntos>` ou `[docs] Update <assuntos>`.
- Só os commits com tag levam `Co-Authored-By: Claude`; os do app, nunca.

## Língua e data

- **Código em inglês**: tudo em `apps/`, `Makefile`, compose, CI e README (comentário, docstring, mensagem de erro, texto da interface, dado de teste), além de commit, branch, issue e PR. Português só no workspace (`ai/`, `.claude/`, `CLAUDE.md`) e no vault. O lint W09 confere.
- **Data real**: a data do commit é a hora em que ele foi feito. Nada de `--date` nem de `GIT_AUTHOR_DATE`/`GIT_COMMITTER_DATE`; reescrever história (rebase) também usa a hora do momento (`--reset-author-date`).

Checklist da mensagem de commit:

| Pergunta | ✗ | ✓ |
|---|---|---|
| "If applied, this commit will …" lê certo? | `Added token check` | `Reject requests without a device token` |
| nomeia o resultado, não o mecanismo? | `Add dict for query params` | `Filter notes by folder` |
| usa o identificador do código? | `Add id of parent` | `Add parent_id to notes` |
| tem "and"? então são dois commits | `Add Postgres and Caddy` | dois commits |
| o verbo bate? `Add/Remove` = código; `Stop/Start/Allow/Prevent` = comportamento | `Remove token from log` (ainda existe) | `Stop logging device tokens` |

## PR e merge

- Título em inglês, passa pela `/escrita` (texto público). (2026-10-26) Corpo só `Issue #N`, nada mais.
- (2026-11-05) **Base do PR = a branch de baixo da pilha**; a primeira aponta para a `master`.
- Antes do push: `git log --oneline master..HEAD` revisado. Push e PR só com ok; force só quando pedido, sempre `--force-with-lease`.
- Merge com **merge commit** (não squash): os commits atômicos ficam, e `git log --first-parent master` lê como uma linha por funcionalidade.
- Nada de Claude/Anthropic/IA em mensagem, branch, issue ou PR; sem `Co-Authored-By` nem "Generated with".

## Revisar se...

- Outra pessoa entrar no projeto: só os próprios commits podem ser reescritos.
- O histórico com merge commits ficar confuso: trocar por *rebase and merge*.
