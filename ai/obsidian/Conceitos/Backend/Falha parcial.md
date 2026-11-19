---
tags: [noteproject, conceito, servidor]
---
# Falha parcial

Uma função de servidor costuma fazer várias coisas em sequência: ler do banco, chamar outra API, gravar. Qualquer passo pode falhar no meio, depois de os anteriores já terem acontecido. **Falha parcial** é esse estado: parte feita, parte não. A ordem dos passos decide se o que sobra é inofensivo ou um dado quebrado.

Tudo *(geral)*, de memória.

## A pergunta de cada linha

Para cada passo: **"se falhar aqui, o que já aconteceu e fica valendo?"**

| Sobra depois da falha | Exemplo | Tudo bem? |
|---|---|---|
| Nada | a checagem falhou antes de qualquer escrita | sim |
| Algo que dá para repetir | a pasta foi criada, a nota não; repetir o pedido termina o serviço | sim, se repetir for seguro |
| Algo órfão e inofensivo | um arquivo salvo que nenhuma linha aponta | aceitável, limpa depois |
| Referência para o que não existe | a linha aponta para um arquivo que não foi salvo | não |
| Efeito que não volta | e-mail enviado, cobrança feita, e a gravação falhou | não |

## Regras de ordem

1. **Barato e local primeiro**: validar a entrada e checar regras antes de gastar rede ou banco. Se for falhar, que falhe cedo.
2. **Ler e checar antes de escrever**: erro na checagem não deixa nada pela metade.
3. **Chamada externa fora da [[Transação|transação]]**: uma chamada HTTP lenta dentro do `BEGIN` segura a conexão do pool e as travas das linhas. Chama antes, e depois abre a transação curta só com as escritas.
4. **Dentro de um banco, uma transação**: escritas no mesmo banco vão juntas no `COMMIT`; ali não existe falha parcial.
5. **Entre dois serviços, escolher quem vai primeiro**: dois bancos não dividem uma transação. Vai primeiro a escrita cuja sobra, se a segunda falhar, cai nas linhas "sim" da tabela.
6. **O que não volta vai por último**: depois de tudo gravado.

## Quando a ordem não basta

| Técnica | Ideia |
|---|---|
| Idempotência | repetir o mesmo pedido dá o mesmo resultado (chave do pedido, `INSERT ... ON CONFLICT`); com ela, "repetir" vira o conserto padrão |
| Compensação (saga) | cada passo tem um passo que desfaz; se o terceiro falha, roda o desfazer do segundo e do primeiro |
| Outbox | a gravação e o "avisar o outro serviço" entram na mesma transação, numa tabela; um processo à parte manda o aviso depois, até dar certo |
| Timeout | chamada externa sem limite pode prender o pedido para sempre; todo cliente HTTP leva um |

> [!example]
> O `save_settings` do `lonzo` chama a API da Anthropic antes de abrir a transação: [[Erros nos serviços#Ordem no `save_settings`]].

O que fazer com o erro de cada passo (lançar, tratar, deixar subir) fica em [[Tratamento de erros]].

Leitura: *Release It!* (Michael Nygard), falhas entre serviços; *Designing Data-Intensive Applications* (Martin Kleppmann), capítulos de transações e de sistemas distribuídos.
