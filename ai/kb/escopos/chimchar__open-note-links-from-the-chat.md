---
id: chimchar/open-note-links-from-the-chat
nome: Abrir links de nota nas respostas do chat (issue #149)
areas: [ui]
---
## Pedido
1. Um link `[palavra](note:<id>)` numa resposta do chat abre a nota no clique.
2. Link para nota que não existe vira texto com "(note not found)".

## Contexto
- O DOMPurify segue tirando os outros esquemas desconhecidos (`javascript:`).

## Fora
- Link dentro de célula de tabela e link para site no editor.
