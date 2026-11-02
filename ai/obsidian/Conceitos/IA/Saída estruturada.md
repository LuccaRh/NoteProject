---
tags: [noteproject, conceito, ia]
---
# Saída estruturada

Um modelo devolve texto. Quando quem chama é um programa, e não uma pessoa, o texto livre não serve: o programa precisa de campos que consiga ler com código (um título aqui, um corpo ali).

- Pedir "responda em JSON" no prompt costuma funcionar, mas não é garantido: pode vir uma frase antes, uma vírgula a mais, um campo com outro nome.
- A **saída estruturada** resolve isso na API: a [[Chamada a um modelo|chamada]] leva um **JSON Schema** (os campos e o tipo de cada um), e o provedor só deixa o modelo gerar texto que obedeça ao schema.
- A resposta continua sendo um bloco de texto, mas agora é um JSON válido com exatamente aqueles campos.

## Como se pede

| Jeito | O que vai na chamada | O que volta |
|---|---|---|
| texto livre | só o prompt | texto qualquer |
| prompt pedindo JSON | o prompt com o formato descrito | JSON, quase sempre |
| saída estruturada | `output_config.format = {type: "json_schema", schema}` | JSON que segue o schema |

- Na lib Python da Anthropic, `messages.parse(..., output_format=Classe)` aceita uma classe Pydantic: a lib gera o schema, manda, e devolve a instância já validada em `parsed_output`.
- É **uma chamada só**: o modelo não pede nada no meio, ao contrário do [[Laço de ferramentas|laço de ferramentas]], em que ele pede uma ferramenta e o programa chama de novo.
- O schema garante a forma, não o conteúdo: o modelo ainda pode inventar ou deixar um campo raso. O prompt continua dizendo o que vai em cada campo.

> [!example] No NoteProject
> O `lonzo` cria um workspace com uma chamada só: o modelo preenche as 5 partes do esqueleto, e cada campo vira uma nota ([[Workspace no app#Como nasce]]).
