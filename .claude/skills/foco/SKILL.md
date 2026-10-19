---
name: foco
description: Mantém a branch no que ela se propôs a fazer. Cria o escopo ai/kb/escopos/<branch>.md (Pedido / Contexto / Fora) ou confere se a conversa e o diff saíram dele. Use quando o Lucca disser "/foco", "estou fugindo do escopo?", "isso é dessa branch?", "o que falta da branch", ou ao começar uma branch sem escopo.
argument-hint: "[branch]"
---
# /foco [branch]

O aviso é automático: a cada prompt, o hook `ai/tools/foco.py` (UserPromptSubmit) pega a branch atual
e um juiz à parte (`claude -p`, Haiku, sem ferramentas nem CLAUDE.md, ~3 s) lê só o escopo + a
mensagem. Fora do Pedido → `⚠ Foco (<branch>, fora|contexto): <motivo>`; senão, nada. Na
`master` não roda. `python3 ai/tools/foco.py --listar` mostra os escopos.

## A. Criar o escopo
1. Do que a branch trata: o pedido do Lucca, o nome da branch, a página do plano no Obsidian
   (`Plano do projeto/Roadmap`, `IA no projeto/Ordem de implementação`).
2. Escreva `ai/kb/escopos/<branch>.md` (`/` no nome vira `__`):
   ```
   ---
   id: add-a-few-decorations-in-code-mirror
   nome: Chips de [!duvida] e [fix] no editor
   areas: [editor]
   ---
   ## Pedido (o que a branch entrega; cada item verificável)
   1. ...
   ## Contexto (pode tocar só o mínimo para o Pedido funcionar)
   - ...
   ## Fora (vira outra branch)
   - ...
   ```
   - Pedido só o que foi pedido; nada inferido. Áreas de `ai/kb/areas.yaml`.
   - Fora começa com o óbvio vizinho; cresce a cada desvio confirmado.
3. Mostre o Pedido (lista curta) para ele aprovar.

## B. Conferir
1. Leia o escopo e `git diff master...HEAD --stat` (e o trecho que importa).
2. Até ~8 linhas: Pedido item → feito / falta (arquivo); o que no diff ou na conversa está em
   Contexto além do mínimo, ou em Fora; próximo passo.
3. Desvio confirmado ("isso não é dessa branch") → acrescente em **Fora**.
