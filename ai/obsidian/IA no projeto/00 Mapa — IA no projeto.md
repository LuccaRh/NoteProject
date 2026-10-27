---
tags: [noteproject, ia]
---
# IA no projeto de notas — mapa

Um app de notas com IA pode ser só isto: um editor, arquivos `.md` como banco e o Claude Code escrevendo neles. O NoteProject vai além: o app tem o próprio [[Workspace no app|workspace]], e quem usa não precisa do Claude Code.

Ideia central: **o app funciona inteiro sem IA**. A IA é mais um cliente das notas: no navegador, um worker do servidor; no app desktop, um worker do [[O daemon notesd|daemon]]. Recebe pouco contexto e devolve pouca coisa.

## Base

| Página | Ideia |
|---|---|
| [[Workspace no app]] | regras, skills, scripts e hooks numa pasta do vault; núcleo do app, kits e o workspace de cada pessoa |
| [[O daemon notesd]] | um processo é dono do [[SQLite]]; todo mundo fala com ele |
| [[MCP — a IA como cliente do daemon]] | o Claude Code chama funções do [[O daemon notesd\|daemon]] em vez de ler arquivos |
| [[Edição por âncora]] | a IA nunca reescreve a nota; propõe uma operação presa a um trecho |

## O que a IA faz

| Página | Ideia |
|---|---|
| [[Marcar dúvida]] | selecionar + `Ctrl+D`; vira um callout que o Obsidian também lê |
| [[Fila de pedidos]] | marcar e pedir a resposta no editor, sem ir ao terminal |
| [[Blocos padronizados]] | a IA preenche moldes (passos, quem é quem...); o [[O daemon notesd\|daemon]] escreve o Markdown |
| [[Figuras geradas]] | a IA escreve a receita (YAML, script); o [[O daemon notesd\|daemon]] gera a imagem |
| [[Classificar a nota pelo tema]] | o tema vem de uma lista fechada, para saber que card carregar |
| [[Fontes de dados]] | repo, PDF ou dados viram notas por jobs pequenos, com `arquivo:linha@commit` |

## Custo e acesso

| Página | Ideia |
|---|---|
| [[Gastar poucos tokens]] | as decisões acima, vistas pelo gasto |
| [[Sem Claude Code — provedores]] | o que funciona sem IA, com modelo local, com API e com Claude Code |

## Próximo passo

[[Ordem de implementação]]: as partes sem IA vêm antes, porque são o que a IA usa depois.
