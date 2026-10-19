---
tags: [noteproject, editor]
---
# Marcador no texto, conteúdo fora

O editor relê o Markdown para decidir o que pintar (headings, listas). Figura, desenho à mão ou o estado de uma dúvida não precisam estar no texto para aparecer na tela, e só pesariam nessa leitura.

A regra: **no texto fica um marcador curto; o conteúdo pesado mora em outra estrutura** (uma tabela do banco, um arquivo). Na tela, uma [[CodeMirror e decorações|decoração]] troca o marcador pela coisa.

| Coisa | No texto | Fora do texto |
|---|---|---|
| figura | `![[fig-3f2a.svg]]` | receita e arquivo gerado ([[Figuras geradas]]) |
| dúvida | `> [!duvida\|d7] ...` | trecho selecionado e estado ([[Marcar dúvida]]) |
| desenho à mão (ink) | marcador do bloco | traços em `ink_blocks` ⏳ |

- Nenhuma dessas peças deixa a digitação mais lenta.
- O arquivo continua Markdown: aberto fora do app, o marcador aparece como texto ou link.
