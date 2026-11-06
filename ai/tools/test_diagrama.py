"""Testes da lib comum de diagramas. python3 tools/test_diagrama.py"""
from __future__ import annotations

import pathlib
import sys
import traceback
import xml.etree.ElementTree as ET

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import diagrama as dg  # noqa: E402

RAIZ = pathlib.Path(__file__).resolve().parent.parent
TESTES = []


def teste(fn):
    TESTES.append(fn)
    return fn


def _specs():
    """Todo spec de diagrama do repo: kb/diagramas/*.yaml."""
    return sorted(RAIZ.glob("kb/diagramas/*.yaml"))


MINI = {
    "titulo": "mini", "tipo": "blocos", "grade": [160, 100],
    "nos": {"r": {"tipo": "entrada", "pos": [0, 0], "texto": "r"},
            "s": {"tipo": "somador", "pos": [1, 0]},
            "g": {"tipo": "bloco", "pos": [2, 0], "texto": "$$\\frac{1}{s+1}$$"},
            "y": {"tipo": "saida", "pos": [3.2, 0], "texto": "y"}},
    "arestas": [["r", "s", {"sinal": "+"}], ["s", "g"], ["g", "y"],
                ["g.d", "s.b", {"por": "baixo", "sinal": "-"}]],
}


@teste
def test_xml_valido():
    d = dg.montar(MINI)
    raiz = ET.fromstring(dg.drawio(d))
    ids = {c.get("id") for c in raiz.iter("mxCell")}
    assert {"r", "s", "g", "y", "e0", "e3"} <= ids, ids
    assert raiz.find(".//mxGraphModel").get("math") == "1", "FT com $$ liga o MathJax"


@teste
def test_tabela_liga_na_linha_da_coluna():
    spec = {"nos": {
        "a": {"tipo": "tabela", "pos": [0, 0], "texto": "a", "cor": "verde",
              "colunas": [["id", "uuid", "PK"], ["b_id", "uuid", "FK"]]},
        "b": {"tipo": "tabela", "pos": [3, 0], "texto": "b", "cor": "azul",
              "colunas": [["id", "uuid", "PK"]]},
    }, "arestas": [["a.d:b_id", "b.e:id", {"pontas": ["ERmany", "ERmandOne"]}]]}
    d = dg.montar(spec)
    x, y, w, _ = d.nos["a"].ret()
    assert d.nos["a"].porta("d:b_id") == (x + w, y + 28 + 30, "d")
    assert "ERmany" in dg.drawio(d)
    ET.fromstring(dg.drawio(d))


@teste
def test_realimentacao_em_u():
    d = dg.montar(MINI)
    pts = d.arestas[3].pontos
    assert all(a[0] == b[0] or a[1] == b[1] for a, b in zip(pts, pts[1:])), f"não ortogonal: {pts}"
    assert max(y for _, y in pts) > d.nos["g"].cy, "não desceu"
    assert pts[-1] == (d.nos["s"].cx, d.nos["s"].cy + 15), "não entrou por baixo do somador"


@teste
def test_mini_sem_colisao():
    assert not dg.colisoes(dg.montar(MINI)), dg.colisoes(dg.montar(MINI))


@teste
def test_pega_linha_sobre_no():
    spec = {**MINI, "nos": {**MINI["nos"], "x": {"tipo": "bloco", "pos": [1.5, 0], "texto": "x"}}}
    probs = dg.colisoes(dg.montar(spec))
    assert any("passa sobre x" in p for p in probs), probs


@teste
def test_pega_fios_sobrepostos_no_mesmo_no():
    """Dois fios para terminais diferentes do mesmo amp-op não podem correr juntos
    (escapou na 1ª versão: bastava chegar ao mesmo nó para ser perdoado)."""
    spec = {"tipo": "circuito", "grade": [100, 70], "nos": {
        "a": {"tipo": "entrada", "pos": [0, 0], "texto": "a"},
        "b": {"tipo": "entrada", "pos": [0, 1], "texto": "b"},
        "amp": {"tipo": "ampop", "pos": [1.5, 0.5]}},
        "arestas": [["a", "amp.+"], ["b", "amp.-"]]}
    probs = dg.colisoes(dg.montar(spec))
    assert any("sobrepostas" in p for p in probs), probs


@teste
def test_pega_grupo_invadido():
    spec = {**MINI, "nos": {**MINI["nos"], "grp": {"tipo": "grupo", "contem": ["r", "g"]}}}
    probs = dg.colisoes(dg.montar(spec))
    assert any("invade o grupo grp" in p for p in probs), probs


@teste
def test_terminal_girado():
    n = dg.No("r", "resistor", 100, 100, 80, 20, rot=90)
    assert n.porta("1")[:2] == (100, 60) and n.porta("2")[:2] == (100, 140), (n.porta("1"), n.porta("2"))


@teste
def test_specs_das_materias_sem_colisao():
    specs = _specs()
    assert specs, "nenhum spec encontrado"
    import yaml
    for p in specs:
        probs = dg.colisoes(dg.montar(yaml.safe_load(p.read_text(encoding="utf-8"))))
        assert not probs, f"{p.relative_to(RAIZ)}: {probs[:3]}"


def test_aresta_com_cor_e_coluna():
    spec = {"nos": {
        "a": {"tipo": "tabela", "pos": [0, 0], "texto": "a", "cor": "verde",
              "colunas": [["id", "uuid", "PK"]]},
        "b": {"tipo": "tabela", "pos": [0, 20], "texto": "b", "cor": "azul",
              "colunas": [["id", "uuid", "PK"]]},
    }, "grade": [100, 10], "arestas": [["a.d:id", "b.d:id", {"cor": "roxo", "coluna": 4}]]}
    d = dg.montar(spec)
    assert d.arestas[0].cor == "roxo"
    assert d.arestas[0].pontos[1][0] == dg.MARGEM + 400


def main() -> int:
    falhas = 0
    for fn in TESTES:
        try:
            fn()
            print(f"  ok    {fn.__name__.removeprefix('test_')}")
        except Exception:                                   # noqa: BLE001
            falhas += 1
            print(f"  FALHA {fn.__name__.removeprefix('test_')}\n{traceback.format_exc()}")
    print(f"{len(TESTES) - falhas}/{len(TESTES)} ok")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
