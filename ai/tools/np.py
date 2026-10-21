#!/usr/bin/env python3
"""ai/np — CLI do workspace de IA do NoteProject (modelo: as CLIs ./<cod> do Disciplinas).

    ai/np status                    branch, escopo dela, mudanças, Estado do CLAUDE.md, marcas pendentes
    ai/np contexto <área> [-v]      o que ler para uma área (kb/areas.yaml): código, notas, libs, commits
    ai/np areas                     o vocabulário de áreas
    ai/np obsidian [-q] [--simular] sincronia vault Note Project/ ↔ obsidian/
    ai/np duvidas [trecho da pág]   marcas [!duvida] [duvidas] [fix] [coment] nas notas
    ai/np diagrama <spec.yaml> [--png]   YAML → draw.io; `destino:` no spec copia o .drawio.svg para obsidian/
    ai/np lint                      regras do workspace que viraram código (W01–W10)
    ai/np test                      testes das ferramentas (tools/test_*.py)
    ai/np check                     o check do app (make check: ruff, mypy, pytest, tsc, build)

Só stdlib + PyYAML.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent          # ai/
REPO = RAIZ.parent                                       # raiz do repo (apps/, CLAUDE.md, .claude/)
sys.path.insert(0, str(RAIZ / "tools"))
OBS = RAIZ / "obsidian"
AREAS = RAIZ / "kb" / "areas.yaml"
LIBS = RAIZ / "kb" / "libs"
ESCOPOS = RAIZ / "kb" / "escopos"
MARCAS = re.compile(r"> \[!duvida\]|\[duvidas\]|\[fix\]|\[coment\]", re.I)
AMARELO, VERDE, RESET = "\033[33m", "\033[32m", "\033[0m"


def marcas(texto: str) -> list[tuple[int, str]]:
    """Linhas com marca do Lucca, fora de bloco de código e de `crase` (lá é exemplo)."""
    out, cerca = [], False
    for i, l in enumerate(texto.splitlines(), 1):
        if l.lstrip().startswith("```"):
            cerca = not cerca
            continue
        if not cerca and MARCAS.search(re.sub(r"`[^`]*`", "", l)):
            out.append((i, l))
    return out


def areas() -> dict:
    return yaml.safe_load(AREAS.read_text(encoding="utf-8")) or {}


def git(*args: str) -> str:
    r = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True)
    return r.stdout.strip()


def n_linhas(p: Path) -> int:
    try:
        return sum(1 for _ in p.open("rb"))
    except OSError:
        return 0


def frontmatter(p: Path) -> dict:
    m = re.match(r"---\n(.*?)\n---", p.read_text(encoding="utf-8"), re.S)
    return (yaml.safe_load(m.group(1)) or {}) if m else {}


# --------------------------------------------------------------------------- #
def cmd_status(_a) -> int:
    br = git("rev-parse", "--abbrev-ref", "HEAD")
    print(f"branch: {br}")
    esc = ESCOPOS / f"{br.replace('/', '__')}.md"
    if esc.exists():
        corpo = esc.read_text(encoding="utf-8")
        pedido = re.search(r"## Pedido.*?\n(.*?)(\n## |\Z)", corpo, re.S)
        print(f"escopo: {esc.relative_to(REPO)}  áreas: {frontmatter(esc).get('areas')}")
        if pedido:
            print("  " + pedido.group(1).strip().replace("\n", "\n  "))
    elif br not in ("master", "main"):
        print(f"{AMARELO}escopo: falta {esc.relative_to(REPO)} (/foco){RESET}")
    st = git("status", "-s")
    print(f"mudanças: {len(st.splitlines())} arquivo(s)" + (f"\n  {st.replace(chr(10), chr(10) + '  ')}" if st else ""))
    claude = (REPO / "CLAUDE.md").read_text(encoding="utf-8")
    m = re.search(r"## Estado \((\d{4}-\d{2}-\d{2})\)", claude)
    print(f"Estado do CLAUDE.md: {m.group(1) if m else '?'}")
    n = sum(len(marcas(p.read_text(encoding="utf-8", errors="replace"))) for p in OBS.rglob("*.md"))
    print(f"marcas pendentes no Obsidian: {n}" + (" (ai/np duvidas)" if n else ""))
    return 0


def cmd_areas(_a) -> int:
    for k, v in areas().items():
        flags = " ".join(f for f in ("aprender", "futuro") if v.get(f))
        print(f"{k:12} {v.get('lado', ''):9} {v.get('nome', '')}" + (f"  [{flags}]" if flags else ""))
    return 0


def cmd_contexto(a) -> int:
    todas = areas()
    if not a.args or a.args[0] not in todas:
        print(f"área desconhecida. Existem: {', '.join(todas)}")
        return 1
    nome = a.args[0]
    ar = todas[nome]
    print(f"# {nome} — {ar.get('nome', '')} ({ar.get('lado', '')})")
    if ar.get("aprender"):
        print("aprender: true → explicar o conceito e deixar o Lucca escrever primeiro (CLAUDE.md)")
    if ar.get("futuro"):
        print("futuro: ainda sem código; ver as notas do vault")
    caminhos = []
    for c in ar.get("codigo") or []:
        p = REPO / c
        arquivos = sorted(f for f in p.rglob("*") if f.is_file() and "__pycache__" not in f.parts) if p.is_dir() else [p]
        for f in arquivos:
            caminhos.append(str(f.relative_to(REPO)))
            print(f"  código  {f.relative_to(REPO)}  ({n_linhas(f)} linhas)")
    for n in ar.get("notas") or []:
        print(f"  nota    ai/obsidian/{n}")
    for lib in ar.get("libs") or []:
        print(f"  lib     ai/kb/libs/{lib}.md")
    if caminhos:
        log = git("log", "--oneline", "-5", "--", *(ar.get("codigo") or []))
        if log:
            print("  commits recentes:\n    " + log.replace("\n", "\n    "))
    if a.v:
        print("\nOutras áreas que citam estes arquivos: " + ", ".join(
            k for k, v in todas.items() if k != nome and set(v.get("codigo") or []) & set(ar.get("codigo") or [])) or "-")
    return 0


def cmd_obsidian(a) -> int:
    import obsidian_sync
    argv = [x for x in ("-q" if a.q else None, "--simular" if a.simular else None) if x]
    return obsidian_sync.main(argv)


def cmd_duvidas(a) -> int:
    trecho = " ".join(a.args).lower()
    n = 0
    for p in sorted(OBS.rglob("*.md")):
        rel = str(p.relative_to(OBS))
        if trecho and trecho not in rel.lower():
            continue
        for i, l in marcas(p.read_text(encoding="utf-8", errors="replace")):
            n += 1
            print(f"ai/obsidian/{rel}:{i}: {l.strip()[:140]}")
    print(f"{n} marca(s)")
    return 0


def cmd_diagrama(a) -> int:
    import diagrama
    if not a.args:
        print("uso: ai/np diagrama ai/kb/diagramas/x.yaml [--png]")
        return 1
    spec = Path(a.args[0])
    spec = spec if spec.is_absolute() else Path.cwd() / spec
    argv = [str(spec)] + (["--png", str(RAIZ / "build" / "diagramas")] if a.png else [])
    r = diagrama.main(argv)
    destino = (yaml.safe_load(spec.read_text(encoding="utf-8")) or {}).get("destino")
    svg = spec.with_suffix(".drawio.svg")
    if r == 0 and destino and svg.exists():
        alvo = OBS / destino
        alvo.mkdir(parents=True, exist_ok=True)
        shutil.copy2(svg, alvo / svg.name)
        print(f"copiado para ai/obsidian/{destino}/{svg.name} (embed: ![[{svg.name}]])")
    return r


# --------------------------------------------------------------------------- #
def problemas() -> list[str]:
    out = []
    todas = areas()
    for k, v in todas.items():
        for c in v.get("codigo") or []:
            if not (REPO / c).exists():
                out.append(f"W01 área {k}: código {c} não existe")
        for n in v.get("notas") or []:
            if not (OBS / n).exists():
                out.append(f"W02 área {k}: nota ai/obsidian/{n} não existe")
        for lib in v.get("libs") or []:
            if not (LIBS / f"{lib}.md").exists():
                out.append(f"W03 área {k}: card ai/kb/libs/{lib}.md não existe")
        if v.get("futuro") and v.get("codigo"):
            out.append(f"W01 área {k}: futuro e com código; tire o futuro")
    for p in sorted(ESCOPOS.glob("*.md")):
        fm = frontmatter(p)
        if not fm.get("id") or not fm.get("nome"):
            out.append(f"W04 {p.relative_to(REPO)}: frontmatter sem id/nome")
        for ar in fm.get("areas") or []:
            if ar not in todas:
                out.append(f"W04 {p.relative_to(REPO)}: área {ar} fora de kb/areas.yaml")
    out += _versoes_libs()
    # W06: api.ts é a única fronteira de rede do front (README, "Decisões que valem lembrar")
    for f in sorted((REPO / "apps/web/src").rglob("*.ts")):
        if f.name != "api.ts" and re.search(r"\bfetch\(|new WebSocket\(|XMLHttpRequest", f.read_text(encoding="utf-8")):
            out.append(f"W06 {f.relative_to(REPO)}: rede fora de notes/api.ts")
    out += _docs()
    # W08: o NoteProject é à parte do trabalho; só a regra que proíbe pode citar o nome
    for f in sorted(OBS.rglob("*.md")):
        if f.name == "Regras de resposta.md":
            continue
        for i, linha in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if "pecazap" in linha.lower():
                out.append(f"W08 {f.relative_to(REPO)}:{i}: cita o Pecazap")
    out += _ingles()
    out += _quebras()
    return out


# Começo de bloco do markdown: a linha depois de uma destas não é continuação de parágrafo.
_BLOCO = re.compile(r"(#{1,6}\s|[-*+]\s|\d+[.)]\s|\||!\[\[|\[!|---|\*\*\*|<|\$\$|```|~~~|\[\^)")


def _quebras() -> list[str]:
    """W10: nota sem quebra de linha no meio do parágrafo; o Obsidian mostra cada quebra."""
    out = []
    for f in sorted(OBS.rglob("*.md")):
        cerca, ant = False, ""
        for i, linha in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            pre, txt = re.match(r"((?:>\s?)*)(.*)", linha).groups()  # type: ignore[union-attr]
            txt = txt.strip()
            if txt.startswith(("```", "~~~", "$$")):
                cerca = not cerca
            elif not cerca and ant and txt and not _BLOCO.match(txt) and pre.replace(" ", "") == ant[0]:
                out.append(f"W10 {f.relative_to(REPO)}:{i}: parágrafo quebrado no meio; junte com a linha de cima")
            ok = not cerca and len(linha) >= 60 and not linha.endswith(("  ", "\\"))
            ant = (pre.replace(" ", ""), txt) if ok and txt and not _BLOCO.match(txt) else ""
    return out


# Palavras e acentos que só aparecem em português; o `í` fica de fora porque o teste da busca
# sem acento precisa dele.
_PORTUGUES = re.compile(r"[ãõçâêôà]|\b(que|para|não|nao|uma|isso|então|entao|também|tambem|porque|"
                        r"quando|ainda|você|voce|aqui|depois|antes|sem|nota|notas|pasta|de|da|das|dos|ao|um|onde|"
                        r"senão|senao|algo|testes|ferramentas|arquivo|banco)\b", re.I)


def _ingles() -> list[str]:
    """W09: código do app, configs e README em inglês (comentário, mensagem, texto da interface)."""
    alvos = [p for p in (REPO / "apps").rglob("*")
             if p.suffix in {".py", ".ts", ".sql", ".css", ".html", ".toml"}
             and not {"node_modules", ".venv", "dist"} & set(p.parts)]
    alvos += [REPO / n for n in ("Makefile", "docker-compose-dev.yml", "README.md")]
    alvos += sorted((REPO / "apps").glob("*/Dockerfile*")) + sorted((REPO / ".github").rglob("*.yml"))
    out = []
    for f in alvos:
        if not f.is_file():
            continue
        for i, linha in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if f.suffix == ".md":  # nome de skill/comando entre crases não conta
                linha = re.sub(r"`[^`]*`", "", linha)
            if m := _PORTUGUES.search(linha):
                out.append(f"W09 {f.relative_to(REPO)}:{i}: português ('{m.group(0)}'); código em inglês")
    return out


def _versoes_libs() -> list[str]:
    """W05: card de lib com versão diferente da instalada (lockfiles) está velho."""
    out = []
    lock_js = REPO / "apps/web/package-lock.json"
    pk = json.loads(lock_js.read_text()).get("packages", {}) if lock_js.exists() else {}
    lock_py = REPO / "apps/server/uv.lock"
    uv = lock_py.read_text() if lock_py.exists() else ""
    for p in sorted(LIBS.glob("*.md")):
        fm = frontmatter(p)
        nome, versao = fm.get("pacote"), str(fm.get("versao", ""))
        if not nome:
            out.append(f"W05 {p.relative_to(REPO)}: frontmatter sem pacote/versao")
            continue
        inst = (pk.get(f"node_modules/{nome}") or {}).get("version")
        if inst is None:
            m = re.search(rf'name = "{re.escape(nome)}"\nversion = "([^"]+)"', uv)
            inst = m.group(1) if m else None
        if inst is None:
            out.append(f"W05 {p.relative_to(REPO)}: {nome} não está nos lockfiles")
        elif inst != versao:
            out.append(f"W05 {p.relative_to(REPO)}: card é da {versao}, instalada {inst}; reconfira o card")
    return out


def _docs() -> list[str]:
    """W07: skill, agente e ferramenta do workspace aparecem no README e no 'Como usar'."""
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    como = OBS / "Workspace de IA" / "Como usar.md"
    pagina = como.read_text(encoding="utf-8") if como.exists() else ""
    pecas = [f"/{d.parent.name}" for d in sorted((REPO / ".claude/skills").glob("*/SKILL.md"))]
    pecas += [a.stem for a in sorted((REPO / ".claude/agents").glob("*.md"))]
    pecas += [f.name for f in sorted((RAIZ / "tools").glob("*.py")) if not f.name.startswith("test_")]
    out = []
    for x in pecas:
        faltam = [n for n, t in (("README.md", readme), ("Como usar", pagina)) if x not in t]
        if faltam:
            out.append(f"W07 {x} não documentado em {', '.join(faltam)}")
    return out


def cmd_lint(_a) -> int:
    p = problemas()
    for x in p:
        print(f"{AMARELO}{x}{RESET}")
    print(f"{VERDE}lint ok{RESET}" if not p else f"{len(p)} problema(s)")
    return 1 if p else 0


def cmd_test(_a) -> int:
    r = subprocess.run([sys.executable, "-m", "unittest", "-q", "test_commit_msg", "test_foco",
                        "test_hooks_contexto", "test_estilo"], cwd=RAIZ / "tools")
    r2 = subprocess.run([sys.executable, "test_obsidian_sync.py"], cwd=RAIZ / "tools")
    r3 = subprocess.run([sys.executable, "test_diagrama.py"], cwd=RAIZ / "tools")
    return r.returncode or r2.returncode or r3.returncode


def cmd_check(_a) -> int:
    return subprocess.run(["make", "check"], cwd=REPO).returncode


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["status", "contexto", "areas", "obsidian", "duvidas", "diagrama",
                                    "lint", "test", "check"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("-q", action="store_true")
    ap.add_argument("-v", action="store_true")
    ap.add_argument("--simular", action="store_true")
    ap.add_argument("--png", action="store_true")
    a = ap.parse_args(argv)
    return globals()[f"cmd_{a.cmd}"](a)


if __name__ == "__main__":
    sys.exit(main())
