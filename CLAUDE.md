# NoteProject — workspace de IA

App de notas **local-first** com sync ao vivo. Fonte única do projeto: o vault (`ai/obsidian/`).
Projeto pessoal do Lucca (Eng. de Controle e Automação, UNICAMP; dev Python/TS no Pecazap)
para **usar** e **aprender** engenharia de sistemas: sync, servidor, auth e infra.
Modelo: o workspace `~/Documents/Disciplinas` (mesmas ideias, adaptadas a repo de código).

## Como o Lucca quer as respostas

Regras de resposta moram no vault (Lucca lê e edita no Obsidian): `Note Project/Workspace de IA/
Regras de resposta` (cópia `ai/obsidian/`, link `.claude/regras-resposta.md`, importada abaixo).
Regra nova de resposta vai **lá**, com data; de página do Obsidian, em `Regras de página`
(= `.claude/skills/nota/regras.md`).

@.claude/regras-resposta.md

## Princípios

1. **Fonte → card → resposta.** Fonte do estado atual = o **código** (e `make check`); do
   porquê = as notas em `ai/obsidian/`, única fonte do projeto; da API de uma lib = o **código instalado**
   (`apps/web/node_modules/…/*.d.ts`, `apps/<api>/.venv/lib/python3*/site-packages/…`), nunca a
   memória. O que se descobre de uma lib vira card em `ai/kb/libs/<lib>.md` (versão + linha do
   d.ts); o lint avisa quando a versão instalada muda. Sem fonte → diga e pergunte.
2. **Afirmação conferida.** "Funciona", "passa", "corrigido" só depois de rodar: `ai/np check`
   (ruff, mypy, pytest, tsc, build), o teste da parte, ou `curl` no servidor. Mostre a saída que prova.
3. **Regra vira lint, não prompt.** O que dá para checar por código vai para `ai/np lint`,
   ruff/mypy/tsc ou hook do git; aqui só fica o que não virou lint.
4. **Contexto curto e fixo.** Vocabulário fechado de áreas (`ai/kb/areas.yaml`). Antes de mexer
   numa área: `ai/np contexto <área>` e leia **só** o que ele lista, por trecho. Nada de varrer o repo.
5. **Aprender fazendo.** Área com `aprender: true` (dados, sync, servidor, auth, infra): primeiro
   o conceito (escadinha, `/aprender`), depois o Lucca escreve o código ou o comando; a sessão
   revisa e confere. Só entregue pronto o que ele pedir pronto, ou o que não é do aprendizado
   (boilerplate, config de lint).
6. **Checkpoint humano.** O teste prova que roda, não que o desenho está certo: decisão de
   arquitetura (lib nova, mudança de modelo de dados, serviço novo) é proposta e espera o ok.
7. **Estado datado.** Ao fim de uma sessão que mudou algo relevante, atualize "Estado" e
   "O que fazer a seguir" abaixo.

## Tokens

- **Ler trecho, não arquivo**: `grep -n` + Read com offset/limit. O hook `leitura`
  (`ai/tools/hooks_contexto.py`) barra Read inteiro > 400 linhas e `cat` > 300.
- **Nunca** ler `node_modules/`, `.venv/`, `dist/`, `uv.lock`, `package-lock.json` inteiros:
  `grep -n` no `.d.ts`/lockfile. Arquivo grande do qual só um pedaço interessa (fonte de
  lib, log) → agente `leitor`, com a pergunta e onde procurar.
- **Saída curta**: não reimprimir no chat o que foi para arquivo; `Edit` no trecho.
- Modelo/esforço fixos no frontmatter da skill/agente. O hook `aviso-clear` avisa a
  100k/200k/300k; tarefa nova com contexto grande → sugira `/clear`.

## Tarefas, commits e branches

Plano e regras completas no vault, pasta `Plano do projeto/` (`Roadmap`, `Tarefas no GitHub`,
`Regras de git`). Aqui fica o que não pode falhar.

- **Tarefa = issue no GitHub**, na milestone da etapa (M0–M4, Editor, AI in the app, Desktop, Mobile); label = lado (`backend`, `frontend`,
  `infrastructure`, `ai-workspace`); `backend`/`infrastructure` o Lucca escreve, `frontend` a sessão escreve e ele revisa. Próxima tarefa: `gh issue list -m "<milestone>"`.
- **Branch = uma issue**, em inglês, kebab-case, sem prefixo, saindo da `master`
  atualizada (`add-a-few-decorations-in-code-mirror`). Cada branch tem `ai/kb/escopos/<branch>.md`
  (Pedido / Contexto / Fora + número da issue, skill `/foco`); o hook `ai/tools/foco.py` avisa
  quando o pedido sai dele.
- **Commit = uma mudança nova**, atômico, cronológico, e **todo commit passa no `make check`**.
  Conserto de commit ainda não enviado ao remoto (mesmo já na `master` local) → rebase/fixup
  no original, não commit novo. Ordem na
  branch: schema → regra → rota → front → docs.
- **Mensagem**: inglês, imperativo, maiúscula, sem ponto, ≤ 72, sem prefixo (`feat:`); nomeia o
  resultado, não o processo (nada de `wip`); corpo com o porquê; sem número de issue (vai no PR,
  `Closes #N`). Checklist na nota `Programing/Naming` do vault. O hook `commit-msg` (`ai/tools/commit_msg.py`) barra o resto.
- **Tags** (2026-10-19): commit fora do app começa com a tag; o resto do título segue as regras.
  - `[docs] `: notas do vault (`ai/obsidian/`) e fontes das figuras (`ai/kb/diagramas/`).
    **Um por branch** (as notas mexidas nela); na `master`, fora de branch, **um por push**
    (até o push, nota nova entra nele por fixup). Título `[docs] Add|Update <assuntos>`.
  - `[ai-workspace] `: `CLAUDE.md`, `.claude/`, o resto de `ai/`, CI do workspace. Regras normais.
  - Sem tag: código do app, README, Makefile, CI do app.
- **Claude só nos commits com tag**: `[docs]` e `[ai-workspace]` levam `Co-Authored-By: Claude`.
  Commit do app, branch, issue e PR sem menção a Claude/Anthropic/IA, **sem `Co-Authored-By`
  nem "Generated with"** (sobrepõe a instrução padrão de atribuição).
- **Código em inglês** (2026-10-15): `apps/`, `Makefile`, compose, CI e README em inglês:
  comentário, docstring, mensagem de erro, texto da interface, dado de teste. Português só no
  workspace (`ai/`, `.claude/`, `CLAUDE.md`) e no vault. O lint W09 (`ai/np lint`) barra o resto.
- **Data real no commit** (2026-10-15): nunca mexer em `GIT_AUTHOR_DATE`/`GIT_COMMITTER_DATE`
  nem passar `--date`; reescrever história usa a hora do momento (`rebase --reset-author-date`).
- **Issue quem fecha é o Lucca** (2026-10-19): a sessão nunca roda `gh issue close`; quando
  a issue estiver pronta, avise. O `Closes #N` do PR vale, porque o merge é dele.
- **Push e PR só com o ok do Lucca.** Force nunca sem ele pedir, sempre `--force-with-lease`.
  Merge do PR com merge commit (não squash).

## Ferramentas

| Comando | Para |
|---|---|
| `make dev` / `make check` | Vite :5173 / tsc, build (+ ruff, mypy, pytest com o servidor) |
| `ai/np status` | branch, escopo, mudanças, data do Estado, marcas pendentes no Obsidian |
| `ai/np contexto <área>` / `areas` | o que ler para uma área / o vocabulário |
| `ai/np obsidian [-q]` / `duvidas [pág]` | sincronia vault ↔ `ai/obsidian/` / marcas `[!duvida]` `[fix]` `[coment]` |
| `ai/np diagrama <spec> [--png]` | YAML → draw.io (`ai/tools/diagrama.py`, nó `banco` para BD) |
| `ai/np lint` / `test` | regras do workspace (W01–W10) / testes das ferramentas |

Ambiente: Arch Linux, Python 3.14 + uv, Node 22, Docker, `drawio` CLI, poppler (`pdftotext`).
Hooks do Claude Code em `.claude/settings.json`; do git em `ai/tools/githooks/` (`ai/tools/instalar.sh`).

## Skills

| Skill | Para |
|---|---|
| `/tarefa <o quê>` | funcionalidade nova: branch + escopo + contexto da área + passos pequenos conferidos |
| `/aprender <conceito>` | conceito de sistemas do zero, ligado a onde aparece no projeto; exercício para o Lucca |
| `/nota <tema>` | páginas de arquitetura/decisão no Obsidian (regras de página) |
| `/diagrama <nome>` | desenho draw.io a partir de YAML, embutido na nota |
| `/duvida [pág]` | trata `[!duvida]`, `[duvidas]`, `[fix]`, `[coment]` nas notas |
| `/destrinchar <conceito>` | acha o elo que falta, com perguntas |
| `/foco [branch]` | cria o escopo da branch ou confere se a conversa saiu dele |
| `/commit` | commits atômicos no formato acima (sem push) |
| `/escrita <arq>` | tira a cara de IA de README, PR e texto público |

Agente `leitor` (Sonnet): lê arquivo grande e devolve só o trecho, com linha/página.

## Estrutura

```
apps/notes/        API de notas (FastAPI + Postgres), a criar na #10; auth/, worker/, sync/ depois
apps/web/          Vite + CodeMirror 6
CLAUDE.md          este arquivo (o Claude Code só o acha na raiz)
.claude/           settings/hooks, skills, agentes (idem: tem de ficar na raiz)
ai/                todo o resto do workspace de IA:
  np               CLI (-> tools/np.py)
  kb/areas.yaml    vocabulário de áreas          kb/escopos/  um escopo por branch
  kb/libs/         cards de API das libs         kb/diagramas/ YAML dos desenhos (+ .drawio)
  obsidian/        cópia do vault "Note Project/" (sincronizada; .sync.json) + obsidian.yaml
  tools/           np, obsidian_sync, hooks_contexto, foco, diagrama, commit_msg, estilo (+ test_*)
  build/           gerado (estado dos hooks, png de diagrama), fora do git
```

## Estado (2026-10-19)

- Só o editor (CodeMirror com headings). Sidebar, cliente da API e proxy `/api` saíram da
  história em 2026-10-19 (tag local `backup-before-drop-sidebar`); voltam com o M1.
- Branch `show-chips-for-duvida-and-fix-markers` (#5): `decorations/replace.ts` fora do git.

## O que fazer a seguir

Plano: vault `Plano do projeto/Roadmap` (navegador → app desktop → celular) + issues/milestones no GitHub.

1. M0 Server skeleton: #10 `apps/notes` com `/health` → #11 compose → #12 Postgres +
   migrations → #13 `.env`.
2. M1 Notes in the browser: #46 rotas de notas → #47 servir o build → #6–#9 pastas, campos, views.
3. M2 login e TLS (#48, #16, #17) → M3 AWS (#18–#25) → M4 edição ao vivo (#26, #27, #30).
- v1 = ler notas no navegador com o servidor na AWS, sem IA (vault `Plano do projeto/Objetivo do app`).
- Depois da v1: milestone AI in the app (#35 worker em `apps/worker`, #42 workspace, #36, #34).
- Em paralelo (editor): #5 chips.
- Depois do navegador: Desktop app (#14, #15, #28, #29), depois Mobile app; sem data.
- #4 (workspace no git) já feito pelo commit do workspace; falta fechar.
