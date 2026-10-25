---
tags: [noteproject, workspace]
---
# Esqueleto de tarefas

Uma tarefa passa sempre pelas mesmas etapas: issue, branch, escopo, código, revisão, check e commit. Hoje quem conduz essas etapas é a `/tarefa`, conversando, e cada passo gasta tokens. O esqueleto passa o que é fixo para script e hook, e deixa para a IA só o que pede julgamento.

Dois limites guiam o desenho:
- **Quem escreve o quê**: o backend e a infra são escritos à mão (áreas `aprender`); o frontend, pela sessão, com o mínimo de revisão.
- **Poucos tokens**: cada subagente começa sem contexto e relê o que precisa. Agente só entra onde lê pouco e devolve pouco.

## Opções

| | Motor de fluxos | Esqueleto leve |
|---|---|---|
| O que é | script que chama um agente por etapa (analista, dev, revisor...) e para nos portões | scripts e hooks nas etapas fixas; a sessão e um agente revisor no resto |
| Quem escreve o código | agente dev | à mão (backend) ou a sessão (front) |
| Tokens | um agente por etapa, cada um relendo o contexto | só a sessão e o revisor, quando pedido |
| Peças | fluxos como dados, estado em disco, runner `claude -p` | 2 comandos no `ai/np`, 2 hooks, 1 agente, 1 card |

**Escolha: esqueleto leve.** O motor serve a quem delega o código; aqui o código de backend é o próprio exercício, e o agente dev não teria papel. Para uma pessoa e poucas tarefas, as peças do motor custam mais do que economizam.

## As peças

Sem custo de token:

| Peça | O que faz | Estado |
|---|---|---|
| `ai/np tarefa N` | branch da `master` atualizada, escopo a partir da issue, contexto da área | ⏳ |
| `ai/np check --curto` | roda o `make check` e mostra só o que falhou, com arquivo:linha | ⏳ |
| hook de push | barra `git push`, `--force` e `gh pr merge` sem ok | ⏳ |
| hook `Stop` | barra "passa"/"funciona" sem um check rodado depois da última edição; só confere, não roda | ⏳ |
| `ai/np contexto <área>` | lista o que ler para a área (faz o papel de um agente explorador) | ✅ |
| `ai/np status` | branch, escopo, mudanças, marcas pendentes | ✅ |

Com pouco token:

| Peça | O que faz | Estado |
|---|---|---|
| agente `revisor` | Sonnet, esforço baixo; lê só o diff e o escopo, devolve até ~15 linhas com arquivo:linha; roda quando pedido, para o código escrito à mão | ⏳ |
| card do front em `ai/kb/` | componentes, CodeMirror, chamada à `/api`; a sessão escreve o front sem reler `apps/web` | ⏳ |
| agente `leitor` | lê arquivo grande e devolve o trecho | ✅ |

O briefing do `revisor` tem forma fixa: **objetivo · leia antes · restrições · entregue · pronto quando**. Na terceira rodada de revisão da mesma mudança ele para e pede decisão (quebrar a mudança, rever o escopo) em vez de seguir.

## O caminho de uma tarefa

```
issue #N
 → ai/np tarefa N          branch + escopo + contexto da área
 → área aprender?          sim: /aprender, código à mão │ front: a sessão escreve
 → agente revisor          quando pedido, até 3 rodadas
 → hook Stop               sem saída do check, não encerra dizendo que passa
 → /commit                 hook barra push e merge
 → ok → PR
```

## Fora, de propósito

- Agente dev e agente explorador: o código de backend é à mão, e o `ai/np contexto` já explora.
- Loop automático dev ↔ revisor e avaliação do revisor: multiplicam tokens sem ganho em uma pessoa só.
- Cópia do repo por tarefa: uma tarefa por vez não mistura alterações.

## Ordem

1. hook de push (o mais barato e o que protege mais);
2. `ai/np check --curto`;
3. `ai/np tarefa N`;
4. agente `revisor`;
5. card do front.

Revisar se: o frontend passar a ser escrito à mão, houver várias tarefas em paralelo, ou o `revisor` passar a ser chamado em toda mudança (aí o custo dele precisa ser medido).
