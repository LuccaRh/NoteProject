---
tags: [noteproject, conceito, dados]
---
# Índice

Sem ajuda, para achar uma linha o banco lê a tabela inteira, linha por linha, e testa cada uma. Com poucas linhas é rápido; com milhares, cada busca paga a tabela toda.

- **Índice**: estrutura à parte que o banco guarda ao lado da tabela, só para achar linhas sem ler todas. É o índice remissivo do fim de um livro: "Caddy → p. 12, 40", e vai direto às páginas.
- O índice não é a tabela: são dados extras no disco, que o banco atualiza sozinho a cada `INSERT`, `UPDATE` e `DELETE`.
- Na consulta, o banco decide sozinho se usa o índice; o SQL não muda.

## Índice comum: valor → linha

O tipo padrão (B-tree) guarda os valores de uma coluna em ordem, cada um apontando para a linha. Achar um valor é como achar uma palavra num dicionário: abre no meio e vai cortando, sem ler tudo.

- A chave primária e cada `UNIQUE` ganham um índice desses, criado pelo próprio [[Postgres]]: é com ele que o banco confere rápido se o valor já existe ([doc](https://www.postgresql.org/docs/current/indexes-unique.html)).
- Serve para `=`, `<`, `>` e ordem; não ajuda em `LIKE '%palavra%'`, porque a palavra pode estar no meio do texto, e o índice está em ordem pelo começo.

## Índice invertido: palavra → linhas

Para texto, o índice guarda cada palavra que aparece em qualquer linha, **uma vez só**, e ao lado dela a lista das linhas que a contêm:

```
caddy    → nota 3, nota 8
pedido   → nota 3
postgres → nota 5, nota 8, nota 12
tls      → nota 8
```

- O nome "invertido": a linha tem as palavras; o índice inverte e guarda, para cada palavra, as linhas.
- Uma palavra em 100 linhas aparece uma vez no índice, com as 100 ao lado. Linha editada: sai das palavras que perdeu, entra nas que ganhou.
- Duas palavras na busca: o banco cruza as duas listas e fica com as linhas que estão nas duas.
- No [[Postgres]], é o tipo **GIN** (*Generalized Inverted Index*); no [[SQLite]], o [[FTS5]].

## Índice sobre uma expressão

O índice pode ser montado sobre o resultado de uma conta, em vez de uma coluna (`lower(title)`, a lista de palavras do texto). O resultado fica só dentro do índice; a tabela não ganha coluna.

- O banco só usa esse índice quando o `WHERE` repete **a mesma expressão**, igual; outra expressão (outra ordem, outro argumento) volta a ler a tabela inteira.
- A alternativa é guardar a conta numa coluna gerada e indexar a coluna: a mesma velocidade, mas o resultado fica duas vezes no disco, na tabela e no índice.

## O custo

- **Disco**: o índice é uma cópia organizada do que ele indexa.
- **Escrita**: cada linha salva também atualiza os índices dela. A leitura fica rápida; a escrita, um pouco mais lenta.
- Por isso não se indexa tudo: só o que as consultas usam.

Doc: [Indexes](https://www.postgresql.org/docs/current/indexes.html), [GIN](https://www.postgresql.org/docs/current/gin.html).
