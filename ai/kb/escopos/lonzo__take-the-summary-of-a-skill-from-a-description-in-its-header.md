---
id: lonzo/take-the-summary-of-a-skill-from-a-description-in-its-header
nome: Resumo da skill vindo do description do cabeçalho (issue #195)
areas: [ia]
---
## Pedido (o que a branch entrega; cada item verificável)
1. `split_skill` tira o resumo do `description` do cabeçalho `---` e devolve o corpo sem o
   cabeçalho; nota sem cabeçalho continua usando a primeira linha.
2. A cópia de uma skill publicada (`published_text`) nasce com o cabeçalho `name` + `description`.
3. `create_workspace.md` e `base_rules.md` mandam toda skill nova abrir com o cabeçalho.
4. (a confirmar) `create_note` e `edit_note` recusam nota de `.workspace/skills/` sem
   `description`; o erro volta ao modelo, que corrige.
5. As 5 notas de skill do banco local ganham o cabeçalho (dado, fora do git).
6. Testes e lonzo 0.18.0.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- Em cima da `lonzo/read-the-skills-of-every-workspace-above-the-conversation` (#192).
- Sem lib nova: `description` numa linha só, lida linha a linha (`pyyaml` não é dependência).
- O título da nota continua sendo o nome que vale na lista; `name` só acompanha o formato.

## Fora (vira outra branch)
- Esconder o cabeçalho no editor (hoje aparece como texto).
- `description` em várias linhas (YAML `>` ou `|`).
- Barrar nota sem cabeçalho salva pelo editor: continua com o fallback da primeira linha.
