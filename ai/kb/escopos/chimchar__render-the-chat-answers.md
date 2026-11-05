---
id: chimchar/render-the-chat-answers
nome: Renderizar as respostas do chat (issue #128)
areas: [ui]
---
## Pedido (o que a branch entrega; cada item verificável)
1. Ao mandar uma pergunta, a página desce sozinha e acompanha a resposta enquanto ela chega.
2. A resposta aparece renderizada: Markdown e fórmulas LaTeX, ao vivo e nas conversas salvas.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- `chat/chat.ts`, `chat/markdown.ts`, `style.css`. Libs novas, aprovadas: marked, dompurify
  e katex; as fórmulas são uma extensão do marked em `markdown.ts`,
  porque a marked-katex-extension deixava `$$` em várias linhas e `($Q$)` crus.
- A branch sai da `chimchar/cancel-a-chat-answer`, onde o rebase tirou o Esc.

## Fora (vira outra branch)
- Cor nos blocos de código da resposta.
- Abrir link da resposta em outra aba.
