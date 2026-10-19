#!/usr/bin/env python3
"""Hooks do Claude Code que seguram o tamanho do contexto (custo em tokens: README, "Uso de tokens").

  aviso-clear  (Stop)        ao fim de cada resposta, se o contexto passou de um limiar
                             (100k, 200k, 300k), avisa uma vez por limiar: /clear ou /compact.
  leitura      (PreToolUse)  barra Read sem offset/limit e `cat` de arquivo grande: pede o
                             trecho (grep -n + offset/limit ou sed -n a,bp) ou o agente leitor.

Lê o JSON do hook no stdin; responde em JSON no stdout (nada = segue normal).
"""
import json, re, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ESTADO = RAIZ / "build" / "contexto"
LIMIARES = (100_000, 200_000, 300_000)
LEITURA_US_POR_M = 0.20          # releitura de cache, Opus 5.5 (US$/M)
MAX_LINHAS_READ = 400
MAX_LINHAS_CAT = 300
BINARIO = {".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ipynb"}


def contexto_atual(transcript):
    """Tokens enviados na última chamada da API registrada no log da sessão."""
    ultimo = 0
    try:
        linhas = Path(transcript).read_text(errors="replace").splitlines()
    except OSError:
        return 0
    for linha in reversed(linhas[-400:]):
        try:
            d = json.loads(linha)
        except ValueError:
            continue
        u = (d.get("message") or {}).get("usage") if d.get("type") == "assistant" else None
        if u and not d.get("isSidechain"):
            ultimo = sum(u.get(c, 0) for c in
                         ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
            break
    return ultimo


def aviso_clear(ev, estado=ESTADO):
    ctx = contexto_atual(ev.get("transcript_path", ""))
    passou = [l for l in LIMIARES if ctx >= l]
    if not passou:
        return None
    arq = estado / re.sub(r"[^\w-]", "_", ev.get("session_id", "sessao"))
    try:
        ja = int(arq.read_text())
    except (OSError, ValueError):
        ja = 0
    if passou[-1] <= ja:
        return None
    estado.mkdir(parents=True, exist_ok=True)
    arq.write_text(str(passou[-1]))
    custo = ctx * LEITURA_US_POR_M / 1e6
    return {"systemMessage":
            f"Contexto em {ctx // 1000}k tokens: cada chamada relê tudo (~US$ {custo:.2f} por chamada, "
            f"várias por resposta). Próximo pedido é outra tarefa → /clear. "
            f"Mesma tarefa e ainda longa → /compact."}


def negar(motivo):
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                   "permissionDecision": "deny",
                                   "permissionDecisionReason": motivo}}


def n_linhas(p):
    try:
        with open(p, "rb") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


def leitura(ev):
    nome, ent = ev.get("tool_name"), ev.get("tool_input") or {}
    cwd = Path(ev.get("cwd") or ".")
    if nome == "Read":
        p = cwd / ent.get("file_path", "")
        if ent.get("offset") or ent.get("limit") or p.suffix.lower() in BINARIO:
            return None
        n = n_linhas(p)
        if n > MAX_LINHAS_READ:
            return negar(f"{p.name} tem {n} linhas. Leia só o trecho: `grep -n` para achar onde e "
                         f"Read com offset/limit; para varrer o arquivo atrás de uma resposta, use o "
                         f"agente leitor. Precisa mesmo do arquivo todo? Leia em partes com offset/limit.")
    if nome == "Bash":
        cmd = ent.get("command", "")
        m = re.fullmatch(r"\s*(?:cd\s+(\S+|\"[^\"]+\")\s*(?:&&|;)\s*)?cat\s+(?:-n\s+)?(\S+|\"[^\"]+\")\s*", cmd)
        if m:
            base = cwd / m.group(1).strip('"') if m.group(1) else cwd
            p = Path(m.group(2).strip('"'))
            p = p if p.is_absolute() else base / p
            n = n_linhas(p)
            if n > MAX_LINHAS_CAT:
                return negar(f"{p.name} tem {n} linhas. Em vez de cat inteiro: `grep -n` para achar e "
                             f"`sed -n 'a,bp'` para ler o trecho, ou o agente leitor.")
    return None


def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        ev = json.load(sys.stdin)
    except ValueError:
        return
    r = {"aviso-clear": aviso_clear, "leitura": leitura}.get(modo, lambda _: None)(ev)
    if r:
        print(json.dumps(r, ensure_ascii=False))


if __name__ == "__main__":
    main()
