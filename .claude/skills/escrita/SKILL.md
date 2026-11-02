---
name: escrita
description: Tira a cara de texto de IA de texto público do NoteProject (README, descrição de PR, issue, apresentação do projeto) — lint ai/tools/estilo.py + checklist do blader/humanizer. Não usar em notas do Obsidian, ai/kb/ nem chat. Use quando o usuário disser "/escrita", "tira a cara de IA", "deixa mais natural", ou ao escrever README/PR.
argument-hint: <arquivo|pasta>
---
# /escrita <arquivo|pasta>

Herdada do Disciplinas. Base: [blader/humanizer](https://github.com/blader/humanizer) (MIT),
commit `225a6f3`, inteiro em `blader.md`. **Não leia o `blader.md`**; para o exemplo de um padrão:
`grep -A14 "^### N\." blader.md`.

- **Vale para** README, PR, issue, apresentação. **Não vale para** notas, `ai/kb/`, chat, commits.
- Só tira vício: não dá "voz", não põe opinião, não inventa fato, número ou fonte.

## Passos
1. `python3 ai/tools/estilo.py <arquivo|pasta>`: E01 "não é X, é Y", E02 expressão de IA, E03
   travessão demais, E04 resíduo de chat, E05 abertura encenada. Corrija, ou deixe se é de propósito.
2. Uma leitura com o checklist. Edite só o trecho; mantenha todo fato, número e código.
3. Lint de novo. Ao usuário, ≤ 5 linhas: o que mudou e por quê.

## Checklist (§ do blader)
- §2 Fecho que repete o parágrafo → corte. §3 Ditado ("no fundo") → a afirmação concreta.
- §5 Rebate objeção que ninguém fez → corte. §6 Tríade por ritmo → só os que dizem algo.
- §7 Mesmo conectivo em todo parágrafo → junte. §9 Ressalva sobre ressalva → uma.
- §13 Importância inflada ("abre caminho para") → o fato. §14 "Está relacionado a" → diga como.
- §15 Gerúndio pendurado → corte. §18 "atua como" → "é". §19–20 Negrito decorativo → texto simples.
- §24 Primeira frase repete o título → corte. §25 Texto falando de si → só se o leitor não deduz.
- Resultado vazio ("funciona bem") → o número ou o teste que mostra.
