---
name: lacunas
description: Lista, numerados numa tabela, os conceitos e perguntas importantes da conversa que ainda não estão no Obsidian (ai/obsidian/), para o Lucca escolher o que vira nota. Use quando ele disser "/lacunas", "o que da conversa falta no vault", "o que vale anotar", "o que eu perguntei que não está no obsidian".
effort: medium
allowed-tools: Bash(bash:*), Bash(grep:*)
---
# /lacunas

Mensagens do Lucca nesta sessão:

!`bash "$(git rev-parse --show-toplevel)/.claude/skills/lacunas/mensagens.sh" ${CLAUDE_SESSION_ID}`

## Passos

1. **Conceitos, não mensagens.** Das mensagens acima e das respostas dadas, tire os conceitos e
   as perguntas de "por quê / como funciona". Junte o que é o mesmo assunto (três perguntas sobre
   psql = um item). Fora: comando que só se roda uma vez, erro já resolvido sem lição, decisão que
   já está no escopo da branch ou numa issue.
   (2026-10-23) Fora também o que um `/lacunas` anterior da mesma conversa já mostrou, escolhido
   ou não: o que o Lucca não escolheu está negado e não volta.
2. **Um `grep` por item** em `ai/obsidian/`, com 2–3 termos e sinônimos
   (`grep -rn -i -E "psql|\\\\dt" ai/obsidian/ | cut -c1-160 | head -5`). Não abrir página inteira.
3. **Classificar**: `falta` (nenhum resultado), `parcial` (citado sem explicar), `tem` (explicado:
   sai da tabela, só conta no rodapé).
4. **Tabela**, numerada, `falta` antes de `parcial`:

   | # | Conceito / pergunta | Status | Hoje no vault | Página sugerida |
   |---|---|---|---|---|
   | 1 | Por que a URL do banco usa o nome do serviço, não o IP | parcial | `Conceitos/IP, porta e rede de containers.md:47` | mesma página |

   - "Conceito / pergunta" em palavras do Lucca, uma linha.
   - "Página sugerida": página existente de `Conceitos/` ou `Estrutura do projeto/` quando cabe nela;
     página nova só se o assunto não cabe em nenhuma.
5. Rodapé: `Já no vault: <itens com status tem>` e `Busquei: <termos>` (para ele ver se faltou
   sinônimo).
6. Feche perguntando quais números entram. **Não escreva nota** antes da escolha; escolhidos os
   números, siga `/nota` (regras de página).
