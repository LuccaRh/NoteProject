---
id: chimchar/add-the-glass-theme
nome: Tema Glass (issue #176)
areas: [ui]
---
## Pedido (o que a branch entrega; cada item verificável)
- O seletor das configurações ganha o tema `Glass`: design B, painéis translúcidos sobre manchas de cor, botões redondos com brilho, azulejo escuro ao lado do título.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- `apps/chimchar/index.html`, `src/style.css`, `src/themes/`, `src/main.ts`.

## Fora (vira outra branch)
- Pastas em cartões e lista de recentes do design B (mudam a árvore); pílula "Synced" (ainda não há sync).
- `backdrop-filter`: o fundo já é desfocado, então o blur não mudaria nada e só custaria.
