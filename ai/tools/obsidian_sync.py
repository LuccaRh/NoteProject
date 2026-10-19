#!/usr/bin/env python3
"""Sincronia bidirecional vault do Obsidian (Note Project/) ↔ pasta obsidian/ do repo.

Herdada do workspace Disciplinas (mesma lib, só o repo oficial e a trava mudam).

Mapa em obsidian.yaml (raiz): pasta do vault -> pasta no repo. A chave "" é a raiz do
vault configurado (aqui, a pasta Note Project inteira).

Estado da última sincronia em <repo>/.sync.json (caminho -> sha1). Para cada arquivo:
  mudou só de um lado   -> copia para o outro (inclusive criação e remoção)
  mudou dos dois lados  -> conflito: não mexe, avisa (resolva à mão e rode de novo)
Proteções (é backup): pasta do vault sumiu -> não apaga nada no repo, só avisa (use
--restaurar); remoção em massa (> metade e > 5 arquivos) -> não faz, avisa.

    python3 tools/obsidian_sync.py [-q] [--simular] [--restaurar] [--notificar] [pasta ...]
Roda pelos hooks SessionStart/Stop (.claude/settings.json) e por `./np obsidian`.
"""
from __future__ import annotations

import argparse
import contextlib
import fcntl
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys

import yaml

RAIZ = pathlib.Path(__file__).resolve().parent.parent
MAPA = RAIZ / "obsidian.yaml"
EXTS = {".md", ".canvas", ".excalidraw", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".pdf"}
AMARELO, RESET = "\033[33m", "\033[0m"
# só a cópia oficial do repo sincroniza com o vault real: um clone de teste (onde os hooks de
# sessão também rodam) escreveria no vault (aconteceu em 2026-10-12)
OFICIAL = pathlib.Path(os.environ.get("NOTEPROJECT_REPO", "~/Documents/NoteProject")).expanduser().resolve()


class Abortado(Exception):
    pass


def carregar_mapa() -> tuple[pathlib.Path, dict[str, pathlib.Path]]:
    m = yaml.safe_load(MAPA.read_text(encoding="utf-8"))
    vault = pathlib.Path(os.path.expanduser(m["vault"]))
    return vault, {k or "": RAIZ / v for k, v in m["pastas"].items()}


def _hashes(raiz: pathlib.Path, excluir: set[str] = frozenset()) -> dict[str, str]:
    if not raiz.exists():
        return {}
    out = {}
    for p in sorted(raiz.rglob("*")):
        partes = p.relative_to(raiz).parts
        if (p.is_file() and p.suffix.lower() in EXTS and not any(x.startswith(".") for x in partes)
                and partes[0] not in excluir):
            out[str(p.relative_to(raiz))] = hashlib.sha1(p.read_bytes()).hexdigest()
    return out


def _remover(rel: str, raiz: pathlib.Path):
    p = raiz / rel
    p.unlink()
    d = p.parent
    while d != raiz and not any(d.iterdir()):
        d.rmdir()
        d = d.parent


@contextlib.contextmanager
def trava():
    """Hooks de duas sessões podem rodar juntos: um de cada vez."""
    caminho = pathlib.Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp")) / "noteproject_obsidian_sync.lock"
    with open(caminho, "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        yield


def sincronizar(vault: pathlib.Path, repo: pathlib.Path, simular: bool = False,
                estado: pathlib.Path | None = None, excluir: set[str] = frozenset()
                ) -> tuple[list[str], list[str]]:
    """Devolve (ações, conflitos). Levanta Abortado se o vault sumiu ou se apagaria demais."""
    estado = estado or repo / ".sync.json"
    real = pathlib.Path(os.path.expanduser(yaml.safe_load(MAPA.read_text(encoding="utf-8"))["vault"])).resolve()
    if vault.resolve().is_relative_to(real) and not repo.resolve().is_relative_to(OFICIAL):
        raise Abortado(f"{repo} não é a cópia oficial ({OFICIAL}): não mexo no vault real")
    if not vault.exists():
        if repo.exists() and _hashes(repo, excluir):
            raise Abortado(f"{vault} não existe; nada apagado no repo (para recriar: --restaurar)")
        return [], []
    base = json.loads(estado.read_text()) if estado.exists() else {}
    v, r = _hashes(vault, excluir), _hashes(repo, excluir)
    plano, conflitos, novo = [], [], {}
    for rel in sorted(set(base) | set(v) | set(r)):
        b, hv, hr = base.get(rel), v.get(rel), r.get(rel)
        if hv == hr:                       # iguais (ou ausentes dos dois lados)
            if hv:
                novo[rel] = hv
            continue
        mv, mr = hv != b, hr != b          # mudou desde a última sincronia?
        if mv and mr:
            conflitos.append(rel)
            if b:
                novo[rel] = b
            continue
        plano.append((rel, mv, hv if mv else hr))
        if hv if mv else hr:
            novo[rel] = hv if mv else hr
    for lado_vault in (True, False):
        n = sum(1 for _, mv, h in plano if h is None and mv == lado_vault)
        if n > 5 and n > len(base) / 2:
            de = "vault" if lado_vault else "repo"
            raise Abortado(f"{n} de {len(base)} arquivos sumiram do {de} ({vault.name}); não repliquei "
                           f"a remoção. Se foi de propósito, apague também do outro lado")
    acoes = []
    for rel, mv, h in plano:
        origem, destino = (vault, repo) if mv else (repo, vault)
        lado = "vault → repo" if mv else "repo → vault"
        acoes.append(f"{'remove ' if h is None else 'copia  '} {rel}  ({lado})")
        if simular:
            continue
        if h is None:
            _remover(rel, destino)
        else:
            (destino / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(origem / rel, destino / rel)
    if not simular:
        repo.mkdir(parents=True, exist_ok=True)
        estado.write_text(json.dumps(novo, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
    return acoes, conflitos


def restaurar(vault: pathlib.Path, repo: pathlib.Path, excluir: set[str] = frozenset()) -> list[str]:
    """Copia repo -> vault o que falta no vault (nunca sobrescreve). Para quando o vault se perdeu."""
    feitos = []
    for rel in _hashes(repo, excluir):
        if not (vault / rel).exists():
            (vault / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(repo / rel, vault / rel)
            feitos.append(rel)
    return feitos


def sincronizar_pasta(pasta: str, simular: bool = False) -> tuple[list[str], list[str]]:
    """Uma entrada do obsidian.yaml (o que ./np obsidian chama)."""
    vault, mapa = carregar_mapa()
    excluir = set(mapa) - {""} if pasta == "" else set()
    with trava():
        return sincronizar(vault / pasta if pasta else vault, mapa[pasta], simular, excluir=excluir)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pastas", nargs="*", help="pastas do vault (padrão: todas do obsidian.yaml)")
    ap.add_argument("-q", action="store_true", help="só fala se fez algo ou deu problema")
    ap.add_argument("--simular", action="store_true")
    ap.add_argument("--restaurar", action="store_true", help="repo -> vault do que falta no vault")
    ap.add_argument("--notificar", action="store_true", help="notify-send se houver conflito (timer)")
    a = ap.parse_args(argv)
    vault, mapa = carregar_mapa()
    if not vault.exists() and not a.restaurar:
        print(f"{AMARELO}vault não encontrado: {vault} (nada feito; --restaurar recria){RESET}")
        return 1
    erro, avisos = 0, []
    with trava():
        for pasta in a.pastas or mapa:
            excluir = set(mapa) - {""} if pasta == "" else set()
            pv, nome = (vault / pasta if pasta else vault), pasta or "(resto do vault)"
            if a.restaurar:
                for rel in restaurar(pv, mapa[pasta], excluir):
                    print(f"  restaura {nome}/{rel}")
                continue
            try:
                acoes, conflitos = sincronizar(pv, mapa[pasta], a.simular, excluir=excluir)
            except Abortado as e:
                print(f"{AMARELO}  {nome}: {e}{RESET}")
                avisos.append(f"{nome}: {e}")
                erro = 1
                continue
            for x in acoes:
                print(f"  {nome}: {x}")
            for c in conflitos:
                print(f"{AMARELO}  {nome}: CONFLITO {c}: mudou no vault e no repo; junte à mão e rode de novo{RESET}")
            erro |= bool(conflitos)
            avisos += [f"{nome}: {c}" for c in conflitos]
    if avisos and a.notificar and shutil.which("notify-send"):
        subprocess.run(["notify-send", "Obsidian ↔ NoteProject: resolver à mão", "\n".join(avisos)])
    if not a.q:
        print("ok" + (" (simulação)" if a.simular else ""))
    return erro


if __name__ == "__main__":
    sys.exit(main())
