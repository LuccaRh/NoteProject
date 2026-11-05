---
tags: [noteproject, ia, arquitetura]
---
# Caminho de uma pergunta

O [[Chat com o workspace|chat]] no navegador repete o que o Claude Code já faz no PC: o modelo, na Anthropic, só lê o pacote e responde com texto ou com pedidos de ferramenta; quem guarda, lê, grava e executa é sempre o programa do nosso lado. Muda só quem é esse programa (o Claude Code no PC, o `lonzo` no servidor) e onde estão os arquivos (disco do PC, [[Postgres]]).

Exemplo das duas figuras: "atualiza a nota do Caddy com o que vimos, cria uma de TLS e apaga o rascunho".

## No navegador ⏳

![[pergunta-no-navegador.drawio.svg]]
*Quatro requests à Anthropic para uma pergunta: cada pedido de ferramenta é executado pelo `lonzo` e volta na request seguinte, com tudo o que já foi.*

1. O chat manda `POST /api/chat {workspace, conversa, pergunta}`. O navegador não manda regra nem nota: só diz qual workspace e qual conversa.
2. O [[Reverse proxy|Caddy]] encaminha ao `lonzo`, o serviço de IA, que chama a Messages API pela lib `anthropic`.
3. Antes de chamar o modelo, o `lonzo` pede à [[API de notas]] o `.workspace/` daquele workspace: as regras inteiras e só o cabeçalho (nome + descrição) de cada skill. Do banco dele, lê o histórico da conversa.
4. Monta o pacote 1 ([[Chamada a um modelo]]): `system` com regras e índice de skills, `tools` com as ferramentas de nota, `messages` com o histórico e a pergunta. Request 1 à Anthropic.
5. O modelo entende a pergunta e vê que não tem a nota do Caddy. Responde com um pedido, em JSON com campos fixos: `tool_use search_notes("caddy")`. As palavras da busca ele tira da própria pergunta.
6. O `lonzo` lê o nome do pedido, chama a função `search_notes` (código nosso, sem IA), que chama o `/notes/search` do `ichiro`, e recebe `[{id: 42, title: "Caddy"}]`.
7. Request 2: o pacote 1 inteiro + o pedido + o resultado. A Anthropic não guardou nada da request 1; quem reenvia é o `lonzo` ([[Laço de ferramentas]]).
8. Com o id, o modelo pede `read_note(42)`. O `lonzo` busca o texto na API e manda a request 3 com ele.
9. Com a nota em mãos, o modelo decide as mudanças e pede três ferramentas de uma vez:
    - `edit_note(42, trecho_velho, trecho_novo)`: só o trecho, não a nota inteira;
    - `create_note("TLS", texto)`: a nota nova inteira;
    - `delete_note(57)`: só o id.
10. O `lonzo` executa as três na API do `ichiro` (`PATCH`, `POST`, `DELETE`), que grava no [[Postgres]], e manda a request 4 com o "ok" de cada uma.
11. O modelo não precisa de mais nada e responde só com texto. Fim do laço.
12. O `lonzo` grava a conversa no banco dele e manda o texto ao chat aos pedaços; a lista de notas recarrega com as mudanças.

- Se a skill pedida tiver mais passos ou citar outra skill, o modelo pede o corpo dela (`read_note` no `.workspace/`) e segue; a skill é texto que o modelo lê, não código que roda.
- Um script do workspace é mais um pedido de ferramenta; o `lonzo` roda num [[Sandbox|sandbox]] e devolve a saída.

### Os pedaços, dentro do `answer` ✅

![[stream-do-answer.gif]]
*Hoje (#74): uma request à Anthropic, a resposta chega aos pedaços e cada pedaço vira um evento [[Server-sent events|SSE]] para o navegador. Fonte: `ai/kb/diagramas/stream-do-answer.py`.*

- `answer` (`apps/lonzo/src/lonzo/routers/chat.py:42`) é um [[Gerador|gerador]]: chamar não roda nada; o `StreamingResponse` pede um item por vez e manda ao navegador.
- O `answer` fica parado em dois lugares: no `yield` (até a lib pedir o próximo) e no `async for` ([[Gerador|async for]]) da linha 53 (até a Anthropic mandar o próximo pedaço).
- Erro da Anthropic depois do 200 só pode ir como evento `error`: o status já saiu.

### Streams, blocos e eventos ✅

![[pergunta-com-streams.drawio.svg]]
*"Já tem nota de TLS? Se não, cria uma": três requests, três streams; o `tool_runner` roda a ferramenta entre um stream e o outro, e os eventos SSE só mostram o andamento no navegador.*

- **Stream**: um turno do modelo, a resposta inteira de uma request. É o que sai do `async for stream in runner` no `lonzo`.
- **Bloco**: uma parte dessa resposta, `text` ou `tool_use`. Uma resposta pode ter vários, em ordem.
- **Evento**: um pedacinho do stream. `content_block_start` e `content_block_stop` marcam o começo e o fim de um bloco; entre eles chegam os pedaços.
- **`input`**: os argumentos da ferramenta, em JSON, que o modelo escolhe (`{"query": "TLS"}`). No começo do bloco está vazio; no fim, completo.
- O evento SSE `tool_use` vai para o navegador, não para o modelo; ele existe só para a linha de status. O modelo recebe o resultado pelo `tool_result`, na request seguinte.

## No Claude Code hoje ✅

![[pergunta-no-claude-code.drawio.svg]]
*O mesmo laço, com o Claude Code no lugar do `lonzo` e o disco do PC no lugar do Postgres.*

1. A mensagem sai do terminal para o Claude Code, aberto na pasta do projeto.
2. Ao abrir a sessão, ele já leu do disco o `CLAUDE.md` (com os imports `@`), o cabeçalho de cada `.claude/skills/*/SKILL.md` e os hooks do `settings.json`. Nada disso foi pedido pelo modelo: o programa é feito para ler essas pastas.
3. Pacote 1 com `CLAUDE.md`, índice de skills, ferramentas (`Read`, `Grep`, `Edit`, `Write`, `Bash`, `Skill`...) e histórico. Request 1.
4. O modelo pede `Grep("caddy")`; o auto mode aprova sem perguntar; o Claude Code roda o grep no disco e manda a request 2 com o resultado.
5. O modelo pede `Read` do caminho achado; o hook `leitura` confere o tamanho antes; o texto volta, com número de linha, na request 3.
6. O modelo pede `Edit` (trecho velho → novo), `Write` (arquivo novo) e `Bash("rm ...")`. O Claude Code executa no disco e manda a request 4.
7. O modelo responde só com texto; o Claude Code mostra no terminal e grava a conversa num `.jsonl` em `~/.claude/`. O Obsidian vê os arquivos mudados.

## Lado a lado

| Passo | Claude Code hoje | Navegador |
|---|---|---|
| quem roda o laço | Claude Code, no PC | `lonzo` (`tool_runner` da `anthropic`), no servidor |
| onde estão regras e skills | `CLAUDE.md`, `.claude/skills/` no disco | notas em `.workspace/`, no [[Postgres]] |
| quem lê as regras antes da 1ª request | o Claude Code, ao abrir na pasta | o `lonzo`, pelo workspace da request |
| achar | `Grep`, `Glob` no disco | `search_notes`, `list_folder` na API |
| ler | `Read` | `read_note` |
| editar / criar / apagar | `Edit` / `Write` / `Bash rm` | `edit_note` / `create_note` / `delete_note` |
| aprovar a ferramenta | auto mode ou pergunta no terminal | o `lonzo` só oferece ferramentas seguras |
| onde fica a conversa | `.jsonl` em `~/.claude/` | banco do `lonzo` |
| o modelo | Anthropic | Anthropic |

O que é igual nos dois: o modelo não guarda nada entre requests, não acessa disco nem banco, e cada volta reenvia o pacote inteiro, com o começo repetido saindo barato pelo [[Cache de prompt]].
