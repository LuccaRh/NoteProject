---
tags: [noteproject, conceito, ia]
---
# Laço de ferramentas

Numa [[Chamada a um modelo|chamada a um modelo]], o modelo só sabe o que veio no pacote. Para responder sobre uma nota que não veio, ele precisa de um jeito de pedir mais, e alguém precisa entregar.

- O modelo não acessa nada fora dele: não abre arquivo, não lê banco, não chama a rede.
- Ele só **responde** dizendo "quero a ferramenta X com estes parâmetros". Quem executa é o programa que fez a chamada.
- O programa executa e faz **uma nova chamada** com tudo de antes mais o resultado. Isso se repete até o modelo responder só com texto.

## Uma volta

A resposta que pede ferramenta é JSON com campos fixos, então o programa não interpreta texto livre:

```json
{"stop_reason": "tool_use",
 "content": [{"type": "tool_use", "id": "tu_1",
              "name": "read_note", "input": {"id": 42}}]}
```

1. `stop_reason == "tool_use"` → o modelo quer uma ferramenta.
2. O programa procura `name` num dicionário `{"read_note": read_note, ...}` e chama a função com `input`.
3. A próxima chamada leva o pacote anterior + duas mensagens no fim:

```json
{"role": "assistant", "content": [{"type": "tool_use", "id": "tu_1", "...": "..."}]},
{"role": "user", "content": [{"type": "tool_result", "tool_use_id": "tu_1",
                              "content": "<texto da nota 42>"}]}
```

- O `id` liga o resultado ao pedido, porque o modelo pode pedir várias ferramentas de uma vez.
- A chamada nunca vem do provedor para o programa: o programa sempre chama, o provedor sempre responde. O programa pode estar numa rede que o provedor não alcança.

## O que pesa

- **O pacote cresce a cada volta**: uma pergunta que lê 5 notas faz 6 chamadas, e a última leva as 5 notas. Cada volta paga de novo pelo que já foi; o [[Cache de prompt]] barateia a parte repetida.
- **Limite de voltas**: o programa para depois de N voltas, para um modelo que fica pedindo ferramenta não rodar para sempre.
- **Quem decide o que o modelo alcança é o programa**: uma ferramenta que não está em `tools` não existe para o modelo.

## Harness

O programa em volta do laço se chama *harness*: monta o pacote, executa as ferramentas e repete. O mesmo modelo responde melhor ou pior conforme o harness:

| Peça do harness | O que muda |
|---|---|
| prompt de sistema | instruções ajustadas de como trabalhar (ler antes de editar, conferir) |
| desenho das ferramentas | editar um trecho exato com erro claro se não achar; ler com número de linha |
| conversa longa | resumir o começo quando o pacote enche; abrir subagentes com pacote próprio |
| erros | devolver a mensagem de erro ao modelo para ele tentar de novo |

- O Claude Code é um harness: um programa no PC, cliente da API da Anthropic. `Read`, `Edit` e `Bash` são ferramentas que ele executa na máquina; o modelo só escolhe qual pedir.
- O Claude Agent SDK é o mesmo harness em forma de biblioteca, com ferramentas próprias no lugar das de disco. *(Doc conferida em 2026-10-31: [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview).)*
- Um servidor [[MCP]] é outro jeito de dar ferramentas a um harness: as funções ficam num programa à parte, e qualquer cliente MCP as usa.

> [!example] No NoteProject
> O serviço de IA roda o laço no servidor, com ferramentas que leem e editam notas ([[Chat com o workspace]]).

Doc: [Anthropic — tool use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use).
