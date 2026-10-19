#!/usr/bin/env python3
"""Vícios de texto de IA em entregas (.tex/.md): a parte do blader/humanizer que dá para checar
por regex, em português (e o básico em inglês, para README/PR). O resto é o checklist da skill
/escrita (.claude/skills/escrita/SKILL.md). Só para entrega e texto público, não para resumo.

  python3 tools/estilo.py <arquivo|pasta>...     sai 1 se houver erro

E01 contraste "não é X, é Y"    E02 expressão de IA    E03 travessão demais
E04 resíduo de chat (erro)      E05 abertura encenada / ditado
E06 verbo na 1ª pessoa do plural ("repetimos" → "repetindo... obtém-se")
"""
import pathlib
import re
import sys

I = re.I | re.M

E01 = [re.compile(p, I) for p in (
    r"\bnão (?:é|são|foi|era|se trata de)\s+(?:apenas|só|somente|meramente|simplesmente)?\b[^.;:!?\n]{1,60}?[,;—]\s*(?:mas|e sim|é|são)\b",
    r"\bnão (?:apenas|só|somente|meramente)\b[^.;!?\n]{1,80}?\bmas\b",
    r"\bnão significa\b[^.\n]{1,80}\.\s*(?:significa|quer dizer)\b",
    r"\b(?:it'?s|is) not (?:just |only |merely )?[^.;\n]{1,50}?[,;—]\s*(?:but|it'?s)\b",
    r"\bnot (?:just|only|merely)\b[^.;\n]{1,60}?\bbut\b",
)]

E02 = re.compile(r"\b(?:" + "|".join((
    r"vale (?:a pena )?(?:ressaltar|destacar|mencionar|notar|lembrar|salientar)",
    r"(?:é|torna-se) (?:importante|fundamental|crucial|essencial) (?:notar|ressaltar|destacar|mencionar|observar|salientar)",
    r"cabe (?:ressaltar|destacar|salientar|mencionar)",
    r"crucia(?:l|is)", r"desempenha(?:m)? (?:um )?papel", r"papel (?:fundamental|central|chave|essencial|importante)",
    r"em suma", r"no cenário atual", r"em constante evolução", r"mergulh(?:ar|amos|e|ando)", r"desvend\w+",
    r"alavanc\w+", r"potencializ\w+", r"sinergia\w*", r"notavelmente", r"meticulos\w+", r"intrincad\w+",
    r"testemunho", r"marco (?:importante|fundamental|significativo)", r"abre caminho para",
    r"de (?:forma|maneira|modo) (?:eficaz|significativa|abrangente|robusta|notável|ímpar)",
    r"por fim, mas não menos importante", r"sem sombra de dúvidas?", r"com (?:grande |total |pleno )?sucesso",
    r"(?:evidenciando|ressaltando|destacando|reforçando|sublinhando|demonstrando) (?:a|sua) (?:importância|relevância|eficácia)",
    r"delve\w*", r"tapestry", r"testament", r"underscor\w+", r"pivotal", r"crucial", r"leverag\w+", r"seamless\w*",
    r"showcas\w+", r"meticulous\w*", r"intricat\w+", r"in today'?s (?:landscape|world)",
)) + r")\b", I)

E04 = re.compile(r"(?:" + "|".join((
    r"\bespero que (?:isso|isto|este \w+|esta \w+) (?:ajude|seja útil)", r"\bfique à vontade\b", r"\bótima pergunta\b",
    r"^\s*(?:claro|certamente|com certeza)\s*[!,]", r"\bcomo (?:um modelo de linguagem|uma ia|uma inteligência artificial)\b",
    r"\b(?:até|segundo) (?:a )?minha última atualização\b", r"\bquer que eu\b", r"^\s*aqui está (?:o|a|um|uma)\b",
    r"\bI hope this helps\b", r"^\s*(?:certainly|of course|absolutely)!", r"\bgreat question\b",
    r"\bas an AI\b", r"\bmy (?:last|knowledge) (?:training )?(?:update|cutoff)\b", r"\blet me know if\b",
)) + r")", I)

E05 = re.compile(r"(?:" + "|".join((
    r"^\s*(?:agora )?vamos (?:explorar|mergulhar|entender|desvendar|analisar a fundo)\b", r"\bsem mais delongas\b",
    r"\ba (?:verdade|questão central|grande questão) é que\b", r"\bno fundo,", r"\bem (?:sua )?essência,",
    r"\bo (?:ponto|segredo) é que\b", r"\bmas afinal\b", r"\bisso (?:muda|diz) tudo\b",
    r"\blet'?s (?:dive|explore|break)\b", r"\bhere'?s the thing\b", r"\bat its core\b", r"\bthe real question is\b",
)) + r")", I)

# 1ª pessoa do plural: palavra sem acento em -amos/-emos/-imos ("últimos", "máximos" têm acento)
E06 = re.compile(r"\b[a-zç]+[aei]mos\b", I)
NAO_VERBO = {"mesmos", "termos", "extremos", "supremos", "ramos", "primos", "anos", "gamos", "remos", "racimos"}

TRAVESSAO = re.compile(r"—|(?<!-)---(?!-)")
PULAR = {"build", "originais", "obsidian", ".git", "node_modules"}


def _branco(m: re.Match) -> str:
    return "\n" * m.group(0).count("\n")


def prosa(txt: str, sufixo: str) -> str:
    """Só o texto corrido, com as mesmas quebras de linha (para o número da linha bater)."""
    if sufixo == ".tex":
        txt = re.sub(r"(?<!\\)%.*", "", txt)
        txt = re.sub(r"\\begin\{(equation|align|gather|multline|eqnarray|displaymath|lstlisting|verbatim|minted|"
                     r"tikzpicture|circuitikz)\*?\}.*?\\end\{\1\*?\}", _branco, txt, flags=re.S)
        txt = re.sub(r"\\\[.*?\\\]|\$\$.*?\$\$", _branco, txt, flags=re.S)
        txt = re.sub(r"(?<!\\)\$[^$]*\$", " x ", txt)
    else:
        txt = re.sub(r"\A---\n.*?\n---\n", _branco, txt, flags=re.S)
        txt = re.sub(r"^(```|~~~).*?^\1", _branco, txt, flags=re.S | re.M)
        txt = re.sub(r"<!--.*?-->", _branco, txt, flags=re.S)
        txt = re.sub(r"`[^`\n]*`", " x ", txt)
        txt = re.sub(r"\]\([^)]*\)", "]", txt)
        txt = re.sub(r"^\s*>.*$", "", txt, flags=re.M)          # citação: não se reescreve
    return txt


def checar(arq: pathlib.Path, nome: str | None = None) -> list[tuple[str, str, str, str]]:
    """(nível, código, arquivo:linha, mensagem)."""
    nome = nome or str(arq)
    txt = prosa(arq.read_text(encoding="utf-8", errors="replace"), arq.suffix)
    out = []
    for n, l in enumerate(txt.splitlines(), 1):
        onde = f"{nome}:{n}"
        for p in E01:
            if m := p.search(l):
                out.append(("aviso", "E01", onde, f"contraste '{m.group(0)[:50]}': diga o que é, sem a metade negada"))
        for m in E02.finditer(l):
            out.append(("aviso", "E02", onde, f"'{m.group(0)}': expressão típica de IA; troque pelo fato ou corte"))
        if m := E04.search(l):
            out.append(("erro", "E04", onde, f"resíduo de chat '{m.group(0).strip()}': corte"))
        if m := E05.search(l):
            out.append(("aviso", "E05", onde, f"'{m.group(0).strip()}': abertura encenada/ditado; vá direto ao ponto"))
        for m in E06.finditer(l):
            if m.group(0).lower() not in NAO_VERBO:
                out.append(("aviso", "E06", onde, f"'{m.group(0)}': 1ª pessoa do plural; use gerúndio ou impessoal "
                                                  "(repetindo... obtém-se, vê-se)"))
    palavras = len(txt.split())
    nt = len(TRAVESSAO.findall(txt))
    if nt >= 3 and nt * 1000 > 3 * palavras:
        out.append(("aviso", "E03", nome, f"{nt} travessões em {palavras} palavras: troque a maioria por vírgula, "
                                          "dois-pontos, parênteses ou ponto"))
    return out


def arquivos(alvos) -> list[pathlib.Path]:
    out = []
    for a in map(pathlib.Path, alvos):
        if a.is_dir():
            out += sorted(p for p in a.rglob("*") if p.suffix in (".tex", ".md") and not PULAR & set(p.parts))
        elif a.exists():
            out.append(a)
        else:
            raise SystemExit(f"não existe: {a}")
    return out


def checar_tudo(alvos, base: pathlib.Path | None = None) -> list[tuple[str, str, str, str]]:
    out = []
    for p in arquivos(alvos):
        out += checar(p, str(p.relative_to(base)) if base else None)
    return out


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    ds = checar_tudo(argv)
    for nivel, cod, onde, msg in ds:
        print(f"  {cod} {onde}  {msg}")
    ne = sum(n == "erro" for n, *_ in ds)
    print(f"estilo: {ne} erro(s), {len(ds) - ne} aviso(s) — o checklist que regex não pega está em /escrita")
    return 1 if ne else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
