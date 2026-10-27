---
tags: [noteproject, dados]
---
# Pastas, campos e views

Organizar nota costuma custar na hora de anotar: escolher tag, preencher propriedade. Quem quer só anotar rápido pula essa etapa, e a nota se perde.

No NoteProject, **organizar é escolher onde criar a nota**. A pasta preenche campos sozinha, e as views mostram a mesma nota de vários jeitos.

## As três peças

| Peça | O que é | No schema |
|---|---|---|
| pasta | uma nota com `is_folder = 1`; a árvore vem de `parent_id` ([[Árvore no banco\|lista de adjacência]]) | `parent_id`, `is_folder` ⏳ (#6, #12) |
| campos | parâmetros da nota em JSON: `aula`, `conteudo[]`, `tipo` | `fields` JSONB ⏳ (#7, #12) |
| view | lista de notas filtrada por campo ("todas de estabilidade") | ⏳ |

## Como uma nota ganha campos

1. A nota é criada em `2S2026/ES728/`.
2. A pasta injeta `semestre` e `materia`: nenhuma decisão na hora de anotar.
3. `conteudo` vem depois, por regra, por modelo pequeno ou à mão ([[Classificar a nota pelo tema]]).

- A mesma nota aparece em várias views sem ser copiada: a view é uma consulta, não uma pasta.
- As colunas entram no [[Postgres]] do servidor (#12); pastas, campos, views e a sidebar são as issues #6–#9 do [[Roadmap]].
