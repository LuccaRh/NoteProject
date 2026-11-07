---
id: chimchar/add-selectable-interface-themes
nome: Temas da interface à escolha (issue #172)
areas: [ui]
---
## Pedido (o que a branch entrega; cada item verificável)
- As configurações têm um seletor de tema; a troca vale na hora e fica neste navegador.
- Temas: `Minimal dark` (o de hoje, padrão) e `Retrofuturism` (design E, título grande).
- As fontes dos temas são carregadas pelo app.
- As cores soltas do `style.css` viram variáveis (sombras pretas ficam).
- O chat segue o tema; configurações e skills mantêm o layout e herdam as cores.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- `apps/chimchar/index.html`, `src/style.css`, `src/themes/`, `src/settings/`, `src/main.ts`.
- Designs no artifact `NoteProject UI`. Sem lib nova; fontes por link do Google Fonts.

## Fora (vira outra branch)
- Temas F (Grid 3D) e G (Liquid), cada um na sua branch.
- Lista com resumo, grade de pastas e outro HTML por tema (nível 3).
- Guardar o tema na conta (`lonzo`).
