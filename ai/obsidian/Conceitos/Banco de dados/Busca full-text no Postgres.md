---
tags: [noteproject, conceito, dados]
---
# Busca full-text no Postgres

Achar notas por palavra com `ILIKE '%caddy%'` lê o texto de todas as linhas a cada busca, e acha "caddy" até dentro de outra palavra. A busca full-text quebra o texto em palavras e guarda um [[Índice|índice invertido]] delas, para a busca ir direto às linhas que têm a palavra.

## As peças

| Peça | O que faz | Exemplo |
|---|---|---|
| `to_tsvector` | texto → lista das palavras, cada uma uma vez, com as posições | `'O Caddy usa o Caddy'` → `'caddy':2,5 'o':1,4 'usa':3` |
| `websearch_to_tsquery` | o texto digitado → a busca que o índice entende | `caddy tls` → `'caddy' & 'tls'` |
| `@@` | a lista casa com a busca? | `to_tsvector(...) @@ websearch_to_tsquery(...)` |
| índice GIN | palavra → linhas, para o `@@` não ler a tabela | `CREATE INDEX ... USING GIN (...)` |

- O primeiro argumento das duas funções é o **dicionário** (`'simple'`, `'portuguese'`, `'english'`), que diz como o texto vira palavra.
- `'simple'` só passa para minúsculas e separa pela pontuação; não descarta palavra nenhuma ("o", "ao" ficam) nem corta sufixo. Serve para texto que mistura línguas.
- Um dicionário de língua (`'portuguese'`) tira as palavras vazias e reduz cada uma à raiz: "notas" acha "nota". Em texto de outra língua, corta errado.
- O `websearch_to_tsquery` aceita o jeito de um buscador: `"frase exata"`, `-palavra`, `or`.

## O que casa

Com `'simple'`:

| Busca | Acha | Não acha |
|---|---|---|
| `caddy` | "Caddy", "caddy,", "(caddy)" | "cadd", "caddyfile" |
| `caddy tls` | linha com as duas palavras, em qualquer ordem e distância | linha só com uma |

## Índice sobre a expressão

A lista de palavras pode morar só dentro do índice, sem coluna nova na tabela ([[Índice#Índice sobre uma expressão|índice sobre uma expressão]]):

```sql
CREATE INDEX notes_search_idx ON notes
USING GIN (to_tsvector('simple', title || ' ' || body));

SELECT id, title FROM notes
WHERE to_tsvector('simple', title || ' ' || body)
      @@ websearch_to_tsquery('simple', 'caddy');
```

1. Ao salvar uma linha, o Postgres roda o `to_tsvector` nela e põe a linha nas listas das palavras dela, dentro do índice.
2. Na busca, o `WHERE` repete a expressão do índice; o Postgres a reconhece, acha "caddy" no índice e lê da tabela só as linhas que ele aponta.
3. Uma expressão diferente (`body || title`, outro dicionário) não casa com o índice, e a busca volta a ler a tabela toda.

Guardar a lista numa coluna gerada e indexá-la dá a mesma velocidade, mas a coluna guarda as posições de cada palavra em cada linha: no teste abaixo, a tabela foi de 2,9 MB para 17 MB.

## Quanto custa e quanto ganha

Medido num Postgres 18, com 10 mil linhas falsas de ~3 KB cada (o mesmo texto repetido) e a palavra em 20 delas:

| Busca | Tempo |
|---|---|
| `ILIKE '%caddy%'`, sem índice | 212 ms |
| `to_tsvector(...) @@ ...`, sem índice | 3160 ms |
| `to_tsvector(...) @@ ...`, com o índice GIN | 0,05 ms |

- Sem índice, o full-text é o mais lento: monta a lista de palavras de cada linha a cada busca.
- Com o índice, a busca não depende do tamanho da tabela, só de quantas linhas têm a palavra.

Num vault real de 138 notas em [[Markdown]] (388 kB de texto, 4.989 palavras diferentes), o índice ocupou 416 kB, mais ou menos o tamanho do texto. Ele cresce mais devagar que as notas: as palavras novas rareiam, e o que cresce é a lista de linhas de cada palavra.

## O que fica de fora

O Postgres também ordena por relevância (`ts_rank`, com peso maior para o título) e devolve o trecho em volta da palavra (`ts_headline`). Uma busca que só lista as notas para alguém escolher não precisa dos dois: a ordem por título basta, e o trecho só aumenta a resposta.

> [!example] No NoteProject
> O `GET /notes/search` do `ichiro` usa o índice sobre a expressão ([[API de notas]]).

Doc: [Full Text Search](https://www.postgresql.org/docs/current/textsearch.html), [Indexes on Expressions](https://www.postgresql.org/docs/current/indexes-expressional.html).
