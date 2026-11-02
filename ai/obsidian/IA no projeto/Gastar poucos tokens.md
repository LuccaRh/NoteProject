---
tags: [noteproject, ia, tokens]
---
# Gastar poucos tokens

A página "Contexto e tokens" do workspace mostra que toda chamada reenvia tudo o que está no contexto, e que muito do gasto vem de a IA explorar (ler arquivos, buscar) antes de responder.

Esta página junta as decisões das outras que cortam esse gasto.

## As regras

| Regra | Como | Página |
|---|---|---|
| o [[O daemon notesd\|daemon]] monta o contexto | pergunta + seção + card; a IA não busca nada | [[Fila de pedidos]] |
| seção, não nota | o pacote para no próximo heading | [[MCP — a IA como cliente do daemon]] |
| o tema já é sabido | card certo por `fields.conteudo`, sem busca | [[Classificar a nota pelo tema]] |
| a saída é uma operação | a IA escreve só o trecho novo (saída é o token mais caro) | [[Edição por âncora]] |
| molde, não instrução de estilo | lista de moldes no lugar das páginas de regra | [[Blocos padronizados]] |
| receita, não imagem | YAML ou script curto | [[Figuras geradas]] |
| lote | várias dúvidas numa chamada, com o começo em [[Cache de prompt\|cache]] | [[Fila de pedidos]] |
| modelo por tarefa | classificar → modelo pequeno; responder → médio; o grande só se pedir | [[Sem Claude Code — provedores]] |
| uma chamada na fila | sem loop de ferramentas; o pedido já vem completo | [[Fila de pedidos]] |
| poucas ferramentas [[MCP]] | 4, com descrição curta | [[MCP — a IA como cliente do daemon]] |

## No chat

O [[Chat com o workspace|chat]] é o oposto da fila: a IA busca o próprio contexto pelo [[Laço de ferramentas|laço de ferramentas]], e cada volta é uma chamada nova com o pacote inteiro.

- O pacote cresce a cada volta: uma pergunta que lê 5 notas faz 6 chamadas, e a última leva as 5 notas.
- O que segura o gasto: `system` e `tools` fixos no começo do pacote, para o [[Cache de prompt|cache]] pegar; ferramentas que devolvem a seção, não a nota inteira; um limite de voltas por pergunta.
- A [[Busca full-text no Postgres|busca de notas]] devolve só `id` e `title` de cada nota achada: o gasto vem do que volta para a IA, não de como o banco acha; a IA abre só a nota que escolher.
- O ganho é a pergunta livre, sem pedido montado antes; o preço é gastar mais por pergunta que a fila.

## Ordem do pacote, para o cache

O [[Cache de prompt|cache]] reaproveita o começo da chamada enquanto ele for igual. Então, do mais fixo ao mais variável:

1. regras e moldes (iguais sempre);
2. card do tema (igual dentro do lote);
3. seção e pergunta (mudam a cada pedido).

## Medir, não supor

Cada pedido grava no [[O daemon notesd|daemon]] os tokens de entrada, de saída e lidos do [[Cache de prompt|cache]], como o `tools/tokens.py` faz com as sessões. Assim dá para ver se uma mudança economizou mesmo.
