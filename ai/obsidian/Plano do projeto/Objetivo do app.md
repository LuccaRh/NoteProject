---
tags: [noteproject, plano]
---
# Objetivo do app

O projeto começou como um anotador grátis entre PC, celular e navegador, para usar nas aulas e em casa. Com o uso de [[00 Mapa — IA no projeto|IA]] para gerar notas e revisar, o Obsidian virou um gargalo: não foi feito para isso. O app junta as duas coisas.

## Motivos, em ordem

| # | Motivo | O que pede do app |
|---|---|---|
| 1 | aprender construindo: servidor, banco, sync, auth, infra | a trilha inteira de backend e infra feita à mão ([[Roadmap]]) |
| 2 | uso diário: a IA gera notas no PC e elas são revisadas e estudadas | ler e navegar notas organizadas, com links |
| 3 | vários aparelhos com IA (ler e gerar notas pelo tablet) | sync e [[Fila de pedidos\|fila]] entre aparelhos |
| 4 | desenhado para várias pessoas, de áreas diferentes | contas, workspace por pessoa, nada preso a uma área |

O motivo 4 também é aprendizado: lidar com várias pessoas faz parte do que se quer aprender.

## O que o Obsidian não resolve

| Hoje no Obsidian | No app |
|---|---|
| app grátis, mas o sync é pago | sync próprio, grátis |
| a IA chega às notas por um timer que copia vault ↔ repo | a IA trabalha dentro do app ([[Workspace no app]]) |
| marcas como `[!duvida]` são texto solto | marcas viram dados e pedidos ([[Marcar dúvida]]) |
| uso pelo mouse em boa parte | uso inteiro pelo teclado |
| escrita à mão em outro app | escrita com caneta no tablet, depois (⏳) |

## v1

A primeira versão que substitui o Obsidian no uso diário: **ler e navegar notas `.md` organizadas, com links entre elas, no navegador, com as notas no servidor na AWS**. A v1 não tem IA: as notas são escritas no editor do app ou importadas do Obsidian. A IA entra depois, já dentro do app ([[Workspace no app]]), e não pelo Claude Code com arquivos locais.

| Opção | Onde as notas ficam | Ensina | Pronta em |
|---|---|---|---|
| pasta local | arquivos no PC | quase nada de backend | rápido |
| servidor em localhost | Postgres no PC | servidor e banco | fim do M1 |
| **servidor na AWS** | Postgres na [[EC2]] | servidor, banco, login, [[TLS e HTTPS\|TLS]], deploy | fim do M3 |

Escolha: servidor na AWS, porque o motivo 1 vem antes do 2. Servidor aberto na internet exige login, então a v1 só fica pronta no fim do M3 (M0 servidor → M1 notas → M2 login e TLS → M3 AWS). Até lá, rodar em localhost é teste, não uso.

## Depois da v1

- IA dentro do app, com o workspace de cada pessoa ([[Workspace no app]]).
- Estudar fontes de fora (repo, PDF, dados) e gerar notas ([[Fontes de dados]]).
- App desktop e celular, com o mesmo front.
- Escrita com caneta; uma skill pode passar o escrito para texto.
- Comunidade de skills prontas.

## Revisar se...

- o uso diário não puder esperar o M3 → servir a v1 em localhost antes, sem login;
- o Obsidian continuar sendo aberto depois da v1 → o que falta nela vira a próxima issue.
