---
id: lonzo/add-the-skill-inventory
nome: Inventário de skills, lado do lonzo (issue #161)
areas: [ia]
---
## Pedido (o que a branch entrega; cada item verificável)
1. Tabela `skills` no banco `lonzo`, só com as públicas: `id`, `user_id`, `note_id`, `title`, `summary`, `body`, `UNIQUE (user_id, note_id)`. Todo usuário logado lê; só o dono escreve.
2. `GET /chat/skills`: as publicadas pelos outros; `?owner=me`: as da pessoa.
3. `GET /chat/workspaces/{folder_id}/skills`: as notas de `.workspace/skills/`, com título e resumo.
4. `POST /chat/workspaces/{folder_id}/skills` com `skill_id` ou `note_id`: copia a skill para uma nota do workspace.
5. `POST /chat/skills` com `note_id`: publica a nota ou atualiza a linha que veio dela.
6. A lista de skills do chat usa a primeira linha com texto, e o resumo vem no formato "Faz X. Use quando Y".

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- Desenho combinado na sessão de 2026-11-05/06: skill privada = nota; pública = linha, foto do momento em que foi publicada. Adicionar sempre copia; não há ligação entre as cópias.
- `note_id` não é FK: notas ficam no banco `ichiro`.
- A branch sai da `master`, porque a pilha anterior foi mergeada.

## Fora (vira outra branch)
- A aba: `chimchar/add-the-skill-inventory`.
- Despublicar, comando `/`, ferramenta `use_skill`, contagem de usos, aviso de versão, moderação.
