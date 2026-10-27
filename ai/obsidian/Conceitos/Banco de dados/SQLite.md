---
tags: [noteproject, conceito, dados]
---
# SQLite

Um app que guarda notas no dispositivo precisa de mais que arquivos soltos: arquivos guardam, mas não dão [[Transação|transação]], índice nem busca.

- **SQLite**: banco SQL inteiro num arquivo só, sem servidor; o programa abre o arquivo por uma biblioteca.
- Só um programa escreve por vez; com muitos clientes escrevendo ao mesmo tempo, entra um banco servidor como o [[Postgres]].
- Busca por palavra vem da extensão [[FTS5]].

## Texto dentro do banco

- Blob pequeno (abaixo de ~100 KB) lê mais rápido de dentro do SQLite que de arquivo solto ([sqlite.org](https://www.sqlite.org/intern-v-extern-blob.html)); uma nota tem dezenas de KB.
- Ganha transação (salva tudo ou nada), índice e busca.

> [!example] No NoteProject
> No app desktop, as notas ficam num SQLite, aberto só pelo [[O daemon notesd|notesd]].

Doc: [SQLite](https://www.sqlite.org/about.html).
