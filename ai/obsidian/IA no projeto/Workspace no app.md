---
tags: [noteproject, ia, arquitetura]
---
# Workspace no app

Hoje o workspace de IA do projeto é o Claude Code no terminal, com regras, skills, agentes, scripts e hooks em arquivos. Quem usa o app não precisa saber nada disso nem ter o Claude Code: o app tem as mesmas peças por dentro, e cada pessoa monta o workspace da área dela (programação, baseball, uma matéria).

## Para que serve

O objetivo de um workspace é a IA entender o máximo de um assunto gastando poucos tokens: sem depender de um chat longo onde o contexto vai sendo injetado, e sem ensinar de novo, a cada conversa, os gostos de quem pergunta.

| Vantagem | Como | Sem workspace |
|---|---|---|
| gostos ditos uma vez | a nota "como responder" entra em toda pergunta | repetir "seja curto" em cada chat |
| conversa curta | o estado datado diz onde parou; uma conversa nova continua dali | um chat gigante, relido a cada mensagem |
| ler só o trecho | as fontes dizem onde está cada coisa, e as ferramentas devolvem a seção ([[Gastar poucos tokens]]) | colar a nota inteira |
| começo barato | regras fixas no começo do pacote, que o [[Cache de prompt\|cache]] reaproveita | pagar o contexto cheio toda vez |
| um assunto não polui outro | cada workspace só alcança a própria pasta | o modelo mistura baseball com cálculo |
| melhora com o uso | "responde mais curto" muda a regra; o fim de uma conversa atualiza o estado | a correção morre com o chat |
| à vista e editável | tudo é nota comum, e o [[#Mapa do workspace\|mapa]] mostra as ligações | memória escondida do provedor |
| não preso a um modelo | texto puro, lido por qualquer provedor ([[Sem Claude Code — provedores]]) | o contexto fica dentro de um produto |
| igual em todo aparelho | sincroniza com as notas | contexto num PC só |

## As peças

| Peça | No Claude Code | No app |
|---|---|---|
| regras | `CLAUDE.md`, regras de página | notas de regra, editáveis |
| ferramentas | ler arquivo, `grep`, editar | buscar nota, ler seção, criar nota, propor [[Edição por âncora\|edição]] |
| [[Laço de ferramentas\|laço]] | o Claude Code chama o modelo, executa a ferramenta, repete | serviço de IA no servidor, com o `tool_runner` da lib `anthropic` ([[Chat com o workspace]]); em segundo plano, o worker da [[Fila de pedidos]] |
| modelo | Claude, pela assinatura | Claude pela chave de API no chat; na fila, o que a pessoa escolher ([[Sem Claude Code — provedores]]) |

## Onde fica

Numa pasta `.workspace/` dentro de qualquer pasta do vault (a coleção de notas): cada pasta que tem uma é um workspace, um por assunto (`Faculdade/`, `Baseball/`), como cada pasta de projeto no PC tem o próprio `.claude/`. Um `.workspace/` na raiz vale para todos, como o `~/.claude/`. Ele sincroniza junto com as notas, então o mesmo workspace aparece no navegador, no desktop e no celular, e cada conversa do [[Chat com o workspace|chat]] pertence a um deles.

| Tipo | Exemplo | Quem usa | Sincroniza |
|---|---|---|---|
| texto para o modelo | regras, skills, agentes (`.md`) | o laço | sim |
| scripts | `lint.ts`, `diagrama.py` | o executor | sim |
| hooks | ao salvar nota → lint | o app, em eventos | sim |
| config | `modelos.yaml`, `fontes.yaml` | o app | sim |
| segredos | chave de API | o worker | **não**, fica por aparelho ou no servidor, cifrada |

## Quem mantém o quê

| Camada | Quem mantém | Exemplo |
|---|---|---|
| núcleo | o app | editor, sync, fila, executor, ferramentas, lista de eventos de hook |
| esqueleto e catálogo | o app | as seções de todo workspace; skills prontas para marcar |
| workspace da pessoa | a pessoa | skills de baseball, regras dela, scripts dela |

- O app mantém a API das ferramentas e dos eventos, pequena e versionada, e não as skills de ninguém (o Obsidian faz o mesmo com plugins).
- Quem não sabe nada aperta "Novo workspace", escreve o que quer e usa as skills como botões e comandos `/`. Quem quer mais abre a pasta e cria skills e agentes.
- Quem não programa também pede pelo [[Chat com o workspace|chat]] ("quero estudar cálculo", "responde mais curto"): a IA cria e edita as regras e skills com `create_note` e `edit_note`, sem a pessoa ver arquivo.

## Como nasce

Um kit fixo ("Estudo": uma regra e duas skills) serve mal a assuntos diferentes: o que se repete entre os workspaces do Claude Code no PC (NoteProject, Disciplinas e as matérias, baseball) é a forma do `CLAUDE.md`, não as skills. Então o app guarda um esqueleto, e a IA o preenche a partir do que a pessoa quer.

| Seção (nota no `.workspace/`) | Para quê | No Claude Code do PC |
|---|---|---|
| objetivo e quem | o assunto e o que a pessoa quer dele | "Quem", "Papel do Claude aqui" |
| como responder | os gostos, ditos uma vez | regras de resposta |
| fatos fixos | o que não muda e não precisa ser repetido | "Fatos fixos do atleta" |
| estado datado | onde parou e o que vem a seguir | "Estado", "Memória do atleta" |
| fontes | onde está cada coisa, para ler só o trecho | KB, cards, `ai/np contexto` |

1. A pessoa escreve um texto breve (objetivo, nível, como gosta das respostas) ou responde a umas cinco perguntas fixas.
2. O `lonzo` faz uma [[Chamada a um modelo|chamada]] só, sem [[Laço de ferramentas|laço]]: manda o esqueleto e o texto, e o modelo devolve a lista de notas preenchidas.
3. O `lonzo` grava as notas no `.workspace/` da pasta pela [[API de notas]].
4. Opcional: a pessoa marca skills prontas de um catálogo, tiradas das que já existem entre os projetos (desenho, relatório, resumo, commit), copiadas para `.workspace/skills/`.

- O `/nova-materia` do Disciplinas faz o mesmo à mão: monta o workspace de uma matéria nova no padrão comum.
- Perguntas guiadas e catálogo podem vir depois; o mínimo é o esqueleto preenchido pelo texto breve.

## Liberação em fases

| Fase | O que a pessoa pode criar | Por quê nessa ordem |
|---|---|---|
| v1 | regras e skills em `.md` | texto quase não quebra com atualização do app |
| v2 | agentes | ainda texto, com ferramentas escolhidas |
| v3 | scripts e hooks, rodando em [[Sandbox]] no servidor | código quebra e pode ser malicioso; primeiro só os scripts do dono, depois os de qualquer pessoa com isolamento forte |

## Scripts

Um script é texto, como uma nota: fica na mesma tabela `notes` (`title` e `body` são `Text`, `apps/ichiro/migrations/versions/e7dd73f8b32e_create_notes.py:46-47`), na pasta `.workspace/scripts/`. A linguagem começa em Python, que roda no servidor e dá o mesmo resultado de qualquer cliente.

```python
# .workspace/scripts/contar_palavras.py
"""
name: contar_palavras
description: conta palavras de uma nota
params: {titulo: string}
"""
```

| Etapa | Como |
|---|---|
| virar ferramenta | a cada pergunta, o serviço de IA lê os scripts daquela pessoa e põe os cabeçalhos em `tools` ([[Chamada a um modelo]]) |
| mudar | a pessoa ou a IA edita a nota; a próxima pergunta já usa a versão nova, sem deploy |
| rodar | o serviço passa o `body` a um Python dentro de um [[Sandbox\|sandbox]] e devolve a saída ao modelo |

- O script não alcança banco, chave nem rede; nota de que precise vem como entrada.
- Script escrito pela IA não passou por revisão: por isso todo script roda no [[Sandbox|sandbox]].

## Como um pedido roda

O [[Chat com o workspace|chat]] chama o modelo direto, porque alguém espera a resposta. Pedido em segundo plano vira um job numa fila: o worker que pega o job monta o contexto com o `.workspace/` e a seção da nota, chama o provedor e devolve uma proposta.

![[ia-job.drawio.svg]]
*Do gatilho à proposta: o job espera na fila até um worker que tenha o que ele precisa.*

## Mapa do workspace

Uma tela mostra o "cérebro" do workspace inteiro, para entender como ele faz as coisas e mudar o que quiser sem abrir arquivo.

- **Estrutura**: regras, skills, agentes, hooks e scripts como um grafo. Cada peça declara no frontmatter do que depende (`usa:`, `gatilho:`), e o app desenha as ligações.
- **Por quê**: cada job guarda quais regras e skills usou; numa nota gerada dá para ver de onde veio cada decisão.
- **Editar**: clicar numa peça abre a regra ou a skill para mudar ali mesmo.

## Em aberto

- Desenho do mapa do workspace (grafo, camadas ou lista).
- Comunidade para publicar e baixar skills e esqueletos.
- Quais são as cinco perguntas iniciais.
- Segurança de scripts: sandbox (Web Worker para JS) e confirmação antes de rodar script de workspace importado; defeito de script não pode estragar nota (a saída passa pela mesma validação das [[Blocos padronizados|respostas da IA]]).
