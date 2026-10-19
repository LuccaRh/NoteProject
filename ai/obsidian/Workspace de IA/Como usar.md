---
tags: [noteproject, workspace]
---
# Workspace de IA — como usar

O repo `~/Documents/NoteProject` tem um workspace de IA: um
`CLAUDE.md` curto, um vocabulário fechado de áreas, skills para cada fluxo e hooks que seguram o gasto de tokens. Abra o Claude Code na raiz do repo. [[00 Mapa — Estrutura do projeto]] Na raiz ficam só `CLAUDE.md` e `.claude/`, porque o Claude Code só os procura ali; todo o resto (ferramentas, `kb/`, esta cópia do vault) mora em `ai/`.

![[workspace.drawio.svg]]
*Do pedido à resposta: o hook de foco olha a branch, a sessão lê só o que a área lista.*

## Por que assim

| Ideia | Como aparece aqui | Ganho |
|---|---|---|
| Contexto curto e fixo | `ai/kb/areas.yaml` + `ai/np contexto <área>` | lê 3–6 arquivos, não o repo |
| Fonte → card → resposta | `ai/kb/libs/<lib>.md` destilado do `.d.ts` instalado, com versão | API certa sem reler a lib; o lint avisa quando a versão muda |
| Regra vira lint | `ai/np lint` (W01–W10), `commit_msg.py`, ruff/mypy/tsc | regra que não gasta token em toda chamada |
| Ler trecho | hook `leitura` barra Read > 400 linhas; agente `leitor` | arquivo grande não entra na sessão |
| Foco | `ai/kb/escopos/<branch>.md` + hook `foco.py` (Haiku) | branch = uma funcionalidade |
| Aprender fazendo | áreas `aprender: true` | o código de sync, auth e infra é escrito pelo Lucca |

## Comandos (`ai/np`, ferramenta `np.py`)

| Comando | Para |
|---|---|
| `ai/np status` | branch, escopo, mudanças, data do Estado, marcas pendentes |
| `ai/np contexto <área>` / `ai/np areas` | o que ler para uma área / o vocabulário |
| `ai/np obsidian` / `ai/np duvidas` | sincronia vault ↔ repo (`obsidian_sync.py`) / marcas nas notas |
| `ai/np diagrama <spec> --png` | desenho draw.io a partir de YAML (`diagrama.py`) |
| `ai/np lint` / `ai/np test` / `ai/np check` | regras do workspace / testes das ferramentas / `make check` |

Ferramentas em `ai/tools/`: `np.py`, `obsidian_sync.py`, `hooks_contexto.py` (hooks `leitura` e `aviso-clear`), `foco.py`, `diagrama.py`, `commit_msg.py` (hook `commit-msg`), `estilo.py`. Primeira vez num clone: `ai/tools/instalar.sh`.

## Skills

| Skill | Quando |
|---|---|
| `/tarefa` | começar ou continuar uma funcionalidade |
| `/aprender` | conceito novo de sistemas, com exercício no projeto |
| `/nota` | página de arquitetura ou decisão aqui no vault |
| `/diagrama` | desenho embutido numa página |
| `/duvida` | tratar `[!duvida]`, `[fix]`, `[coment]` |
| `/destrinchar` | achar o elo que falta, com perguntas |
| `/foco` | escopo da branch / conferir desvio |
| `/commit` | commits no formato do repo |
| `/escrita` | README e PR sem cara de IA |

Agente `leitor`: lê fonte de lib ou log grande e devolve só o trecho.

Próximas peças (scripts e hooks nas etapas fixas, agente `revisor`, card do front): [[Esqueleto de tarefas]].

## Marcar nas notas

```
> [!duvida] por que o token não vai num cookie?
[fix] tira a parte de Redis daqui
[coment] acho que isso deveria vir antes do sync
```
Depois, `/duvida` na sessão.

## Regras
- [[Regras de resposta]]: como as respostas no chat devem ser.
- [[Regras de página]]: como as páginas daqui são escritas.
