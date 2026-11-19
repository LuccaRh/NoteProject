---
tags: [noteproject, ia, servidor]
---
# Chat com IA

O `lonzo` responde perguntas sobre as notas usando um modelo Claude que chama ferramentas (buscar, ler, criar, editar notas). Ficou no servidor para a mesma pergunta ter o mesmo contexto de qualquer aparelho ([[Chat com o workspace]]). Passo a passo com desenhos em [[Caminho de uma pergunta]].

![[pergunta-com-streams.drawio.svg]]
*Uma pergunta: o runner do SDK abre um stream por turno do modelo; o `lonzo` traduz cada evento em SSE para o navegador.*

## O laço

O [[Laço de ferramentas|laço de ferramentas]]: o modelo responde com texto ou com um pedido de ferramenta; o app roda a ferramenta, devolve o resultado e chama de novo, até o modelo parar.

- Feito pelo `tool_runner(stream=True)` do SDK `anthropic` (beta): um stream por turno, `max_iterations` = limite de turnos do usuário (`tools_max_turns`).
- Ferramentas declaradas com `@beta_async_tool(strict=True)`: o schema JSON sai da assinatura e da docstring, e `strict` obriga o modelo a mandar exatamente aquele formato ([[Saída estruturada]]).
- Erro numa ferramenta (`ValueError("old_text is not in ...")`) volta ao modelo como resultado de erro, e ele tenta de novo.
- Modelo, `max_tokens` e thinking são do usuário ([[Chave da API por usuário]]).

## Streaming para o navegador

`POST /api/chat` devolve `StreamingResponse` com `text/event-stream` ([[Server-sent events]]), alimentado por um [[Gerador|gerador]] async:

| Evento | Quando |
|---|---|
| `message_start` | primeiro, com o `conversation_id` |
| `text_delta` | cada pedaço de texto do modelo |
| `tool_use` | quando uma ferramenta começa, com nome e alvo (`Reading Roadmap`), para a linha de status |
| `message_end` | fim: uso de tokens (entrada, saída, cache), modelo, `stop_reason` |
| `error` | `APIError` no meio da resposta |

- Chave, conversa e regras são conferidas **antes** do primeiro evento (`answer` é aguardado antes do `StreamingResponse`): esses erros ainda viram status HTTP (422 sem chave, 404 conversa ou pasta inexistente, 502 com o `ichiro` fora). Depois que o 200 saiu, erro só pode ser evento.
- Cancelar no front fecha a conexão; o gerador para.

## Histórico

- Banco `lonzo`: `conversations` (dono, pasta, título) e `messages` (`role`, `content JSONB`).
- `content` guarda os blocos no formato que a API aceita de volta, incluindo `tool_use` e `tool_result`: a próxima pergunta reenvia a conversa inteira com as ferramentas, e o modelo sabe o que já leu.
- A conversa nova é criada antes do stream (o id vai no `message_start`); pergunta e turnos só são salvos no fim, numa transação: erro no meio não deixa troca pela metade.
- Turno vazio não é salvo (a API recusaria em toda pergunta seguinte).
- SQLAlchemy async + psycopg 3; `create_async_engine` global, fechado no `lifespan`.

## Se perguntarem

- **"Por que SSE e não WebSocket?"** O fluxo é de mão única (servidor → navegador) e por pedido; SSE é HTTP comum, passa pelo Caddy sem config, e o cancelamento é fechar a conexão. [[WebSocket]] fica para a edição ao vivo.
- **"Por que não o Claude Agent SDK?"** Ele roda o Claude Code (CLI, sistema de arquivos) por baixo; aqui as "ferramentas" são chamadas HTTP ao `ichiro` com o usuário do pedido, e a API direta dá controle de cache, histórico e custo.
- **"Como controla custo?"** Limite de turnos, `max_tokens`, [[Cache de prompt|cache]] do system e do histórico, chave do próprio usuário ([[Gastar poucos tokens]]).
- **"E se o modelo apagar uma nota errada?"** Hoje não há trava nem desfazer: limitação conhecida. O plano é [[Edição por âncora|edição por âncora]] com revisão.
