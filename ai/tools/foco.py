#!/usr/bin/env python3
"""Hook UserPromptSubmit: avisa quando o pedido sai do que a branch atual se propôs a fazer.

Herdado do workspace Disciplinas. Lá a tarefa era a atividade; aqui é a **branch**
(regra do CLAUDE.md: branch = uma funcionalidade). Cada branch tem `kb/escopos/<branch>.md`
(skill /foco) com frontmatter id (= nome da branch), nome, areas e o corpo Pedido / Contexto / Fora.

A cada prompt:
  1. acha a branch atual (git); na master/main não faz nada;
  2. com escopo: um juiz separado (`claude -p`, Haiku, sem ferramentas, sem CLAUDE.md, sem
     hooks) lê só o escopo, a mensagem e o fim da última resposta, e classifica
     pedido / contexto / fora; pedido → nada (zero token na sessão);
  3. sem escopo: uma linha pedindo para a sessão criar o escopo (uma vez por sessão).
Qualquer erro ou demora → segue sem aviso (o hook nunca trava o prompt).

  python3 tools/foco.py                       (hook; lê o JSON do stdin)
  python3 tools/foco.py --listar              escopos e qual é o da branch atual
  python3 tools/foco.py --julgar <id> "msg"   roda só o juiz (para testar o prompt)
"""
import json, os, re, subprocess, sys, tempfile
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
ESCOPOS = "kb/escopos"
ESTADO = RAIZ / "build" / "foco"
PRINCIPAIS = {"master", "main", "HEAD", ""}
MODELO, TIMEOUT = "haiku", 25
ENV_JUIZ = "FOCO_JUIZ"           # o juiz é um claude -p: não pode disparar o hook de novo

JUIZ = """Você verifica se um desenvolvedor está se desviando do que a branch atual se propôs a fazer.
Recebe o ESCOPO da branch (Pedido = o que a funcionalidade entrega; Contexto = pode tocar só o
mínimo para o Pedido funcionar; Fora = desvios já conhecidos, que viram outra branch), a MENSAGEM
e o fim da última resposta do assistente (só para entender a que a mensagem se refere).

Classifique a MENSAGEM:
- "pedido": serve diretamente a um item do Pedido. Inclui dúvida de conceito necessária para o
  item, testes, tipos, lint, build, commits e revisão da própria branch.
- "contexto": é sobre um item de Contexto e quer mais do que o mínimo (refatorar, generalizar).
- "fora": é sobre algo listado em Fora, ou é outra funcionalidade que não ajuda o Pedido.
- "pedido" também para mensagens que não são sobre o código da branch (git, ferramentas,
  workspace, notas do Obsidian, estudo de um conceito): não é com você.
- "pedido" também quando a mensagem pergunta se algo é do escopo, ou pede para tirar algo de
  Contexto/Fora: isso é voltar ao foco.
Na dúvida, "pedido". Só avise o que tomaria tempo de verdade.

Responda só um JSON numa linha, sem markdown:
{"classe": "pedido|contexto|fora", "motivo": "<até 25 palavras, em português: por que, e qual item do Pedido está mais perto>"}"""


def branch_atual(raiz=None):
    try:
        r = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=raiz or RAIZ,
                           capture_output=True, text=True, timeout=5)
        return r.stdout.strip()
    except (subprocess.SubprocessError, OSError):
        return ""


def arquivo_escopo(branch, raiz=None):
    return (raiz or RAIZ) / ESCOPOS / f"{branch.replace('/', '__')}.md"


def ler_escopo(p):
    txt = p.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n?(.*)", txt, re.S)
    if not m:
        return None
    meta = yaml.safe_load(m.group(1)) or {}
    if not meta.get("id"):
        return None
    return {**meta, "corpo": m.group(2).strip(), "arquivo": p}


def escopos(raiz=None):
    return [e for e in (ler_escopo(p) for p in sorted(((raiz or RAIZ) / ESCOPOS).glob("*.md"))) if e]


def ultima_resposta(transcript, n=600):
    """Fim do último texto do assistente no log da sessão (para o juiz entender 'e isso?')."""
    try:
        linhas = Path(transcript).read_text(errors="replace").splitlines()[-300:]
    except (OSError, TypeError):
        return ""
    for linha in reversed(linhas):
        try:
            d = json.loads(linha)
        except ValueError:
            continue
        if d.get("type") != "assistant" or d.get("isSidechain"):
            continue
        conteudo = (d.get("message") or {}).get("content") or []
        texto = " ".join(c.get("text", "") for c in conteudo if isinstance(c, dict) and c.get("type") == "text")
        if texto.strip():
            return texto.strip()[-n:]
    return ""


def julgar(e, prompt, anterior=""):
    """Chama o juiz; devolve (classe, motivo) ou None se falhar."""
    entrada = (f"ESCOPO de {e['nome']}:\n{e['corpo']}\n\n"
               f"FIM DA ÚLTIMA RESPOSTA DO ASSISTENTE:\n{anterior or '(nenhuma)'}\n\n"
               f"MENSAGEM:\n{prompt[:2000]}")
    cmd = ["claude", "-p", "--model", MODELO, "--tools", "", "--setting-sources", "",
           "--disable-slash-commands", "--no-session-persistence", "--system-prompt", JUIZ]
    try:
        r = subprocess.run(cmd, input=entrada, capture_output=True, text=True, timeout=TIMEOUT,
                           cwd=tempfile.gettempdir(), env={**os.environ, ENV_JUIZ: "1"})
        m = re.search(r"\{.*\}", r.stdout, re.S)
        d = json.loads(m.group(0)) if m else {}
    except (subprocess.SubprocessError, OSError, ValueError):
        return None
    classe = str(d.get("classe", "")).lower()
    return (classe, str(d.get("motivo", "")).strip()) if classe in ("pedido", "contexto", "fora") else None


def contexto(ev, raiz=None, estado=ESTADO, juiz=julgar, branch=None):
    raiz = raiz or RAIZ
    prompt = ev.get("prompt", "")
    if not prompt.strip() or prompt.lstrip().startswith("/"):
        return None                          # comando/skill: não é pergunta sobre a branch
    branch = branch_atual(raiz) if branch is None else branch
    if branch in PRINCIPAIS:
        return None
    arq = arquivo_escopo(branch, raiz)
    e = ler_escopo(arq) if arq.exists() else None
    if not e:
        marca = estado / f"{ev.get('session_id', 'x')}.sem-escopo"
        if marca.exists() and branch in marca.read_text().split("\n"):
            return None
        estado.mkdir(parents=True, exist_ok=True)
        with open(marca, "a") as f:
            f.write(branch + "\n")
        return {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext":
                f"[foco] A branch {branch} não tem {arq.relative_to(raiz.parent)}. Antes de seguir, crie-o pela "
                "skill /foco (parte A) e mostre o Pedido em 3–6 linhas para o Lucca aprovar."}}
    veredito = juiz(e, prompt, ultima_resposta(ev.get("transcript_path")))
    if not veredito or veredito[0] == "pedido":
        return None
    classe, motivo = veredito
    aviso = f"⚠ Foco ({e['id']}, {classe}): {motivo}"
    return {"systemMessage": aviso,
            "hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext":
                f"[foco] O verificador julgou esta mensagem '{classe}' para a branch {e['nome']}: {motivo} "
                f"Comece a resposta com a linha '{aviso}', responda curto e pergunte se quer seguir nisso "
                f"(ou abrir outra branch); nada disso entra na branch sem o ok dele. "
                f"Escopo: {e['arquivo'].relative_to(raiz.parent)}."}}


def main():
    if "--listar" in sys.argv:
        atual = branch_atual()
        for x in escopos():
            print(f"{'*' if x['id'] == atual else ' '} {x['id']:40} {x['nome']}")
        print(f"branch atual: {atual or '?'}")
        return
    if "--julgar" in sys.argv:
        i = sys.argv.index("--julgar")
        e = next(x for x in escopos() if x["id"] == sys.argv[i + 1])
        print(julgar(e, sys.argv[i + 2]))
        return
    if os.environ.get(ENV_JUIZ):
        return
    try:
        out = contexto(json.load(sys.stdin))
    except Exception:
        return
    if out:
        print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
