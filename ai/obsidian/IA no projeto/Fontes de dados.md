---
tags: [noteproject, ia]
---
# Fontes de dados

Para entender um projeto (um repo no GitHub, um PDF, uma planilha), hoje o trabalho é pedir ao Claude Code que leia e escreva as notas. No app, a fonte é configurada uma vez e o estudo vira uma sequência de jobs da [[Fila de pedidos]]. Tudo aqui é plano (⏳).

## Fluxo

1. **Fonte**: repo, pasta, PDF ou CSV, em `fontes.yaml` do [[Workspace no app|workspace]].
2. **Importar**: o executor baixa o conteúdo e indexa em pedaços (busca por palavra; embeddings depois).
3. **Estudar**: uma skill gera jobs pequenos: mapa da estrutura → uma nota por módulo → visão geral e diagramas.
4. **Ligar**: cada nota aponta para `arquivo:linha@commit`.
5. **Atualizar**: commit novo gera job só para as partes que mudaram.

## Por que jobs pequenos

- Cada job leva só o pedaço de que precisa, como na [[Fila de pedidos]]: a IA não procura nada.
- Modelo aberto pequeno dá conta de um pedaço por vez; o estudo inteiro fica lento, mas grátis ([[Sem Claude Code — provedores]]).
- Importar repo e rodar `git` exige o app desktop ou o servidor; o celular só cria o job.
