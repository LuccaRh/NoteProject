---
id: lonzo/stream-the-workspace-creation
nome: Criação de workspace com streaming (issue #229)
areas: [ia]
---
## Pedido (o que a branch entrega; cada item verificável)
1. `run_tools` (`clients/anthropic.py`) chama o `tool_runner` com `stream=True`: criar um
   workspace com `max_tokens` acima de ~21333 (padrão 64000) não dá mais 500
   ("Streaming is required for operations that may take longer than 10 minutes").
2. lonzo 0.21.0 (commit só da versão).

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- O limite próprio da criação (`TOOLS_MAX_TOKENS = 16000`) saiu no `ebb4fbf`; desde então o
  `run_tools` usa o `max_tokens` do usuário e o SDK recusa sem stream
  (`anthropic/_base_client.py:857-866`, anthropic 2.3.0).
- `until_done()` consome o runner com stream (`lib/tools/_beta_runner.py:1301`).

## Fora (vira outra branch)
- Teste que pegue a checagem do SDK (os testes usam um fake da Anthropic).
