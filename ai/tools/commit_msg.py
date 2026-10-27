#!/usr/bin/env python3
"""Lint da mensagem de commit do NoteProject (regras em CLAUDE.md, "Tarefas, commits e branches").

Formato (checklist no vault, Plano do projeto/Regras de git):
- título em inglês, imperativo, com maiúscula, sem ponto final, ≤ 72 caracteres;
- sem prefixo (`feat:`, `fix:`, `docs:`...); a única marca aceita é a tag do que não é app:
  `[docs] ` (notas do vault) ou `[ai-workspace] ` (workspace de IA), antes do imperativo;
- nada de Claude/IA, sem Co-Authored-By nem "Generated with" (com tag, pode);
- commit do app (sem tag) só com título; corpo só nos commits com tag;
- nada de "wip", "fix", "update", "changes" sozinhos: diga o que mudou.
Merge, revert e fixup!/squash! gerados pelo git passam (o fixup some no rebase --autosquash).

    python3 tools/commit_msg.py <arquivo>   # hook commit-msg (tools/githooks/commit-msg)
    python3 tools/commit_msg.py -m "msg"

Sai com 1 e lista os erros se a mensagem quebrar alguma regra. Só barra a sessão do Claude Code
(`CLAUDECODE` no ambiente); commit do Lucca vira aviso com "commitar mesmo assim? [y/N]" no terminal.
"""
from __future__ import annotations

import argparse
import os
import pathlib
import re
import sys

PROIBIDO = re.compile(r"claude|anthropic|co-authored-by|generated with", re.I)
PREFIXO = re.compile(r"^[a-z]+(\([^)]*\))?!?: ")              # feat: , fix(web): , docs!:
GERADO = re.compile(r"^(Merge (branch|pull request|remote-tracking)|Revert \"|(fixup|squash|amend)! )")
VAGO = re.compile(r"^(wip|fix|fixes|update|updates|changes|adjustments|misc|stuff)\b\W*\d*$", re.I)
ACENTO = re.compile(r"[ãõáéíóúâêôàç]", re.I)                  # sinal de português
NAO_IMPERATIVO = re.compile(r"^\w+(ed|ing|s)\b")               # Added, Adding, Adds
TAG = re.compile(r"^\[([^\]]*)\] ?")                          # [docs] Add ...
TAGS = {"docs", "ai-workspace"}
VERBOS_OK = {"Address", "Process", "Pass", "Bypass", "Focus", "Discuss", "Express", "Access"}


def erros(texto: str) -> list[str]:
    linhas = [l for l in texto.splitlines() if not l.startswith("#")]
    while linhas and not linhas[0].strip():
        linhas.pop(0)
    if not linhas:
        return ["mensagem vazia"]
    titulo, e = linhas[0], []
    tag = TAG.match(titulo)
    com_tag = bool(tag) and tag.group(1) in TAGS  # commit com tag pode citar o Claude
    achou = sorted({m.group(0).lower() for m in PROIBIDO.finditer("\n".join(linhas))})
    if achou and not com_tag:
        e.append(f"menciona {achou} (nada de Claude/IA, sem Co-Authored-By)")
    if GERADO.match(titulo):
        return e
    if not com_tag and any(l.strip() for l in linhas[1:]):
        e.append("commit do app sem corpo: só o título (corpo só com [docs]/[ai-workspace])")
    if tag:
        if tag.group(1) not in TAGS:
            e.append(f"tag [{tag.group(1)}] desconhecida: só [docs] ou [ai-workspace]")
        elif not tag.group(0).endswith(" "):
            e.append(f"espaço depois de [{tag.group(1)}]")
        resto = titulo[tag.end():]
    else:
        resto = titulo
    if PREFIXO.match(resto):
        e.append("sem prefixo (feat:, fix:, docs:...): só o imperativo")
    if VAGO.match(resto.strip()):
        e.append(f"'{resto.strip()}' não diz o que mudou: nomeie o resultado")
    if len(titulo) > 72:
        e.append(f"título com {len(titulo)} caracteres (máx. 72)")
    if resto[:1] != resto[:1].upper():
        e.append("título começa com maiúscula")
    if titulo.rstrip().endswith("."):
        e.append("título sem ponto final")
    if ACENTO.search(titulo):
        e.append("título em inglês")
    pal = resto.split()[0] if resto.split() else ""
    if NAO_IMPERATIVO.match(pal) and pal not in VERBOS_OK:
        e.append(f"título no imperativo ('{pal}' → 'Add', não 'Added/Adds')")
    if len(linhas) > 1 and linhas[1].strip():
        e.append("linha em branco entre título e corpo")
    return e


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("arquivo", nargs="?")
    ap.add_argument("-m")
    a = ap.parse_args(argv)
    texto = a.m if a.m is not None else (
        pathlib.Path(a.arquivo).read_text(errors="replace") if a.arquivo else sys.stdin.read())
    if not (e := erros(texto)):
        return 0
    lista = "\n".join(f"  - {x}" for x in e)
    if os.environ.get("CLAUDECODE"):
        print(f"commit bloqueado (CLAUDE.md, 'Tarefas, commits e branches'):\n{lista}", file=sys.stderr)
        return 1
    print(f"aviso (CLAUDE.md, 'Tarefas, commits e branches'):\n{lista}", file=sys.stderr)
    return 0 if confirma("commitar mesmo assim? [y/N] ") else 1


def confirma(pergunta: str) -> bool:
    """Pergunta no terminal (o hook não tem stdin); sem terminal (IDE, script), deixa passar."""
    try:
        with open("/dev/tty", "r+") as tty:
            tty.write(pergunta)
            tty.flush()
            return tty.readline().strip().lower() in {"y", "yes"}
    except OSError:
        return True


if __name__ == "__main__":
    sys.exit(main())
