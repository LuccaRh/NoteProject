---
tags: [noteproject, conceito, ia]
---
# MCP

Um programa de IA sabe conversar, mas não sabe o que existe fora dele: um banco, uma API. Cada integração feita à mão seria diferente.

- **MCP** (*Model Context Protocol*): padrão aberto para ligar um programa de IA a ferramentas de fora.
- **Servidor MCP**: programa pequeno que diz "tenho estas funções, com estes parâmetros" e as executa quando a IA chama.
- **Cliente MCP**: o programa de IA; inicia o servidor e mostra as funções ao modelo.

- Nome, descrição e parâmetros de cada função entram no contexto do modelo: quanto menos e mais curtas, menos tokens.
- Qualquer cliente MCP usa o mesmo servidor.

> [!example] No NoteProject
> Proposta: a IA chega às notas por funções do daemon em vez de abrir arquivos ([[MCP — a IA como cliente do daemon]]).

Doc: [modelcontextprotocol.io](https://modelcontextprotocol.io/).
