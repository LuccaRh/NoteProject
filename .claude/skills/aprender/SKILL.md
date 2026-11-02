---
name: aprender
description: Ensina do zero um conceito de sistemas/infra/backend (CRDT, WebSocket, reverse proxy, TLS, JWT x session, backup, CI/CD, índices...) ligado a onde ele aparece no NoteProject, e fecha com um exercício que o usuário implementa no projeto. Grava a página do conceito em Note Project/Conceitos/ e o uso nas páginas do projeto. Use quando ele disser "/aprender", "quero entender X", "como funciona X", "me ensina X para usar no projeto".
argument-hint: "<conceito>"
---
# /aprender <conceito>

O objetivo é o usuário **saber fazer**, não ler sobre: a página prepara, o exercício ensina.

1. **O que ele já tem.** `grep -ril "<conceito>"` em `ai/obsidian/` (primeiro `Conceitos/`): ele já escreveu
   sobre isso?
   Use as palavras de lá e não repita.
2. **Uma pergunta** ao usuário: o que ele já sabe do pré-requisito e se quer teoria curta ou
   direto ao exercício. Espere.
3. **Página do conceito** em `ai/obsidian/Conceitos/<pasta>/` (entra no `00 Mapa — Conceitos`, na seção da pasta; já
   existe → amplie em vez de criar outra), seguindo `.claude/skills/nota/regras.md`:
   de onde vem → para que serve → como funciona (com figura `/diagrama` se tem fluxo) → onde
   aparece (mercado) → erros comuns. Fonte: doc oficial ou código; marque *(geral)* o que
   é de conhecimento geral sem fonte conferida.
4. **Uso no projeto** em `ai/obsidian/` (página da área ou seção nova): onde o conceito entra, qual
   decisão ele muda, link para a página geral.
5. **Exercício** (no chat e no fim da página do projeto, `## Exercício`): uma tarefa pequena no
   repo, com o critério de pronto verificável (teste, `curl`, `docker compose ps`). Ele faz; você
   revisa e roda. Exercício de área `aprender: true` não vem resolvido.
6. `ai/np obsidian`. No chat: páginas criadas e o exercício. Não cole as páginas.

Chat curto (regras de resposta); explicação longa vai para a página.
