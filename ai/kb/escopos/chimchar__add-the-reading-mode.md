---
id: chimchar/add-the-reading-mode
nome: Modo de leitura (issue #179)
areas: [editor, ui]
---
## Pedido (o que a branch entrega; cada item verificável)
- Um botão no pé da barra lateral, junto de configurações e logout, troca entre escrita e leitura com um clique.
- O ícone do botão muda de escrita para leitura.
- Em leitura, a nota não se edita (corpo e título) e o Markdown fica desenhado, sem marcas no cursor.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- `apps/chimchar/index.html`, `src/style.css`, `src/editor.ts`, `src/decorations/preview.ts`, `src/notes/page.ts`, `src/main.ts`.
- O modo vale para todas as notas e fica no `localStorage`, como o tema.

## Fora (vira outra branch)
- Agrupar abas.
- Imagens na nota.
- Modo por nota.
