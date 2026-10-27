---
tags: [noteproject, conceito, infra]
---
# CI

Todo commit pode quebrar algo, e rodar os testes à mão antes de cada merge é fácil de esquecer.

- **CI** (integração contínua): a cada push, um robô roda testes e build. O commit que quebra fica vermelho antes do merge.
- **GitHub Actions**: o robô do GitHub; cada workflow é um YAML em `.github/workflows/`.
- Depois do merge, pôr no ar sozinho é o [[CD]].

> [!example] No NoteProject
> O CI roda, a cada push, os mesmos checks do `make check` (um job por serviço) ([[Infra — deploy e operação]]).

Doc: [GitHub Actions](https://docs.github.com/en/actions).
