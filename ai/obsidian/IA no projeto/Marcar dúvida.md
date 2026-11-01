---
tags: [noteproject, ia, editor]
---
# Marcar dúvida

> [!info] Depois, sem data
> Saiu da fila em 2026-10-31: o [[Chat com o workspace|chat]] cobre a pergunta sobre um trecho ([[Ordem de implementação]]).

Hoje, para marcar uma dúvida no Obsidian, você digita `> [!duvida] ...` à mão. Depois vai ao terminal e roda `/duvida`.

A ideia é marcar com um atalho, sem sair da leitura, e deixar a resposta para depois.

## O gesto

1. Selecione o trecho que não entendeu.
2. Aperte `Ctrl+D`: abre uma caixinha embaixo do trecho.
3. Escreva a pergunta e dê `Enter`.

Caixa vazia + `Enter` = "não entendi este trecho"; a seleção vira a pergunta.

| Atalho | Marca | Quer dizer |
|---|---|---|
| `Ctrl+D` | dúvida | não entendi |
| `Ctrl+Shift+D` | fix | está errado / tira isto |

## O que fica no Markdown

O mesmo callout que o workspace já usa, mais um id curto depois do `|`:

```
> [!duvida|d7] por que pode usar Cayley-Hamilton se A não é diagonalizável?
```

- O Obsidian aceita texto depois do `|` num callout. A página continua abrindo lá, e a `/duvida` de hoje continua funcionando.
- No editor, o callout vira um **chip** com o estado (pendente, na fila, respondida). É uma [[CodeMirror|decoração do CodeMirror]], como `decorations/headings.ts`.
- O trecho selecionado e o estado ficam no banco (tabela `pedidos`), não no texto: no [[Postgres]] do servidor no [[Navegador|navegador]], no [[O daemon notesd|daemon]] no app desktop. No texto fica só o [[Marcador no texto, conteúdo fora|marcador curto]].

## Custo

Marcar não chama a IA, então não gasta nada. Pedir a resposta é a [[Fila de pedidos]].
