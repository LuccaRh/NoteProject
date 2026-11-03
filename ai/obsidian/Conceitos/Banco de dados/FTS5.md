---
tags: [noteproject, conceito, dados]
---
# FTS5

Achar notas por palavra com `LIKE '%palavra%'` lê todas as linhas, uma por uma. A busca full-text resolve isso com um índice próprio para texto.

- **FTS5**: extensão do [[SQLite]] para busca full-text. Monta um [[Índice|índice invertido]]: palavra → linhas onde ela aparece.

## Como o índice acompanha a tabela

- Modo *external content*: o índice não copia o texto, aponta para o `rowid` da tabela.
- Nesse modo, quem mantém o índice são três gatilhos (insert, delete, update). Sem eles, o índice começa vazio e não segue as mudanças.
- `tokenize="unicode61 remove_diacritics 2"`: "funcao" acha "função".
- Na consulta, `MATCH` tem sintaxe própria (`-`, `*`, aspas): texto digitado vai entre aspas para não virar operador.

> [!example] No NoteProject
> A busca do app desktop usa FTS5 no SQLite do [[O daemon notesd|notesd]].

Doc: [FTS5](https://www.sqlite.org/fts5.html).
