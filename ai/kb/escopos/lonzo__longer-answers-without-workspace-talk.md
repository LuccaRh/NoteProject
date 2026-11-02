---
id: lonzo/longer-answers-without-workspace-talk
nome: Resposta do chat sem corte e sem falar do workspace (issue #76, PR do lonzo)
areas: [ia]
---
## Pedido (o que a branch entrega; cada item verificável)
1. `CHAT_MAX_TOKENS` de 512 para 64000: uma resposta do chat não é cortada no meio
   (o pedido é em stream, então o valor alto não esbarra no timeout do SDK).
2. `create_workspace.md` manda o `CLAUDE.md` gerado proibir o modelo de citar
   `CLAUDE.md`, `.workspace/`, subpastas, regras ou skills, salvo se a pessoa perguntar;
   o aviso "o que mudou" sai em palavras comuns, sem nome de arquivo.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- PR do lonzo da #76: a `chimchar/chat-with-the-ai-from-the-web-app` fica empilhada
  sobre esta até o merge (os dois serviços rodam do diretório de trabalho).
- O item 2 só vale para workspace criado depois; o `CLAUDE.md` de um já existente se
  edita à mão.

## Fora (vira outra branch)
- Mudança no front (`chimchar/chat-with-the-ai-from-the-web-app`).
- `max_tokens` do laço de ferramentas (`TOOLS_MAX_TOKENS`, sem stream).
