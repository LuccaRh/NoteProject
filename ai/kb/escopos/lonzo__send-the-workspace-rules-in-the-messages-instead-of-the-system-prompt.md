---
id: lonzo/send-the-workspace-rules-in-the-messages-instead-of-the-system-prompt
nome: Regras dos workspaces em messages, fora do system (issue #198)
areas: [ia]
---
## Pedido (o que a branch entrega; cada item verificável)
1. O `system` de toda pergunta é só o `base_rules.md`, igual para toda pergunta e toda pessoa.
2. Data, pasta atual, regras dos workspaces e lista de skills vão numa mensagem `user` no começo de `messages`, antes do histórico, refeita a cada pergunta e não salva no banco.
3. O `base_rules.md` diz que esse bloco vem do app, não da pessoa, e que deve ser seguido.
4. lonzo 0.19.0.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- Em cima da `lonzo/take-the-summary-of-a-skill-from-a-description-in-its-header`.
- Skills globais, se existirem um dia, entram na mesma lista deste bloco.
- Duas mensagens `user` seguidas: a API junta num turno só (`anthropic/types/beta/message_create_params.py:60`).

## Fora (vira outra branch)
- Acrescentar regras no meio da conversa (#197).
- Marca de cache própria no bloco das regras.
