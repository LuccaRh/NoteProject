---
tags: [noteproject, conceito, dados]
---
# Árvore no banco

Pastas dentro de pastas formam uma árvore, e uma tabela de banco é uma lista plana de linhas. Para guardar a árvore, cada linha precisa dizer onde está.

- **Lista de adjacência**: cada linha guarda o `id` de quem a contém (`parent_id`); a raiz tem `parent_id` vazio (`NULL`). A árvore inteira sai dessa coluna. *(geral)*

```
id  title     is_folder  parent_id
1   2S2026    true       NULL      ← raiz
2   ES728     true       1         ← dentro de 2S2026
3   Aula 3    false      2         ← dentro de ES728
```

| Operação | Como |
|---|---|
| abrir uma pasta | `SELECT ... WHERE parent_id = 2` |
| mover | trocar o `parent_id` de uma linha |
| apagar a pasta e o que tem dentro | chave estrangeira com `ON DELETE CASCADE`: o banco apaga os filhos, e os filhos deles |
| caminho até a raiz | subir de pai em pai (no Postgres, uma consulta recursiva, `WITH RECURSIVE`) |

## Pasta como item da mesma tabela

Pasta e item têm quase os mesmos dados: id, nome, pai, datas. Com uma tabela só e uma marca (`is_folder`), listar uma pasta é uma consulta só, com subpastas e itens juntos; a pasta só deixa o conteúdo vazio.

| Desenho | Quando serve |
|---|---|
| uma tabela, `parent_id` + `is_folder` | cada item numa pasta só; pasta dentro de pasta |
| tabela `folders` à parte, item com `folder_id` | pastas com dados muito diferentes dos itens; pasta dentro de pasta ainda pede `folders.parent_id`, e listar vira consulta em duas tabelas |
| tabela de relação (`item_id`, `pasta_id`) | o mesmo item em várias pastas ao mesmo tempo, como uma tag (muitos-para-muitos) |

## Em outros programas

| Programa | Pasta é | Quem guarda a relação |
|---|---|---|
| Google Drive | um arquivo do tipo pasta | o filho aponta para o pai, como aqui |
| Notion | uma página que contém páginas | idem: tudo é página com um pai |
| Obsidian | uma pasta de verdade no disco, sem banco | o sistema de arquivos; o caminho é a identidade da nota |
| Linux (sistema de arquivos) | um diretório | o pai: cada diretório guarda a lista "nome → arquivo"; o mesmo arquivo pode ter dois nomes (hard link) |

Tudo *(geral)*, de memória. O jeito do Linux só compensa quando o mesmo item precisa aparecer em dois lugares; sem isso, é uma tabela a mais sem uso.

> [!example] No NoteProject
> Pasta é uma nota com `is_folder` e a árvore vem de `parent_id` ([[Pastas, campos e views]]).

Doc: [PostgreSQL — WITH RECURSIVE](https://www.postgresql.org/docs/current/queries-with.html#QUERIES-WITH-RECURSIVE).
