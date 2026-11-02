---
id: lonzo/move-the-error-handlers-into-their-own-module
nome: Handlers de erro do lonzo num módulo próprio (issue #100)
areas: [servidor]
---
## Pedido (o que a branch entrega; cada item verificável)
1. Os `exception_handler` saem do `main.py` para `lonzo/handlers.py`, igual ao ichiro
   (#98): tabela erro → status (`APIError` 502, `MissingApiKey` 503, `FolderNotFound` 404,
   `NotAFolder` 422) com um handler só, mais o `notes_unavailable` (`httpx2.HTTPError`, 502,
   `detail` fixo); o `main.py` só chama `add_handlers`.
2. O status e o `detail` de cada erro não mudam (os testes antigos passam sem mexer).
3. Versão 0.2.0 → 0.3.0.

## Contexto (pode tocar só o mínimo para o Pedido funcionar)
- (2026-11-02, pedido do Lucca) Escrita pela sessão, revisão dele; empilhada sobre a
  `ichiro/split-ichiro-into-routers-and-services` (o W13 avisa até ela entrar na `master`).
- `str(error)` de um `APIError` é a mensagem dele (`anthropic/_exceptions.py:51`); a tabela
  procura com `isinstance`, para pegar as subclasses (`APIStatusError`...).

## Fora (vira outra branch)
- Mudar o status ou o texto de algum erro.
