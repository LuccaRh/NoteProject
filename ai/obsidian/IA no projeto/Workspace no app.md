---
tags: [noteproject, ia, arquitetura]
---
# Workspace no app

Hoje o workspace de IA do projeto é o Claude Code no terminal, com regras, skills, agentes, scripts e hooks em arquivos. Quem usa o app não precisa saber nada disso nem ter o Claude Code: o app tem as mesmas peças por dentro, e cada pessoa monta o workspace da área dela (programação, baseball, uma matéria).

## As peças

| Peça | No Claude Code | No app |
|---|---|---|
| regras | `CLAUDE.md`, regras de página | notas de regra, editáveis |
| ferramentas | ler arquivo, `grep`, editar | buscar nota, ler seção, criar nota, propor [[Edição por âncora\|edição]] |
| laço | o Claude Code chama o modelo, executa a ferramenta, repete | worker do app ([[Fila de pedidos]]) |
| modelo | Claude, pela assinatura | o que a pessoa escolher ([[Sem Claude Code — provedores]]) |

## Onde fica

Numa pasta `.workspace/` dentro do vault (a coleção de notas), como a `.obsidian/`. Ela sincroniza junto com as notas, então o mesmo workspace aparece no navegador, no desktop e no celular.

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
| kits | o app (poucos) | "Estudo", "Programação": uma `.workspace/` pronta para copiar |
| workspace da pessoa | a pessoa | skills de baseball, regras dela, scripts dela |

- O app mantém a API das ferramentas e dos eventos, pequena e versionada, e não as skills de ninguém (o Obsidian faz o mesmo com plugins).
- Quem não sabe nada aperta "Novo workspace", escolhe um kit e usa as skills como botões e comandos `/`. Quem quer mais abre a pasta e cria skills e agentes.

## Liberação em fases

| Fase | O que a pessoa pode criar | Por quê nessa ordem |
|---|---|---|
| v1 | regras e skills em `.md` | texto quase não quebra com atualização do app |
| v2 | agentes | ainda texto, com ferramentas escolhidas |
| v3 | scripts e hooks, só no app desktop | código quebra e pode ser malicioso; o navegador não roda programa |

## Como um pedido roda

Todo pedido de IA vira um job numa fila. O worker que pega o job monta o contexto com o `.workspace/` e a seção da nota, chama o provedor e devolve uma proposta.

![[ia-job.drawio.svg]]
*Do gatilho à proposta: o job espera na fila até um worker que tenha o que ele precisa.*

## Mapa do workspace

Uma tela mostra o "cérebro" do workspace inteiro, para entender como ele faz as coisas e mudar o que quiser sem abrir arquivo.

- **Estrutura**: regras, skills, agentes, hooks e scripts como um grafo. Cada peça declara no frontmatter do que depende (`usa:`, `gatilho:`), e o app desenha as ligações.
- **Por quê**: cada job guarda quais regras e skills usou; numa nota gerada dá para ver de onde veio cada decisão.
- **Editar**: clicar numa peça abre a regra ou a skill para mudar ali mesmo.

## Em aberto

- Desenho do mapa do workspace (grafo, camadas ou lista).
- Comunidade para publicar e baixar skills e kits.
- Segurança de scripts: sandbox (Web Worker para JS) e confirmação antes de rodar script de workspace importado; defeito de script não pode estragar nota (a saída passa pela mesma validação das [[Blocos padronizados|respostas da IA]]).
