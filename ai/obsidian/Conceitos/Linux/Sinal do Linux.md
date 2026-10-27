---
tags: [noteproject, conceito, infra]
---
# Sinal do Linux

Um processo que está rodando precisa de um jeito de receber "pare" de fora: do Ctrl+C no terminal, do `kill`, do Docker ao parar um [[Container|container]]. O sinal é esse aviso do Linux, que o processo pode tratar ou não ([`man 7 signal`](https://man7.org/linux/man-pages/man7/signal.7.html)).

| Sinal | Quem manda | O processo pode tratar? |
|---|---|---|
| `SIGINT` | Ctrl+C | sim |
| `SIGTERM` | `kill <pid>`, `docker stop` | sim: fecha com calma |
| `SIGKILL` | `kill -9`, o Docker depois do prazo (10 s por padrão) | não: morre na hora |

- Tratar o sinal = rodar um código de saída antes de morrer: fechar conexões, terminar o que está em andamento.
- Servidor HTTP que trata o `SIGTERM` (o uvicorn do [[FastAPI]]) para de aceitar requests novas e espera as em andamento terminarem.
