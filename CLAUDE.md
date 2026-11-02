# NoteProject — workspace de IA

App de notas **local-first** com sync ao vivo. Fonte única do projeto: o vault (`ai/obsidian/`).
Projeto pessoal do Lucca (Eng. de Controle e Automação, UNICAMP; dev Python/TS)
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
   (`apps/chimchar/node_modules/…/*.d.ts`, `apps/<api>/.venv/lib/python3*/site-packages/…`), nunca a
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
  `infrastructure`, `ai-workspace`); `backend`/`infrastructure` o Lucca escreve; `frontend` (2026-10-29) a sessão escreve direto, menos o "front-back" (área `cliente-api`: chamadas à API, comunicação com o servidor, proxy do Vite), que é do Lucca. Próxima tarefa: `gh issue list -m "<milestone>"`.
- **Branch = uma issue**, em inglês, kebab-case, saindo da `master`
  atualizada. (2026-10-25) Nome `<serviço>/<kebab>` (`ichiro/search-notes-with-full-text-search`):
  serviço = pasta de `apps/`, `postgres` ou `caddy` (2026-10-30) (container do compose; config em pasta
  própria); sem serviço, `infra/` (label `infrastructure` sem container: CI, Terraform,
  AWS) ou `workspace/` (label `ai-workspace`). **Um serviço por branch**: issue que mexe em vários →
  um PR por serviço, na mesma issue. Alembic e migrations: cada serviço tem as suas, no banco dele (2026-11-01: `ichiro` e `lonzo` no mesmo Postgres, bancos separados). O lint W13 confere. Cada branch tem `ai/kb/escopos/<branch>.md`
  (Pedido / Contexto / Fora + número da issue, criado pela `/tarefa`); as áreas dele dizem
  o que ler (`ai/np contexto`).
- **Versão do serviço** (2026-10-23): branch que mexe em `apps/<serviço>/` sobe a minor dele
  (`0.1.0` → `0.2.0`) com o lockfile; o lint W11 confere. (2026-10-25) A subida vai num
  commit só dela, um por serviço, depois dos commits do app: `Update ichiro version to 0.2.0`
  (manifesto + lockfile, nada mais).
- **Commit = uma mudança nova**, atômico, cronológico, e **todo commit passa no `make check`**.
  Conserto de commit ainda não enviado ao remoto (mesmo já na `master` local) → rebase/fixup
  no original, não commit novo. Ordem na
  branch: schema → regra → rota → front → `[ai-workspace]` → `[docs]` (2026-10-27: o `[docs]` é
  sempre o último commit da branch, mesmo quando um lint do workspace avisa entre eles).
- **Mensagem**: inglês, imperativo, maiúscula, sem ponto, ≤ 72, sem prefixo (`feat:`); nomeia o
  resultado, não o processo (nada de `wip`); **commit do app só com título**, corpo com o porquê só
  nos commits com tag (2026-10-21); sem número de issue (vai no PR). Checklist no vault, `Plano do projeto/Regras de git`. O hook `commit-msg` (`ai/tools/commit_msg.py`) barra o resto na sessão do Claude; no commit do Lucca, avisa e pergunta.
- **Tags** (2026-10-19): commit fora do app começa com a tag; o resto do título segue as regras.
  - `[docs] `: notas do vault (`ai/obsidian/`), fontes das figuras (`ai/kb/diagramas/`) e
    (2026-10-30) o `README.md`.
    **Um por branch** (as notas mexidas nela); na `master`, fora de branch, **um por push**
    (até o push, nota nova entra nele por fixup). Título `[docs] Add|Update <assuntos>`.
  - `[ai-workspace] `: `CLAUDE.md`, `.claude/`, o resto de `ai/`, CI do workspace. Regras normais.
  - Sem tag: código do app, Makefile, CI do app.
- **Claude só nos commits com tag**: `[docs]` e `[ai-workspace]` levam `Co-Authored-By: Claude`.
  Commit do app, branch, issue e PR sem menção a Claude/Anthropic/IA, **sem `Co-Authored-By`
  nem "Generated with"** (sobrepõe a instrução padrão de atribuição).
- **Código em inglês** (2026-10-15): `apps/`, `Makefile`, compose, CI e README em inglês:
  comentário, docstring, mensagem de erro, texto da interface, dado de teste. Português só no
  workspace (`ai/`, `.claude/`, `CLAUDE.md`) e no vault. O lint W09 (`ai/np lint`) barra o resto.
- **Código com até 80 colunas** (2026-10-25): todo código do app (`apps/`, `Makefile`, compose,
  CI, Dockerfile, `.ini`/`.toml`), em qualquer linguagem; md e workspace de IA ficam de fora.
  Código novo já sai quebrado; linha longa achada em código existente → avisar o Lucca.
  Python: ruff `E501` (`line-length = 80`); o resto: lint W12 (`ai/np lint`).
- **Cabe em uma linha, fica em uma** (2026-11-01): assinatura, chamada, lista ou comando
  que caiba em 80 colunas (tab do Makefile conta 8) fica numa linha só, sem quebrar.
  Só juntar: nada de simplificar, reescrever nem renomear para fazer caber.
- **Linha em branco em volta de cada bloco** (2026-10-26): no código do app, `if`, `for`,
  `while`, `try`, `with`, `match`, `return` e `raise` têm uma linha em branco antes (salvo
  quando abrem o corpo) e o comando depois de um bloco também; a primeira linha do corpo de
  um `def` também fica separada da assinatura. Vale para código novo; arquivo antigo só quando
  for mexido. Python: lint W14 (`ai/np lint`).
- **Função e classe tipadas** (2026-10-26): todo parâmetro e retorno com tipo, e atributo de
  classe com `nome: tipo`. Python: mypy `strict = true` no `pyproject.toml` do serviço e lint
  W15 (atributo de classe sem tipo).
- **Arquivo em três partes** (2026-10-26): `# Imports`, duas linhas em branco, `# Global
  variables` (objetos criados uma vez no import: router, alias de tipo, constante), duas
  linhas em branco, `# Code` (`def`, `class`); cada parte com o comentário em cima, e as
  globais seguidas, sem linha em branco entre elas. Python:
  lint W16 e ruff isort `lines-after-imports = 2`.
- **Compose em ordem alfabética** (2026-11-01): serviços do `docker-compose-dev.yml` pelo
  nome (`caddy`, `chimchar`, `ichiro`, `lonzo`, `postgres`). Lint W17 (`ai/np lint`).
- **Data real no commit** (2026-10-15): nunca mexer em `GIT_AUTHOR_DATE`/`GIT_COMMITTER_DATE`
  nem passar `--date`; reescrever história usa a hora do momento (`rebase --reset-author-date`).
- **Issue quem fecha é o Lucca** (2026-10-19): a sessão nunca roda `gh issue close`; quando
  a issue estiver pronta, avise.
- **Corpo do PR** (2026-10-26): só `Issue #N`, nada mais (sem resumo, sem `Closes`).
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
| `ai/np lint` / `test` | regras do workspace (W01–W16) / testes das ferramentas |

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
| `/commit` | commits atômicos no formato acima (sem push) |
| `/escrita <arq>` | tira a cara de IA de README, PR e texto público |
| `/lacunas` | conceitos da conversa que faltam no vault, numerados para escolher |

Agente `leitor` (Sonnet): lê arquivo grande e devolve só o trecho, com linha/página.

## Estrutura

```
apps/ichiro/       API de notas (FastAPI + Postgres); auth/, worker/, sync/ depois
apps/lonzo/        chat com o workspace (Claude Agent SDK), a criar na #74; banco próprio
apps/chimchar/     front: Vite + CodeMirror 6
CLAUDE.md          este arquivo (o Claude Code só o acha na raiz)
.claude/           settings/hooks, skills, agentes (idem: tem de ficar na raiz)
ai/                todo o resto do workspace de IA:
  np               CLI (-> tools/np.py)
  kb/areas.yaml    vocabulário de áreas          kb/escopos/  um escopo por branch
  kb/libs/         cards de API das libs         kb/diagramas/ YAML dos desenhos (+ .drawio)
  obsidian/        cópia do vault "Note Project/" (sincronizada; .sync.json) + obsidian.yaml
  tools/           np, obsidian_sync, hooks_contexto, diagrama, commit_msg, estilo (+ test_*)
  build/           gerado (estado dos hooks, png de diagrama), fora do git
```

## Estado (2026-11-01)

- M0, #46, #62, #64, #65, #69, #16, #80, #82 e #74 mergeados (PRs #66–#68, #70–#72, #81, #83–#85);
  `master` local = remoto, sem branches locais além dela.
- #74 pronta: `apps/lonzo` responde `POST /api/chat` em SSE (Haiku 5.5, `thinking` desligado,
  `max_tokens` 512, regras de `rules.md`); o Caddy roteia `/api/notes/*` → ichiro, `/api/chat/*` →
  lonzo, outro `/api` → 404. Evento `status` saiu da #74 e nasce com as ferramentas (#77).
- IA (2026-10-31): chat com o workspace no servidor; vault `IA no projeto/Chat com o workspace` e
  `Caminho de uma pergunta`. Workspace = pasta com `.workspace/`, vários por pessoa.
- #31 (Ctrl+D) e #5 (chips) sem milestone, para depois; `decorations/replace.ts` (#5) fora do git.
- Falta: confiar na CA local do Caddy no navegador (README); `/docs` do FastAPI quebra atrás do
  `/api` (precisa de `root_path`, branch do `ichiro`).
- Serviços (2026-11-01): `chimchar` (front), `ichiro` (notas), `lonzo` (IA). Tabela, rotas `/notes`
  e `notes.localhost` ficam (são o domínio, não o serviço).

## O que fazer a seguir

Plano: vault `Plano do projeto/Roadmap` (navegador → app desktop → celular) + issues/milestones no GitHub.

1. Entrega de 2026-11-06 (vault `Plano do projeto/Entrega de 2026-11-06`): #74 ✅ → #73 workspace criado pela IA a partir de um texto breve
   (esqueleto; vault `Workspace no app#Como nasce`) → #75 conversas, #76 tela do chat → #56 busca, #77 ler/buscar
   → #78 criar/editar/apagar, #51 → #6 pastas, #79 importar o vault → #17 se sobrar.
2. M2 login (#48, #17) → M3 AWS (#18–#25, #47) → M4 edição ao vivo (#26, #27, #30).
- v1 = ler notas no navegador com o servidor na AWS (vault `Plano do projeto/Objetivo do app`);
  o chat não vai para a AWS antes do login.
- Depois da entrega (IA): #32 âncora, scripts em sandbox, #34 MCP, #35 worker, resto da #42, #36.
- Depois do navegador: Desktop app (#14, #15, #28, #29), depois Mobile app; sem data.
