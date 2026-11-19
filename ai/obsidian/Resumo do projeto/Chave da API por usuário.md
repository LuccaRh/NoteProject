---
tags: [noteproject, ia, auth]
---
# Chave da API por usuário

O chat chama a API da Anthropic, que cobra por token. Para o app não pagar a IA de todo mundo, cada pessoa cola a própria chave nas configurações; o serviço não tem chave própria.

## Como fica guardada

- Tabela `settings` do banco `lonzo`, uma linha por usuário, com [[Row-Level Security|RLS]] ([[Isolamento por usuário]]).
- `api_key bytea` = a chave cifrada com Fernet (`cryptography`): AES-128-CBC + HMAC-SHA256, com timestamp. A chave de cifra é `LONZO_SECRET_KEY`, do ambiente, fora do banco e do git.
- `key_end`: os últimos caracteres, para a tela mostrar "termina em ...xyz" sem decifrar.
- Banco vazado sem o `LONZO_SECRET_KEY` não revela as chaves. Cifra **reversível** (e não hash) porque o serviço precisa da chave original para chamar a API.

## Como é usada

- Um `AsyncAnthropic()` global sem chave (conexões reaproveitadas); cada chamada faz `sdk.with_options(api_key=...)` com a chave do usuário.
- Ao salvar, `models.list()` com a chave: `AuthenticationError` → `InvalidApiKey` (422), e a lista de modelos que a chave pode usar volta para a tela.
- Cada modelo traz `capabilities` (tipos de thinking aceitos) e `max_tokens`; a tela só oferece o que o modelo aceita, em vez de uma tabela fixa no código.
- Também por usuário: modelo, `max_tokens`, `tools_max_turns`, thinking, mostrar `.workspace`.

## Se perguntarem

- **"E a rotação do `LONZO_SECRET_KEY`?"** Ainda não existe; o caminho é `MultiFernet` (decifra com a velha, cifra com a nova) e um script que recifra as linhas.
- **"Por que não um cofre (KMS, Secrets Manager)?"** Na AWS, o `LONZO_SECRET_KEY` vai para um deles; cifrar no app continua igual.
