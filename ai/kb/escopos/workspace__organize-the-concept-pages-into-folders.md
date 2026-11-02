---
id: workspace/organize-the-concept-pages-into-folders
nome: Conceitos em pastas, um conceito por página, e páginas das issues feitas (issue #60)
areas: [workspace]
---
## Pedido (o que a branch entrega; cada item verificável)
1. `Conceitos/` em pastas por assunto, um conceito por página, mapa com uma seção por pasta.
2. Links do vault e do workspace (`areas.yaml`, skills, escopos) apontando para as páginas novas; `ai/np lint` passa.
3. `Issues feitas/` com uma página por issue, dentro da pasta da milestone.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- Regras de página (um conceito por página, página de issue) e o hook `commit-msg`, que só avisa no commit do usuário; vieram no mesmo `wip`.

## Fora (vira outra branch)
- Código do app (`apps/`).
