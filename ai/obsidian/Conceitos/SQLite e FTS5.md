---
tags: [noteproject, conceito, dados]
---
# SQLite e FTS5

Um app que guarda notas no dispositivo precisa achá-las por palavra. Arquivos soltos guardam, mas não dão transação, índice nem busca.

- **SQLite**: banco SQL inteiro num arquivo só, sem servidor; o programa abre o arquivo por uma biblioteca.
- **FTS5**: extensão do SQLite para busca full-text. Monta um índice invertido: palavra → linhas onde ela aparece.

## Texto dentro do banco

- Blob pequeno (abaixo de ~100 KB) lê mais rápido de dentro do SQLite que de arquivo solto ([sqlite.org](https://www.sqlite.org/intern-v-extern-blob.html)); uma nota tem dezenas de KB.
- Ganha transação (salva tudo ou nada), índice e busca.

## Como o índice acompanha a tabela

- Modo *external content*: o índice não copia o texto, aponta para o `rowid` da tabela.
- Nesse modo, quem mantém o índice são três gatilhos (insert, delete, update). Sem eles, o índice começa vazio e não segue as mudanças.
- `tokenize="unicode61 remove_diacritics 2"`: "funcao" acha "função".
- Na consulta, `MATCH` tem sintaxe própria (`-`, `*`, aspas): texto digitado vai entre aspas para não virar operador.

> [!example] No NoteProject
> No app desktop, as notas ficam num SQLite com FTS5, aberto só pelo [[O daemon notesd|notesd]].

Doc: [FTS5](https://www.sqlite.org/fts5.html).
