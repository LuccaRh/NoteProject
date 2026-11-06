---
id: chimchar/add-the-liquid-theme
nome: Tema Liquid (issue #174)
areas: [ui]
---
## Pedido (o que a branch entrega; cada item verificável)
- O seletor das configurações ganha o tema `Liquid` (design G): noite azul, estrelas, título itálico grande, botões redondos.
- Globo de pontos em `<canvas>` atrás da nota, só neste tema, parado com `prefers-reduced-motion`.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- `apps/chimchar/index.html`, `src/style.css`, `src/themes/`, `src/settings/theme.ts`, `src/main.ts`.

## Fora (vira outra branch)
- "Synced on 2 devices" (ainda não há sync).
- Desenhar o globo num Web Worker, se o custo pesar em máquina real.
