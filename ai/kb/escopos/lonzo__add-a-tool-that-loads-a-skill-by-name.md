---
id: lonzo/add-a-tool-that-loads-a-skill-by-name
nome: Ferramenta que carrega skill pelo nome, lado lonzo (issue #196)
areas: [ia]
---
## Pedido (o que a branch entrega; cada item verificável)
1. Ferramenta `load_skill(name)`: acha a skill pelo título entre as da pasta da conversa e as de cima; no empate, vale a mais perto; sem skill com o nome, erro para o modelo.
2. O evento `tool_use` leva o nome da skill em `target`.
3. A lista `# Skills` sai sem ids, e o `base_rules.md` manda usar `load_skill`.
4. lonzo 0.20.0.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- Em cima da `lonzo/send-the-workspace-rules-in-the-messages-instead-of-the-system-prompt`.
- Skills globais, se existirem um dia, entram na mesma busca.

## Fora (vira outra branch)
- Rótulo do status no front (`chimchar/add-a-tool-that-loads-a-skill-by-name`).
- Tirar da lista skills de mesmo nome em níveis diferentes.
