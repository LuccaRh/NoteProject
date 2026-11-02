---
name: duvida
description: Responde dúvidas e aplica correções e comentários marcados nas notas do NoteProject no Obsidian (> [!duvida], [duvidas], [fix], [coment]) ou sobre um trecho de nota. Use quando o usuário disser "/duvida", "marquei dúvidas", "comentei nas notas", "arruma as notas", "não entendi esse trecho".
argument-hint: "[página | texto da dúvida]"
---
# /duvida [página | pergunta]

Marcas no ponto exato da página:
```
> [!duvida] por que o token não vai num cookie?
[duvidas] o que é um sidecar?
[fix] tira a parte de Redis daqui
[coment] acho que não faz sentido passar pelo Claude Code
```

1. `ai/np obsidian` (puxa o que ele escreveu agora). Conflito na página → pare e avise.
2. `ai/np duvidas [trecho do nome]`. Pergunta solta no chat → localize o trecho em `ai/obsidian/`,
   responda no chat e só edite a página se ele pedir. Nenhuma achada → mostre o formato acima.
3. Para cada uma: leia a **seção inteira** em volta; identifique a área (`ai/kb/areas.yaml`) e use a
   fonte dela (código por trecho, card `ai/kb/libs/`, nota do vault). Nada de cabeça.
4. Aplique (regras em `.claude/skills/nota/regras.md`, "Dúvidas e marcas"):
   - `[!duvida]`/`[duvidas]` → apague a marca e reescreva a seção até ela responder; a pergunta
     vai para `## Dúvidas` no fim (lista numerada, redação dele, sem resposta).
   - `[fix]` → aplique e apague; se vale para outras páginas, vira regra em `regras.md`.
   - `[coment]` → é opinião/decisão dele: ajuste o texto (ou a decisão) para refleti-la, ou, se
     discorda com motivo técnico, responda no chat em 2–4 linhas e deixe a marca até ele decidir.
     Comentário que muda o plano → atualize também a página do plano (ex.: `Ordem de implementação`).
5. `ai/np obsidian` e `ai/np duvidas` (confere que não ficou pendente).
6. No chat: uma linha por marca (página:linha, o que fez). Não cole a página.
