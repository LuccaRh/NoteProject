---
name: diagrama
description: Desenha em draw.io, a partir de um YAML, diagramas de arquitetura, fluxo de dados, sequência em blocos e deploy do NoteProject (lib ai/tools/diagrama.py herdada do Disciplinas, sem colisão, conferido no PNG antes de mostrar) e embute o .drawio.svg na nota do Obsidian. Use quando o usuário disser "/diagrama", "desenha", "faz um desenho de", "diagrama da arquitetura", "drawio".
argument-hint: "<nome> [o que desenhar]"
---
# /diagrama <nome>

O **YAML é a fonte da verdade**; o `.drawio` é a vista (editar o .drawio não volta para o YAML).

1. **Do que é o desenho.** Leia a fonte do que ele representa (`ai/np contexto <área>`, a nota
   do vault). Peça sem fonte → marque *(geral)* na legenda.
2. **YAML** em `ai/kb/diagramas/<nome>.yaml`. Rascunhe a grade antes: que nó em que `[col, lin]`;
   fluxo da esquerda para a direita (cliente → servidor → dados) ou de cima para baixo (camadas);
   retorno numa linha embaixo.
3. **Gere**: `ai/np diagrama ai/kb/diagramas/<nome>.yaml --png`. COLISAO → mexa na grade e gere de
   novo. **Abra o PNG (Read, `build/diagramas/<nome>.png`) e olhe**: texto legível, setas certas.
4. **Embuta**: `destino:` no YAML copia o `.drawio.svg` para `ai/obsidian/<destino>/`; na página,
   `![[<nome>.drawio.svg]]` + legenda de uma linha. `ai/np obsidian`.
5. **Checkpoint:** caminho do `.drawio`, suposições, o que ficou *(geral)*. Espere o usuário.

## Formato do YAML
```yaml
titulo: Três camadas
tipo: blocos
grade: [180, 110]            # px por coluna / por linha
destino: Estrutura do projeto/Figuras   # opcional: pasta em ai/obsidian/ que recebe o .drawio.svg
nos:
  gui:  {tipo: bloco, pos: [0, 0], texto: "GUI<br>(CodeMirror)", cor: azul}
  d:    {tipo: bloco, pos: [1, 0], texto: "notesd", cor: verde}
  db:   {tipo: banco, pos: [1, 1], texto: "SQLite<br>+ FTS5", cor: amarelo}   # cilindro
  srv:  {tipo: bloco, pos: [3, 0], texto: "servidor", cor: laranja}
  dev:  {tipo: grupo, contem: [gui, d, db], texto: "Dispositivo", cor: cinza}
  n1:   {tipo: nota, pos: [3, 1], texto: "só sincroniza"}
arestas:
  - [gui, d, {rotulo: "HTTP"}]
  - [d, db]
  - [d, srv, {rotulo: "WebSocket", tracejada: true}]
legenda: {WS: "WebSocket com o token do dispositivo"}
```
- Quebra de linha no texto: `<br>` (o rótulo é HTML; `\n` não quebra).
- Nós: `bloco`, `banco` (cilindro), `nota`, `grupo` (pode conter grupo), `entrada`, `saida`,
  `ramo`; os de circuito (`resistor`...) também existem, herdados.
- Portas `e d c b` (esquerda, direita, cima, baixo): `[a.b, b.c]`. Sem porta, a lib escolhe.
- ER: nó `tabela` com `colunas: [[nome, tipo, PK|FK|UQ, "null"]]`, `extras: [[ix, texto]]`, `nota`; porta `d:coluna`
  liga na linha da coluna; aresta com `pontas: [ERmany, ERmandOne]`. `escuro: true` no topo e `forte: true` no grupo
  (modelo: `esquema-do-postgres.yaml`).
- Opções de aresta: `rotulo`, `seta`, `tracejada`, `sai`, `entra`, `por`, `nivel`, `pontos`, `lado_rotulo`.
- Cores: azul (front), verde (back), laranja (servidor), amarelo (dados), roxo (infra), vermelho
  (segurança), cinza (grupo). Mantenha essa convenção entre desenhos.
