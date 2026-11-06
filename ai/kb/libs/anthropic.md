---
pacote: anthropic
versao: 2.3.0
fonte: apps/lonzo/.venv/lib/python3.14/site-packages/anthropic/
areas: [ia]
---
# anthropic — cliente da Messages API (lonzo)

Card destilado do código instalado (fonte acima, linhas citadas). Versão mudou → `ai/np lint`
avisa; reconfira as linhas antes de confiar no card. Escolhida em 2026-11-01 no lugar do
`claude-agent-sdk` 0.2.176 (traz o Claude Code CLI 2.1.316 como binário de 328 MB em
`claude_agent_sdk/_bundled/claude`; um subprocesso por pergunta).

## Cliente (`_client.py`)
- `AsyncAnthropic(api_key=None, ...)` (607). Sem argumento, lê `ANTHROPIC_API_KEY` (107).
- Sem key, **constrói sem erro** e só falha na request, com `TypeError` "Could not resolve
  authentication method" (conferido rodando). Por isso o `get_client` do lonzo checa o env antes.

## Stream (`resources/messages/messages.py`, `lib/streaming/_messages.py`)
- `client.messages.stream(model=, max_tokens=, messages=, system=, tools=, ...)` (2660) devolve
  um gerenciador: `async with ... as stream`.
- `stream.text_stream` (216): só os pedaços de texto, `AsyncIterator[str]`.
- `async for event in stream` (238): todos os eventos (`text`, `content_block_*`, `message_stop`...).
- `await stream.get_final_message()` (261): a mensagem inteira no fim; `.stop_reason`, `.usage`.
- `stop_reason` (`types/stop_reason.py`): `end_turn`, `max_tokens`, `stop_sequence`, `tool_use`,
  `pause_turn`, `refusal`, `model_context_window_exceeded`.
- `usage.input_tokens`, `usage.output_tokens` (`types/usage.py:25,28`).

## Saída estruturada (`resources/messages/messages.py`), para a #73
- `await client.messages.parse(model=, max_tokens=, messages=, system=, output_format=<classe
  Pydantic>, ...)` (2785): a lib converte a classe em JSON schema, manda em `output_config`
  (`format: {type: "json_schema", schema}`, `types/json_output_format_param.py`) e valida a volta.
- `message.parsed_output` (`types/parsed_message.py:78`): a instância da classe, ou `None` sem
  bloco de texto válido. Conferido com o Haiku 5.5 em 2026-11-02 (rota `/chat/workspaces`).
- HTTP por baixo: `httpx2` (`_base_client.py:40`), não `httpx` (card `httpx2`).

## Modelos (`types/model.py`)
- `claude-haiku-5-5` (8): o do lonzo no dev, `max_tokens` 512.

## Erros (`_exceptions.py`)
- `APIError` (35, com `.message`) ← `APIStatusError` (71: 4xx/5xx), `APIConnectionError` (95);
  `AuthenticationError` (139) é um `APIStatusError` (key errada).

## Ferramentas, para a #77
- Bloco `tool_use`: `id`, `name`, `input: Dict[str, object]` (`types/tool_use_block.py:16`).
- Resposta: bloco `tool_result` com `tool_use_id`, conteúdo e `is_error: bool`
  (`types/tool_result_block_param.py:36`).
- Laço pronto (beta): `client.beta.messages.tool_runner(...)` (`resources/beta/messages/messages.py:1436`),
  com cada ferramenta como função decorada por `@beta_tool` (`lib/tools/_beta_functions.py:354`).
- Com `stream=True`, cada item do runner é um stream de um turno, e `async for event in stream` traz
  `text` (`.text`, `lib/streaming/_beta_types.py:20`), `content_block_start` e `content_block_stop`
  (`.content_block`; 96 e 116). Bloco `tool_use`: no start `input` é `{}`; no stop vem inteiro
  (conferido com o Haiku 5.5 em 2026-11-05).
- A ferramenta roda depois do fim do stream do turno: `generate_tool_call_response`
  (`lib/tools/_beta_runner.py:1311`), salvo com `run_tools_eagerly` (1552), que o lonzo não liga.

## Cache de prompt (tool_runner)

- `tool_runner` aceita `cache_control` no topo (`resources/beta/messages/messages.py:1443`): marca o último bloco a cada volta.
- `system` pode ser lista de `BetaTextBlockParam` com `cache_control` em um bloco (`:1459`).
- Lido do cache: `usage.cache_read_input_tokens` (`types/beta/beta_usage.py:21`); não entra em `input_tokens`.
- `await runner.generate_tool_call_response()` guarda o resultado e o laço segue com ele (`lib/tools/_beta_runner.py:776`, `:1288`).

## Chave por pedido e modelos (`_client.py`, `resources/models.py`, `types/model_info.py`)
- `client.with_options(api_key=...)` = `copy` (896): cópia do client que usa as mesmas conexões
  (`http_client = http_client or self._client`, 942).
- `client.models.list()` (`models.py:245`): `async for` pagina sozinho. Chave recusada levanta
  `AuthenticationError` (`_exceptions.py:139`).
- `ModelInfo`: `id` (13), `display_name` (35), `max_tokens: Optional[int]` (60).
