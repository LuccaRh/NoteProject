---
tags: [noteproject, conceito, servidor]
---
# Tratamento de erros

Em Python, uma função que não consegue terminar o que promete lança uma exceção com `raise`. A exceção sobe pela pilha de chamadas até alguém pegar com `try/except`; se ninguém pegar, o programa (ou o pedido, num servidor) termina com erro. Tratar erros é decidir **em que andar** cada exceção é lançada e pega.

Tudo *(geral)*, de memória.

## Três escolhas

| Escolha | Quando | Exemplo |
|---|---|---|
| `raise` | a função não consegue cumprir o contrato: entrada inválida, item que não existe, regra violada | `raise FolderNotFound(...)` quando a pasta pedida não existe |
| `try/except` | o andar **faz algo** com o erro | ver a tabela abaixo |
| Deixar subir | o andar não tem o que fazer com o erro | bug, banco fora do ar: vira 500 e log |

O que justifica um `except`:

| Ação | Ideia |
|---|---|
| Traduzir | troca o erro de baixo por um que o andar de cima entende: `IntegrityError` → `TitleTaken`, `TitleTaken` → status 409. Com `raise Novo(...) from error`, o erro original fica no traceback |
| Repetir ou ter plano B | timeout numa API externa: tenta de novo, ou usa um valor padrão |
| Limpar e relançar | fechar conexão, desfazer transação, e mandar o erro adiante com `raise` sozinho; o [[Context manager\|`with`]] e o `finally` fazem isso sem `except` |

## Erro esperado e bug

- **Esperado**: faz parte do uso normal (título repetido, chave recusada, pasta apagada). Ganha uma classe própria, com nome do domínio, e uma resposta clara.
- **Bug**: o código está errado (`KeyError`, `AttributeError`). Não se trata: deixar subir faz o erro aparecer no log com a linha certa.

## Erros comuns

> [!warning]
> - `except Exception:` no meio do código: pega bug junto com erro esperado, e o bug some.
> - `except` que só faz `pass` ou `print`: o chamador acha que deu certo.
> - Pegar cedo demais: o andar de baixo não sabe que resposta dar; quem sabe é o de cima.
> - Traduzir sem `from error`: o traceback perde onde o erro nasceu.

## Exemplo completo

```python
class TitleTaken(Exception):
    pass


def save(titles: set[str], title: str) -> None:
    if title in titles:                       # erro esperado: lança
        raise TitleTaken(f"{title} already exists")

    titles.add(title)


def handle(titles: set[str], title: str) -> int:
    try:
        save(titles, title)
    except TitleTaken:                        # traduz para status
        return 409

    return 201


titles: set[str] = set()
print(handle(titles, "a"), handle(titles, "a"))   # 201 409
```

> [!example]
> Nos serviços do projeto, cada andar (client, service, handler) faz uma tradução: [[Erros nos serviços]].

A ordem dos passos que podem falhar fica em [[Falha parcial]].

Docs: [Python — Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html).
