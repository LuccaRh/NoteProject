---
id: workspace/show-every-theme-in-gifs-in-the-readme
nome: Mostrar todos os temas em GIFs no README (issue #214)
areas: [workspace]
---
## Pedido (o que a branch entrega; cada item verificável)
1. No `README.md`, as seções dos 7 temas mostram nota, chat e Skills em GIF, com as mesmas cenas do topo (#212).
2. As notas do vault mexidas com os PRs #199–#205 (`load_skill`, regras de cima, bloco `<context>`) entram na branch.
3. `ai/np test` passa e `ai/np lint` não acusa nada novo.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- GIFs em `docs/images/themes/`, no lugar dos PNGs, gravadas com dados de exemplo simulados no navegador, sem conta real.
- Liquid em 6 quadros/s e 800px: o globo muda todo quadro e a GIF passava de 13 MB.

## Fora
- Mudanças de app.
