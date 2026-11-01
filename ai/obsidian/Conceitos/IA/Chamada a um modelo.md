---
tags: [noteproject, conceito, ia]
---
# Chamada a um modelo

Um modelo de linguagem roda na máquina do provedor (Anthropic, OpenAI) ou num programa local (Ollama). Um programa que quer usar o modelo precisa mandar a pergunta e receber a resposta de alguma forma.

- A forma é uma request HTTP comum: `POST` com corpo JSON para a API do provedor, com a chave da conta num cabeçalho. A resposta é outro JSON.
- **O modelo não guarda nada entre chamadas.** Ele não lembra da pergunta anterior nem sabe que arquivos, notas ou programas existem.
- Por isso cada chamada leva tudo o que o modelo precisa saber, e o pacote é montado de novo a cada vez por quem chama.

## O pacote

Na Messages API da Anthropic, o corpo tem três partes além do nome do modelo:

| Parte | O que é | Muda entre chamadas? |
|---|---|---|
| `system` | instruções fixas: regras, papel, índice do que existe | quase nunca |
| `tools` | ferramentas que o modelo pode pedir: nome, descrição, parâmetros (JSON Schema) | quase nunca |
| `messages` | a conversa até agora, alternando `user` e `assistant` | cresce a cada volta |

```json
{
  "model": "claude-...",
  "system": "Responda curto. Skills: resumir-aula (resume uma aula)...",
  "tools": [{"name": "read_note", "description": "lê uma nota pelo id",
             "input_schema": {"type": "object",
                              "properties": {"id": {"type": "integer"}}}}],
  "messages": [{"role": "user", "content": "como o Caddy faz o TLS?"}]
}
```

- Uma conversa longa é a mesma lista `messages` reenviada com as mensagens novas no fim.
- Reenviar tudo custa tokens de novo a cada chamada; o [[Cache de prompt]] barateia o começo repetido.
- Há um limite de tamanho do pacote, a **janela de contexto**: o que não cabe precisa ficar de fora ou ser resumido.

## Como o modelo sabe o que existe

O modelo só conhece o que está escrito no pacote. Para ele "saber" de uma nota, skill ou ferramenta, alguém precisa ter posto no pacote:

| O quê | Como entra no pacote |
|---|---|
| ferramenta | em `tools`, com nome, descrição e parâmetros |
| regra | inteira no `system` |
| skill, agente | um índice no `system`: nome + uma linha de descrição; o corpo vem só se o modelo pedir |
| documento, nota | não vem listado (seria grande demais); o modelo pede por uma ferramenta de busca e recebe os títulos |

- A descrição é o que faz o modelo escolher: uma skill com descrição vaga não é usada.
- Pedir algo que não está no pacote é o [[Laço de ferramentas]].

> [!example] No NoteProject
> O chat monta o `system` com as regras do `.workspace/` e acha as notas por ferramenta ([[Chat com o workspace]]).

Doc: [Anthropic — Messages API](https://docs.anthropic.com/en/api/messages).
