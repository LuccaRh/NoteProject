---
tags: [noteproject, conceito, editor]
---
# Markdown

Texto formatado costuma depender do programa que o abre: um `.docx` sem o Word vira bytes ilegíveis. Markdown resolve isso escrevendo a formatação com caracteres comuns, que se leem mesmo sem programa nenhum.

- **Markdown**: um combinado de como escrever texto puro: `#` no começo da linha é título, `**x**` é negrito, `- ` é item de lista. *(geral)*
- **Arquivo `.md`**: um arquivo de texto com esse nome no fim. O conteúdo é o mesmo texto que estaria numa coluna do banco ou na memória do editor; não há conversão entre "texto" e "md".

| Etapa | O que acontece | Muda o texto? |
|---|---|---|
| guardar | o texto vai inteiro para um arquivo ou para uma coluna `TEXT` | não |
| editar | o editor mostra o texto e pinta por cima: o título fica grande, o `#` continua lá ([[CodeMirror e decorações]]) | não |
| render | uma lib lê o texto e gera HTML (`<h1>`, `<strong>`), como no modo leitura do Obsidian | gera outra coisa; o original fica igual |

- Por ser texto puro, a mesma nota abre em qualquer editor, entra no git linha a linha e é buscada por palavra no banco.
- Existem variações do combinado: CommonMark (a base), GFM (do GitHub, com tabela e caixa de seleção) e extras do Obsidian (`[[link]]`, callouts `> [!info]`). *(geral)*

## Extensão × formato

Todo arquivo é uma sequência de bytes. O que separa foto, programa e texto é **como os bytes estão organizados** (o formato), não o nome.

| | O que é | Quem usa |
|---|---|---|
| **assinatura** (*magic number*) | bytes fixos no começo: `‰PNG`, `%PDF`, `.ELF` | quem lê o conteúdo: `file`, o visualizador, o Linux ao executar |
| **extensão** (`.md`, `.png`) | parte do nome, uma etiqueta; não muda os bytes | quem escolhe sem abrir: o desktop (`*.md` → `text/markdown` → Obsidian) e programas como o Obsidian, que só lista `.md` |

- Texto puro **não tem assinatura**: `.txt` e `.md` têm bytes iguais, e o `file` diz só "UTF-8 text". Só o nome diz que o texto segue o combinado do Markdown.
- A assinatura é um chute: um `.txt` que começa com `%PDF` aparece no `file` como PDF.
- O desktop escolhe o programa em dois passos. Primeiro do nome para o tipo: `/usr/share/mime/globs2` liga `*.md` a `text/markdown`. Depois do tipo para o programa: `xdg-mime query default text/markdown` responde `obsidian.desktop`.
- Para [[Executar um arquivo no Linux|executar um arquivo]], o Linux não usa a extensão: ele exige o formato ELF (ou um script com `#!`) e a permissão `x`.

> [!example] No NoteProject
> A nota fica como texto na coluna `body` da [[API de notas]] e o editor só a decora ([[Front — editor e UI]]).

Doc: [CommonMark](https://commonmark.org/help/).
