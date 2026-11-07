---
pacote: "@codemirror/view"
versao: 6.43.6
fonte: apps/chimchar/node_modules/@codemirror/view/dist/index.d.ts
areas: [editor]
---
# @codemirror/view — decorações

Card destilado dos tipos instalados (fonte acima, linhas citadas). Versão mudou → `./np lint`
avisa; reconfira as linhas antes de confiar no card.

## Os quatro tipos (`Decoration`, d.ts:331–346)

| Função | Faz | Uso no projeto |
|---|---|---|
| `Decoration.line({class})` | classe na linha inteira | headings (`decorations/headings.ts`) |
| `Decoration.mark({class})` | estilo num trecho | negrito, código inline |
| `Decoration.replace({widget?})` | esconde um trecho, opcionalmente põe um widget | chips `[!duvida]` (`decorations/replace.ts`) |
| `Decoration.widget({widget, side})` | insere DOM num ponto | botão, ícone |

- `Decoration.set(ranges, sort?)` (d.ts:352): sem `sort = true`, os ranges têm de vir em ordem
  de `from`. `RangeSetBuilder.add` exige a mesma ordem (state d.ts, "sorted order").
- `Decoration.none` (d.ts:356): conjunto vazio.

## Widget (`WidgetType`, d.ts:205)

- `toDOM(view)` é obrigatório; `eq(widget)` evita redesenhar o mesmo widget a cada tecla.
- `ignoreEvent(event)` (d.ts:247): `false` deixa o editor tratar o clique (mover cursor).

## De onde as decorações vêm

- `ViewPlugin.fromClass(cls, {decorations: v => v.decorations})` (d.ts:519): recalcula em
  `update(u)` quando `u.docChanged || u.viewportChanged`; só as `view.visibleRanges`.
- **Limite** (d.ts:1310–1314): decoração dada por função (que é o caso do ViewPlugin) **não pode**
  ter block widget nem `replace` que cubra quebra de linha. Para isso, `StateField` que fornece
  o `DecorationSet` direto.
- Cursor pular o chip inteiro: dar o mesmo range set a `EditorView.atomicRanges` (d.ts:1352).
- `MatchDecorator({regexp /g, decoration | decorate})` (d.ts:1822): regex por linha;
  `createDeco(view)` no construtor e `updateDeco(update, deco)` no `update` (d.ts:1874–1880).
  Serve para `[!duvida]` sem escrever o laço de linhas à mão.
- `lineNumbers(config?)` (`index.d.ts:2395`) e `highlightActiveLineGutter()` (`:2401`): números na margem. O `formatNumber` recebe o `state`, mas a margem só redesenha quando o documento ou a config mudam, então número relativo ao cursor não sai só com ele.
