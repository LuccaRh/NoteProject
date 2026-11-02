---
tags: [noteproject, ia, arquitetura]
---
# Chat com o workspace

Hoje a IA do projeto é o Claude Code no terminal de um PC: o contexto (regras, skills, notas) está nos arquivos daquela máquina. Do navegador ou do celular não dá para fazer a mesma pergunta com o mesmo contexto.

O chat leva as duas coisas para o servidor: o [[Workspace no app|workspace]] e a chamada ao modelo. Qualquer cliente ([[Navegador|navegador]], app desktop, celular) só mostra a conversa e manda a pergunta, e a resposta sai igual de qualquer um. Pelo mesmo chat, quem não programa pede "quero estudar cálculo" e a IA cria as regras e skills do próprio workspace.

## Vários workspaces

Cada assunto tem o seu workspace, como cada pasta de projeto no PC tem o próprio `CLAUDE.md` e `.claude/`: **workspace = qualquer pasta com um `.workspace/` dentro** (`Faculdade/`, `Baseball/`, `NoteProject/`). Um `.workspace/` na raiz faz o papel do `~/.claude/`: regras que valem em todos.

- Cada conversa pertence a um workspace; o pacote leva as regras do `.workspace` da pasta. A raiz nunca tem `.workspace` (combinado de 2026-11-02).
- Um workspace novo nasce de um texto breve ou de perguntas iniciais: a IA preenche um esqueleto fixo (objetivo, como responder, fatos fixos, estado, fontes), e skills prontas são opcionais ([[Workspace no app#Como nasce]]).

## Onde cada peça fica ⏳

| Peça | Onde | Por quê |
|---|---|---|
| workspaces (regras, skills, scripts) | [[Postgres]] do servidor, como notas: cada workspace é uma pasta com `.workspace/` dentro | o mesmo de qualquer aparelho |
| notas | [[Postgres]] do servidor | a IA lê por ferramenta |
| histórico do chat | banco `lonzo` no mesmo [[Postgres]], com usuário e [[Migration\|migrations]] próprios | a conversa começa num aparelho e continua em outro; o `ichiro` continua dono só das notas |
| [[Laço de ferramentas\|laço]] e chave da API | serviço de IA, no servidor | a chave nunca sai do servidor |
| tela do chat | cliente | só mostra e manda |

![[chat-workspace.drawio.svg]]
*Uma pergunta: o serviço de IA monta o pacote, chama a Anthropic e, a cada pedido de ferramenta, lê a nota pelo `ichiro` e chama de novo.*

## Conversas no banco

Banco `lonzo`, com usuário próprio, criado na primeira subida do [[Postgres]] (`postgres/init/`); as tabelas vêm da [[Migration|migration]] do lonzo (#75).

![[bancos-e-tabelas.drawio.svg]]
*Um Postgres, dois bancos: cada serviço só faz SQL no seu; `folder_id` aponta para `notes.id` sem FK, e o lonzo chega às notas por HTTP.*

| Tabela | Uma linha por | Colunas |
|---|---|---|
| `conversations` | conversa | `id` (uuidv7), `folder_id` (o workspace; nulo = raiz; sem chave estrangeira, a pasta mora no banco do `ichiro`), `title` (começo da 1ª pergunta), `created_at`, `updated_at` |
| `messages` | mensagem | `id` (uuidv7: ordena a conversa), `conversation_id` (apagar a conversa apaga as mensagens), `role` (`user`/`assistant`), `content` (jsonb: os blocos da Messages API, devolvidos ao modelo como estão), `created_at` |

- `POST /api/chat` sem `conversation_id` cria a conversa e devolve o id no primeiro evento; com ele, manda o histórico antes da pergunta.
- Pergunta e resposta são gravadas juntas, no fim da resposta; erro no meio não grava nada.
- `content` em jsonb e não texto: com as ferramentas (#77), a resposta traz blocos `tool_use`/`tool_result`, e a tabela não muda.

## Uma pergunta

O passo a passo completo, com edição, criação e remoção de notas e a comparação com o Claude Code, está em [[Caminho de uma pergunta]].

1. O cliente manda `POST /api/chat {workspace, conversa, pergunta}`; o [[Reverse proxy|Caddy]] encaminha ao serviço de IA.
2. O serviço lê as regras e o índice de skills do `.workspace/` daquele workspace e o histórico da conversa, e monta a [[Chamada a um modelo|chamada ao modelo]].
3. Se o modelo pede ferramenta, o serviço executa e chama de novo ([[Laço de ferramentas]]), até vir só texto.
4. O texto volta ao cliente aos pedaços, enquanto é gerado, e a conversa é gravada no banco do `lonzo`.

O chat chama o modelo direto, sem passar pela [[Fila de pedidos]]: alguém está esperando a resposta. A fila fica para pedidos em segundo plano.

## Ferramentas

Todas rodam no serviço de IA, `apps/lonzo`, em [[Container|container]] próprio: ele chama a Messages API pela lib `anthropic`, e a chave da API fica só nele. O harness é o `tool_runner` da mesma lib, com as ferramentas do app como funções ([[Sem Claude Code — provedores#Harness]]).

| Ferramenta | O que faz | Toca em |
|---|---|---|
| `search_notes`, `list_folder` | acha notas e devolve títulos | API do `ichiro` |
| `read_note` | devolve o texto de uma nota ou skill | API do `ichiro` |
| `create_note`, `edit_note` | grava nota, regra ou skill; a edição manda só o trecho velho → novo (é assim que a IA monta o workspace) | API do `ichiro` |
| `delete_note` | apaga uma nota pelo id | API do `ichiro` |
| scripts do `.workspace/` | o que a pessoa ou a IA escreveu | [[Sandbox]] ([[Workspace no app#Scripts]]) |

- As ferramentas só alcançam as notas da pasta do workspace da conversa: o chat de um assunto não lê nem muda as notas de outro.
- O serviço chega às notas pela API do `ichiro` ([[API de notas]]), pela [[Rede de containers|rede interna do compose]], e não direto no banco: o `ichiro` continua dono da tabela, e as regras de pasta e validação valem para a IA também.
- Mudança feita pela IA passa a ser [[Edição por âncora|proposta por âncora]] quando ela existir; antes disso, grava direto.

## O que o app faz do que o Claude Code faz

| No Claude Code hoje | No chat |
|---|---|
| perguntar com o vault de contexto | ✅ ferramentas de nota |
| escrever e corrigir notas, ensinar conceito, achar lacuna | ✅ skills em texto + `create_note`, `edit_note` |
| regras de resposta e de página | ✅ notas no `.workspace/`, no `system` |
| subagente | depois: um segundo laço com pacote próprio (o SDK tem) |
| desenho draw.io, script | depois: [[Sandbox]] |
| hooks | v3 ([[Workspace no app#Liberação em fases]]) |
| git, terminal, código do repo | ❌ o servidor não alcança o PC |

O que mexe no repo continua no Claude Code. A ponte entre os dois é o [[MCP — a IA como cliente do daemon|MCP]]: o Claude Code no PC lê e edita as mesmas notas do servidor.

## Em aberto

- Como a resposta chega aos pedaços ao cliente ([[Server-sent events|SSE]] ou [[WebSocket]]).
- Sem login (M2), qualquer um que alcance o servidor gasta a chave: o chat não vai para a AWS antes do login.
