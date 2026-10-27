---
tags: [noteproject, ia, editor]
---
# Blocos padronizados

As regras de página do workspace já pedem formatos fixos: passos numerados, a tabela Entra | Ferramenta | Sai, "Quem é quem" para símbolos, a lista `## Dúvidas`. Hoje isso é texto de prompt que a IA lê e tenta seguir.

Com blocos padronizados, a IA **preenche um molde** e o [[O daemon notesd|daemon]] transforma o molde em Markdown. O formato fica garantido por código, não por pedido.

## Os moldes

| Bloco | Campos | Vira |
|---|---|---|
| `passos` | lista de passos curtos | `> [!passos]` + lista numerada |
| `caminho` | entra, ferramenta, sai | tabela de uma linha Entra / Ferramenta / Sai |
| `quem-e-quem` | símbolo, o que é, tamanho, de onde vem | lista, um bullet por símbolo |
| `bullets` | itens | lista |
| `comparacao` | colunas, linhas | tabela |
| `exemplo` | enunciado, conta, resultado | `> [!exemplo]` |
| `nota` | texto de até 2 linhas | `> [!note]` |
| `figura` | tipo + receita | ver [[Figuras geradas]] |

## Exemplo

A IA devolve:

```json
{"bloco": "passos", "itens": ["Escreva p(λ) = det(λI − A)", "Troque λ por A", "Resultado: p(A) = 0"]}
```

O [[O daemon notesd|daemon]] escreve:

```
> [!passos]
> 1. Escreva p(λ) = det(λI − A)
> 2. Troque λ por A
> 3. Resultado: p(A) = 0
```

## Por que

- **Formato garantido**: o [[O daemon notesd|daemon]] valida o JSON com Pydantic, como já faz nas rotas, e recusa bloco fora do molde. É o "regra vira lint" do workspace um passo antes: a regra vira schema.
- **Menos tokens**: o prompt não explica estilo, só lista os moldes. A saída é só conteúdo.
- **Continua Markdown**: são callouts do Obsidian. A nota abre no Obsidian e exporta sem o app.
- **Funciona sem IA**: `/` no editor abre um menu (estilo Notion) que insere o molde vazio.

No editor, cada tipo de callout ganha [[CodeMirror|decoração]] própria (cor, ícone), do mesmo jeito que `decorations/headings.ts`.
