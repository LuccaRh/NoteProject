---
tags: [noteproject, workspace, regras]
---
# Regras de página

Valem para toda página que o workspace escreve ou corrige no Obsidian (`/nota`, `/aprender`, `/duvida`, `/destrinchar`). O estilo de texto vem das [[Regras de resposta]]; aqui fica o que é **de página**. Correção do Lucca que vale para outras páginas entra aqui, com data.

> [!info] Onde este arquivo mora
> As skills leem `.claude/skills/nota/regras.md`, que é um link para esta página (cópia em `obsidian/Workspace de IA/` do repo).

## Conteúdo
- **Fonte**: estado atual sai do código; plano e porquê, destas notas; fato externo que muda decisão (preço, licença, lib descontinuada) vem com data e link. Sem fonte → *(geral)*.
- (2026-10-15) **O vault é a única fonte do projeto.** Nada de citar o PDF de arquitetura (era só o esboço inicial), o workspace das matérias nem outro projeto. Fora daqui, só fonte de pesquisa oficial (doc, site do fornecedor), com link.
- **Uma ideia por página**, título que nomeia o tópico, para várias páginas citarem a mesma.
- **Escadinha**: a página começa por de onde vem (que problema resolve) e para que serve.
- **Página grande vira pasta** com `00 Mapa — <pasta>` (tabela Página | Ideia) e uma página por parte.
- (2026-10-15) **Conceito tem uma página só**, em `Conceitos/` (mapa `00 Mapa — Conceitos`): o que é, de onde vem, para que serve, escrito sem se amarrar a uma página. Página de plano, decisão ou IA usa o conceito e linka, nunca reexplica. Conceito que o texto precisa e não tem página → criar a página antes.
- (2026-10-16) **Conceito explica como funciona; o projeto tem página própria.** Em `Conceitos/` não entra o que o NoteProject faz com o conceito: nada de "No projeto", ✅/⏳, arquivo:linha, issue nem etapa. No máximo um `> [!example]` de 1–2 linhas mostrando um uso, com link para a página do projeto. Como está implementado (ou planejado) vai numa página do projeto, em `Estrutura do projeto/` (ou `IA no projeto/`), que linka o conceito.
- **Decisão = opções + critério + escolha + o que faria mudar de ideia.** Tabela das opções lado a lado; a escolha com o porquê; "revisar se..." no fim.
- (2026-10-17) **Página de decisão descreve o que será feito**, sem `Decidido (data)` no título nem como funciona hoje. A alternativa descartada entra breve: um parágrafo, a tabela lado a lado e o porquê da escolha.
- **Estado vs plano**: diga o que já existe no código (✅) e o que é plano (⏳). Página de plano não descreve como pronto o que não está.

## Desenhos
- Fluxo, camadas, sequência e deploy viram **desenho draw.io** (`/diagrama`), em `Figuras/` da pasta, embutido com `![[nome.drawio.svg]]` e legenda de uma linha. Mermaid só para o pequeno.
- Cores fixas entre desenhos: azul front, verde back, laranja servidor, amarelo dados, roxo infra, vermelho segurança, cinza grupo.

## Links
- **Grafo, não árvore**: linke a página de qualquer conceito que aparece no texto, de qualquer pasta do vault (`Programing/`, `Docker/`, `Git/`), menos as notas do trabalho: o projeto é à parte (2026-10-15, [[Regras de resposta]]). Antes de escrever, `grep` nos títulos.
- (2026-10-15) **Todo conceito com página é linkado onde aparece**, no texto e nas tabelas, não só na primeira vez. Título, código e título de callout ficam sem link.
- (2026-10-19) **Parágrafo numa linha só**, sem quebrar a linha no meio da frase: o Obsidian mostra cada quebra (lint W10).
- **Link passivo**: o texto usa uma palavra que é nome de página → `[[Página|palavra]]`. Nada de frase criada para linkar (`(ver [[X]])`, `Vem de [[X]]:`).
- Sem cabeçalho de "onde é usado"; página nova é citada por pelo menos uma além do mapa.

## Dúvidas e marcas do usuário
- `> [!duvida]`, `[duvidas]` (dúvida), `[fix]` (correção), `[coment]` (opinião/decisão dele).
- Dúvida não vira callout: o texto é reescrito até responder; a pergunta vai para `## Dúvidas` no fim (lista numerada, redação dele, sem resposta; número novo no fim).
- `[fix]` → aplica e apaga. `[coment]` → o texto passa a refletir a decisão dele; se há motivo técnico contra, responde no chat e a marca fica até ele decidir.

## Texto
- Página não fala do usuário (nada de "você", nome, "seu ok"): texto impessoal.
- Vícios de texto de IA: "não é X, é Y"; abertura encenada; primeira frase que repete o título; fecho que repete o parágrafo; tríade por ritmo; "está relacionado a" sem dizer como; gerúndio pendurado; "atua como"; negrito decorativo; resultado vazio ("funciona bem").

## Formato
- Frontmatter `tags: [noteproject, <área>]` (áreas de `kb/areas.yaml`).
- Callouts: `[!info]`, `[!example]`, `[!warning]` (erros comuns), `[!note]- Resposta` (dobrada).
- Dentro de tabela, `\|` no alias do link.
