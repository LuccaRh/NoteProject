---
tags: [noteproject, ia]
---
# Classificar a nota pelo tema

Para responder uma dúvida, a [[Fila de pedidos]] precisa saber **qual card** mandar junto. No workspace, o card é achado pelo nome do tema em `kb/temas.yaml`: vocabulário fechado, sem busca semântica.

Classificar é guardar o tema em cada nota. Assim o [[O daemon notesd|daemon]] e as [[Pastas, campos e views|views]] sabem do que ela fala sem ler o texto.

## O que é

- Toda nota tem [[Pastas, campos e views|`fields`]] (JSON) no schema (#7): `aula`, `conteudo[]` e `tipo`.
- Classificar = preencher `fields.conteudo` escolhendo **da lista fechada** da matéria.
- Exemplo: uma nota em `2S2026/ES728/` que fala de "polinômio característico... p(A) = 0" ganha `conteudo: [cayley_hamilton]`.

O card pode ser uma nota do próprio app (`tipo: card`) ou continuar em `kb/` do workspace.

## Quem preenche, do mais barato ao mais caro

| Passo | Preenche | Custo |
|---|---|---|
| 1. a pasta | `materia`, `semestre` (a [[Pastas, campos e views\|pasta injeta]]) | zero |
| 2. uma regra | heading igual ao nome de um tema da lista | zero |
| 3. um modelo pequeno | escolhe da lista lendo o título e os primeiros parágrafos | uma chamada curta |
| 4. você | corrige no painel de campos | — |

- A IA só roda se os passos 1 e 2 não resolverem. Ela só escolhe da lista: a resposta é um nome, não texto livre.
- Roda em segundo plano, depois de salvar, nunca durante a captura (nenhuma decisão de organização na captura).

## Para que mais serve

- Views por parâmetro: "todas as notas de estabilidade", "dúvidas pendentes de autovalores".
- A resposta a uma dúvida carrega um card só, o certo, em vez de a IA procurar ([[Gastar poucos tokens]]).
