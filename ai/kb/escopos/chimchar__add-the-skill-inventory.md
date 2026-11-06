---
id: chimchar/add-the-skill-inventory
nome: Inventário de skills, lado do chimchar (issue #161)
areas: [ui, cliente-api]
---
## Pedido (o que a branch entrega; cada item verificável)
1. Uma aba Skills, aberta por um botão da barra lateral, uma só por vez.
2. A aba lista os workspaces e, para o escolhido, as skills com título e resumo.
3. Clicar numa skill abre a nota; dá para remover, copiar para outro workspace e publicar.
4. A seção "Add" lista as skills publicadas (dos outros ou minhas), sem as que o workspace já tem, com o corpo visível antes de adicionar.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- `skills/api.ts` é do usuário (área `cliente-api`); `skills/skills-tab.ts` importa dele.
- Remover usa o `deleteNote` e os workspaces saem do `listTree`, ambos de `notes/api.ts`.
- Texto de skill vem de outras pessoas: só `textContent`, nada de `innerHTML`.

## Fora (vira outra branch)
- Despublicar, comando `/`, aviso de que a cópia difere da publicada.
