---
tags: [noteproject, editor, ui, cliente-api]
---
# Front — editor e UI

O front é o que se vê: a lista de notas e o editor. A regra que manda nele: **nada do caminho de digitação espera a rede** ([[Local-first|local-first]]).

![[estrutura-front.drawio.svg]]
*Módulos de `apps/web/src` hoje: só o editor; ainda não há rede.*

## O que existe (✅)

| Módulo | Faz |
|---|---|
| `main.ts` | monta o editor no `#editor` (`main.ts:4-7`) |
| `editor.ts` | [[CodeMirror\|CodeMirror 6]] com Markdown |
| `decorations/headings.ts` | headings com tamanho; `replace.ts` (chips de `[!duvida]`) está vazio |

- Stack: TypeScript + Vite + [[CodeMirror|CodeMirror 6]], sem framework de UI.
- Ordem para ler o código: [[Como ler o front]].
- Nada é salvo ainda: lista de notas e cliente da API vêm com o servidor (M1).

### Decorações

| O quê | [[CodeMirror\|Tipo]] | Estado |
|---|---|---|
| headings com tamanho | `line` (`decorations/headings.ts:8`) | ✅ |
| chip de `[!duvida]` e `[fix]` | `replace` (`decorations/replace.ts`, #5) | ⏳ |
| figura no lugar de `![[...]]` | `replace` | ⏳ [[Figuras geradas]] |

- É o que faz o [[Marcador no texto, conteúdo fora]] funcionar: o texto guarda o marcador, a tela mostra a coisa.

## O que está planejado (⏳)

| Peça | Para quê |
|---|---|
| lista de notas (sidebar) | abrir, criar e apagar notas (M1, #62) |
| cliente da API (`api.ts`) | única porta do front para a rede; trocar HTTP por Tauri mexe só nele |
| `/api` pelo Caddy | o [[Reverse proxy\|Caddy]] do compose repassa ao serviço `notes:8000`, na mesma origem do front, sem [[CORS]]; o Vite não tem mais proxy |
| Tauri | casca desktop leve (5–15 MB × 150–200 MB do Electron) |
| [[Yjs]] + `y-codemirror.next` | o editor gera updates de [[CRDT]] para o sync |
| KaTeX | fórmulas `$$…$$` |
| índice fuzzy em memória | `Ctrl+P` em < 1 ms |
| Svelte ou React | palette, abas, outline; **em aberto** |
| React Native | app do celular, [[Local-first\|local-first]] (milestone Mobile app) |

- Busca em 4 níveis: `Ctrl+F` no [[CodeMirror]], `Ctrl+J` outline, `Ctrl+P` fuzzy, `Ctrl+Shift+F` na busca full-text do servidor (no desktop, o [[FTS5]] do [[O daemon notesd|daemon]]).

## Fronteira com o back

- No [[Navegador|navegador]], quem serve o build e responde `/api` é o servidor. A tela usa [[UI otimista]]: mostra a edição antes da resposta e desfaz se o servidor recusar.
- No app desktop, o front só fala com o [[O daemon notesd|daemon]] local, que responde as mesmas rotas; o cliente da API não muda ([[Back — daemon e servidor]]).
- No app desktop não existe o Vite: quem serve o build é o próprio [[O daemon notesd|daemon]] ou o Tauri. Esse ponto ainda não está decidido.
