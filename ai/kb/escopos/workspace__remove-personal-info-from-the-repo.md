---
id: workspace/remove-personal-info-from-the-repo
nome: Tirar o nome e os dados pessoais do dono do repo (issue #87)
areas: [workspace]
---
## Pedido (o que a branch entrega; cada item verificável)
1. Nenhum arquivo do repo (fora `node_modules`, `.venv`, `.git`, `dist`) com o nome, a faculdade, o caminho da home ou o usuário do GitHub do dono; `grep -rIi` não acha nada.
2. `ai/np lint` e `ai/np test` passam.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- "o Lucca" vira "o usuário" no `CLAUDE.md`, skills, ferramentas, escopos e notas; links de issue/milestone do GitHub viram texto.

## Fora
- Reescrever o histórico do git; remote e repo no GitHub.
