---
tags: [noteproject, conceito, ia]
---
# Cache de prompt

Toda chamada a um modelo reenvia o contexto inteiro: instruções, documentos, pergunta. Cada token de entrada é pago de novo a cada chamada.

- **Cache de prompt**: o provedor guarda o começo de uma chamada; a próxima que começar igual lê esse pedaço do cache, mais barato e mais rápido.
- Só o prefixo conta: mudou um token, dali para a frente nada aproveita.
- O cache expira depois de alguns minutos sem uso.
- Por isso a chamada vai do mais fixo ao mais variável, e chamadas parecidas seguidas aproveitam o mesmo começo.

> [!example] No NoteProject
> Regras → card → pergunta, em lote ([[Gastar poucos tokens]], [[Fila de pedidos]]).

Doc: [Anthropic — prompt caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching).
