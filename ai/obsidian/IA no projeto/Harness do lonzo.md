---
tags: [noteproject, ia, arquitetura]
---
# Harness do lonzo

O [[Chat com o workspace|chat]] criava notas no lugar errado e citava pastas internas nas respostas, mesmo com o `CLAUDE.md` do workspace em dia. A nota ia para a raiz quando o modelo esquecia o `folder_id`, que era opcional, e ia para o `kb/` porque nada dizia que aquela pasta não era da pessoa. Regra nova no prompt não resolvia: um texto escrito pelo modelo dependia de o próprio modelo obedecer.

A raiz era o [[Laço de ferramentas|harness]]. O `lonzo` já tinha o laço e as ferramentas, e faltavam as peças que o Claude Code põe em volta do modelo. A regra daqui em diante: o que precisa acontecer sempre fica no código, e o texto guarda só o que depende do julgamento do modelo.

## As peças

| Peça | Claude Code | `lonzo` antes | `lonzo` agora ✅ |
|---|---|---|---|
| instruções fixas | system prompt do programa | nenhuma; sem workspace, o `system` ia vazio | `base_rules.md`, igual em toda pergunta |
| onde estou | pasta de trabalho no pacote | id da pasta, só se o modelo o escreveu no `CLAUDE.md` | data e pasta atual, geradas pelo código |
| escrita | `Write` exige caminho absoluto | `folder_id` opcional, com a raiz como padrão | caminho inteiro começando em `/` |
| skills | lista gerada dos arquivos | só notas soltas, que nenhum código lia | lista gerada com id, título e primeira linha |
| histórico | guarda as chamadas de ferramenta | só o texto | texto, `tool_use` e `tool_result` |
| cache | automático | sem marca nenhuma | duas marcas de [[Cache de prompt\|cache]] |

## Lado a lado

![[harness-lonzo-e-claude-code.drawio.svg]]
*Os dois repetem o mesmo laço com a API da Anthropic; a diferença está em volta dele. O lado do Claude Code é uma visão geral, sem o código dele como fonte.*

O `lonzo` só alcança as notas, e por isso roda no servidor sem permissão nem hook. O Claude Code alcança o disco e o shell da pessoa, então cada chamada pode ser barrada antes de rodar.

## O pacote

![[pacote-do-lonzo.drawio.svg]]
*Do mais fixo ao mais variável: o [[Cache de prompt|cache]] compara o começo do pacote, então uma mudança invalida só o que vem depois dela.*

O `system` virou dois blocos. O primeiro é o `base_rules.md`, igual para todo mundo. O segundo sai de `question_context` em `services/workspaces.py`: data, pasta atual, notas do `.workspace/` e lista de skills. A primeira marca fica no bloco fixo e a segunda é o `cache_control` no topo do `tool_runner`, que acompanha o fim do pacote a cada volta do laço.

> [!example] Medição real (2026-11-05, Haiku 5.5)
> A primeira pergunta de um workspace leu 2.732 tokens do cache e pagou 6 de entrada normal. A pergunta seguinte, com o histórico, leu 10.799 e pagou 8. O número sai no evento final, em `usage.cached_tokens`.

## Caminho inteiro

`create_note` e `create_folder` não têm mais `folder_id`: o caminho sai da raiz e começa com `/`, como `/Física/Ondas/Resumo`. O `/` é o que separa um caminho inteiro de um chute: `kb/resumo` volta como erro para o modelo, em vez de virar uma pasta na raiz. Um nome só, como `/resumo`, é um caminho válido e cria na raiz: o caminho obriga o modelo a dizer o destino, mas não garante que seja o certo, e nada impede de escrever em `.workspace/`.

Com pasta no caminho, o primeiro nome precisa existir. Pastas faltando no meio são criadas, mas um primeiro nome desconhecido costuma ser engano, e criar a pasta de raiz exige um `create_folder` explícito. O `ichiro` ganhou `GET /notes/{id}/path`, que dá o caminho de uma pasta a partir do id que a conversa guarda.

`create_note` devolve o id da nota, para o modelo editá-la sem listar a pasta.

## Skills

O `lonzo` lista `.workspace/skills/` a cada pergunta, sem depender do `CLAUDE.md`. Só a primeira linha de cada skill entra no pacote, e por isso o `create_workspace.md` exige que ela diga o que a skill faz. O modelo lê a skill inteira com `read_note` quando a pergunta pede. A lista garante que o modelo saiba da skill, não que a use; para garantir o uso, falta o comando `/` previsto em [[Workspace no app]]. ⏳

## Inventário de skills

(2026-11-06, issue #161) A aba Skills mostra as skills de cada workspace e as publicadas.

| Skill | Onde mora | Quem vê | Editar |
|---|---|---|---|
| privada | nota em `.workspace/skills/` | só o dono | no editor ou pelo chat |
| publicada | linha na tabela `skills` do banco `lonzo` | todo mundo logado | só publicando de novo |

- A tabela guarda só as publicadas: uma cópia privada lá ficaria desatualizada, porque o navegador salva a nota direto no `ichiro`, sem passar pelo `lonzo`.
- Publicar é uma foto do momento. `note_id` diz de qual nota veio, e publicar de novo atualiza a mesma linha. Não é FK, porque as notas ficam em outro banco.
- A seção "Add" separa "Everyone" (as dos outros) de "Mine" (as suas), e esconde o que o workspace já tem.
- Adicionar sempre copia, de uma skill publicada ou de outro workspace da pessoa. As cópias são independentes: editar uma não muda as outras.
- O chat continua lendo só as notas, então nada muda no pacote da pergunta.
- ⏳ Falta despublicar e moderar antes de abrir para outras pessoas: skill pública é texto de outro virando instrução para a IA.

## Histórico

Cada turno do modelo vira uma mensagem no banco, e o resultado das ferramentas vira a mensagem seguinte. Assim a próxima pergunta sabe o que foi criado e onde. O custo é levar o texto das notas lidas nas perguntas seguintes; o cache alivia, e cortar resultados grandes fica para quando pesar. O `chimchar` pula os turnos sem texto ao reabrir uma conversa.

## Ainda falta ⏳

- hooks: a pasta existe, mas nenhum código a lê;
- comando `/` para chamar uma skill;
