---
tags: [noteproject, ia]
---
# Ferramentas e contexto da IA

O modelo só sabe o que entra no pedido. Esta página junta o que o `lonzo` põe em volta dele: as ferramentas, as regras de cada pasta, as skills e o cache. Visão das peças em [[Harness do lonzo]].

## As ferramentas (`NoteTools`)

| Ferramenta | Faz |
|---|---|
| `search_notes`, `search_titles` | busca full-text e por título no `ichiro` ([[Serviço de notas]]) |
| `list_folder`, `read_note` | navega e lê |
| `create_note`, `create_folder` | recebem o **caminho inteiro** (`/Projetos/X/Resumo`): pastas que faltam são criadas |
| `edit_note(note_id, old_text, new_text)` | troca um trecho que aparece **uma vez** no corpo |
| `delete_note` | apaga nota ou pasta |
| `load_skill(name)` | carrega as instruções de uma skill pelo nome |

- `edit_note` por trecho: o modelo não reescreve a nota inteira (menos tokens, menos chance de estragar o resto). Trecho ausente ou repetido → erro que pede mais texto em volta. É a mesma ideia do `Edit` do Claude Code.
- Cada ferramenta é uma chamada HTTP ao `ichiro` com o usuário do pedido: o [[Row-Level Security|RLS]] vale para a IA também ([[Isolamento por usuário]]).
- Um dicionário dá o título de cada ferramenta para o status no front (`Reading Roadmap`).

## Workspace

Uma pasta com uma subpasta `.workspace/` vira um workspace ([[Workspace no app]]):

```
Projeto/
  .workspace/
    CLAUDE.md      regras desta pasta
    skills/        uma nota por skill
    kb/  scripts/  hooks/
```

- `POST /api/chat/workspaces {folder_id, description}`: o modelo cria o `.workspace/` a partir de uma descrição curta, guiado pelo `create_workspace.md`.
- As regras são de **todas** as pastas acima: o `ichiro` devolve o `.workspace/CLAUDE.md` de cada ancestral numa consulta só (`/notes/{id}/above`), da raiz para baixo; a mais perto vem por último e vence.
- `.workspace` fica escondida na árvore por padrão.

## Skills

- Skill = nota em `.workspace/skills/`, com cabeçalho `---` e `description` (o resumo que vai na lista). `create_note`/`edit_note` recusam skill sem `description`.
- No contexto vai só a lista (nome + resumo), da raiz até a pasta; o corpo entra quando o modelo chama `load_skill`. Mesmo esquema de "carregar sob demanda" das skills do Claude Code: a lista é barata, o texto só quando serve.
- Nome repetido em pastas diferentes: a mais perto vence.
- Inventário: publicar copia a skill para a tabela `skills` do banco `lonzo` (foto do momento); outros usuários leem e adicionam, o que sempre copia de novo.
- No chat, `/nome` põe o texto da skill na mensagem num bloco `<skill>` que a bolha esconde.

## Montagem do pedido

| Parte | Conteúdo | Cache |
|---|---|---|
| `system` | só o `base_rules.md` (fixo para todos) | marcado `cache_control` |
| 1ª mensagem `user` | bloco `<context>`: data, pasta atual, regras dos workspaces, lista de skills | refeito a cada pergunta, não salvo |
| histórico | as mensagens salvas, com ferramentas | cache automático do runner |
| pergunta | o texto | — |

- Prompts moram em `.md` lidos pelo código, nunca em string no Python (regra com lint).
- O `system` fixo e idêntico para todos maximiza o acerto do [[Cache de prompt|cache]]; o que muda por pergunta (data, pasta) foi tirado dele e posto no `<context>`, senão cada pergunta invalidaria o cache.

## Se perguntarem

- **"Por que não RAG com embeddings?"** As notas são de uma pessoa, a busca full-text do Postgres e a leitura por ferramenta resolvem; o modelo decide o que ler. Embeddings entram se a busca por palavra começar a falhar.
- **"Como evita prompt injection de uma nota?"** Não evita totalmente: o conteúdo lido entra como resultado de ferramenta. Limita o estrago: só as notas do próprio usuário, sem rede, sem execução de código.
