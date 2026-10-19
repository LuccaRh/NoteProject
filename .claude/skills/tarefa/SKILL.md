---
name: tarefa
description: Começa ou continua uma funcionalidade do NoteProject do jeito do workspace — branch própria, escopo (Pedido/Contexto/Fora), contexto só da área, passos pequenos conferidos por make check, e o Lucca escrevendo nas áreas de aprender. Use quando ele disser "/tarefa", "vamos fazer X", "implementa X", "próxima feature", "continuar a branch".
argument-hint: "<o que fazer>"
---
# /tarefa <o que fazer>

1. **Onde estamos.** `ai/np status`. Branch atual já é desta tarefa → pule para o 3. Sem tarefa
   dita → próxima issue aberta da milestone atual (`gh issue list -m "<milestone>"`).
2. **Branch + escopo.** Da `master` atualizada: `git switch -c <nome-em-inglês-kebab>`. Nome da branch = título da issue
   em kebab-case. Crie o escopo pela `/foco` (parte A, com o número da issue) e espere o ok do Pedido.
3. **Contexto.** Para cada área do escopo: `ai/np contexto <área>`. Leia só o que ele lista, por
   trecho; API de lib → card `ai/kb/libs/` ou o `.d.ts`/fonte instalada (`grep -n`), nunca de cabeça.
   Lib nova sem card → escreva o card ao descobrir (frontmatter `pacote`, `versao`, `fonte`).
4. **Plano em passos** (≤ 6 linhas no chat): cada passo = um commit que passa no `make check`.
   Decisão de arquitetura (lib nova, mudança de schema, serviço novo) → proponha e espere.
5. **Cada passo:**
   - área com `aprender: true` → explique só o conceito do passo (2–4 linhas, ou `/aprender` se é
     novo), diga **o que** escrever e onde, e espere o código dele; depois revise e rode.
   - outra área → implemente o mínimo do passo.
   - Rode o teste da parte e `ai/np check` (ou `make check-web` se só o front mudou).
     Mostre a linha que prova. Falhou → conserte antes de seguir.
6. **Fecho.** `/commit` (sem push). Atualize "Estado" do `CLAUDE.md` se a etapa mudou. Algo
   aprendido que vale nota → ofereça `/nota` ou `/aprender` (uma linha).

Fora do Pedido (aviso do foco ou percebido) → anote em **Fora** do escopo e siga; vira outra branch.
