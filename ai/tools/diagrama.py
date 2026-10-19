#!/usr/bin/env python3
"""spec.yaml -> desenho em draw.io (.drawio, + .drawio.svg e .png se o draw.io desktop existir).

Herdado do workspace Disciplinas; aqui com o nó `banco` (cilindro) para arquitetura.
O YAML é a fonte da verdade; o .drawio é a VISTA para ler e
ajustar. Editar o .drawio não volta para o YAML: mudou o desenho, muda o YAML e gera de novo
(mesma regra do GRAFCET do es925, de onde vieram as primitivas e a checagem de colisão).

Dois tipos de desenho:
  blocos    diagrama de blocos / funções de transferência (setas, somadores, grupos)
  circuito  esboço de circuito (símbolos mxgraph.electrical, fios sem seta)

Layout em GRADE: cada nó diz `pos: [col, lin]` (pode ser fracionário) e a lib calcula as
coordenadas; as arestas são ortogonais e a rota sai daqui, não do draw.io. Nada de linha
sobre linha, linha sobre texto nem cruzamento: `colisoes()` confere e o comando falha.

    python3 tools/diagrama.py <spec.yaml> [-o pasta] [--png]

Formato do YAML: ver a skill `/diagrama` (.claude/skills/diagrama/SKILL.md).
"""
from __future__ import annotations

import argparse
import html
import pathlib
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field

import yaml

G = 10                  # todo ponto cai nesta grade de px
CHAR = 7.0              # largura média de um caractere (fonte 12), em px
SAIDA = 20              # trecho reto ao sair/entrar de uma porta antes de dobrar
MARGEM = 40

CORES = {   # (preenchimento, contorno): claros, para figura em tema claro
    "azul": ("#dae8fc", "#6c8ebf"), "verde": ("#d5e8d4", "#82b366"),
    "laranja": ("#ffe6cc", "#d79b00"), "vermelho": ("#f8cecc", "#b85450"),
    "roxo": ("#e1d5e7", "#9673a6"), "amarelo": ("#fff2cc", "#d6b656"),
    "cinza": ("#f5f5f5", "#666666"),
}

# --------------------------------------------------------------------------- #
# símbolos: tipo -> (estilo draw.io, w, h, terminais em fração da caixa NÃO girada)
# --------------------------------------------------------------------------- #
_EL = ("pointerEvents=1;verticalLabelPosition=bottom;verticalAlign=top;align=center;"
       "html=1;fontSize=12;strokeWidth=1;fillColor=none;")
DOIS = {"1": (0.0, 0.5), "2": (1.0, 0.5)}
SIMBOLOS = {
    "resistor":  (_EL + "shape=mxgraph.electrical.resistors.resistor_2;", 80, 20, DOIS),
    "indutor":   (_EL + "shape=mxgraph.electrical.inductors.inductor_3;", 80, 20, DOIS),
    "capacitor": (_EL + "shape=mxgraph.electrical.capacitors.capacitor_1;", 60, 40, DOIS),
    "fonte_dc":  (_EL + "shape=mxgraph.electrical.signal_sources.dc_source_3;", 40, 60,
                  {"1": (0.5, 0.0), "2": (0.5, 1.0)}),
    "fonte_v":   (_EL + "shape=mxgraph.electrical.signal_sources.dependent_source_3;", 40, 60,
                  {"1": (0.5, 0.0), "2": (0.5, 1.0)}),
    "chave":     (_EL + "shape=mxgraph.electrical.electro-mechanical.simple_switch;", 70, 20,
                  {"1": (0.0, 1.0), "2": (1.0, 1.0)}),
    "ampop":     (_EL + "shape=mxgraph.electrical.abstract.operational_amp_1;", 80, 60,
                  {"-": (0.0, 0.25), "+": (0.0, 0.75), "o": (1.0, 0.5)}),
    "terra":     (_EL + "shape=mxgraph.electrical.signal_sources.signal_ground;", 30, 20,
                  {"1": (0.5, 0.0)}),
}
LADOS = {"e": (0.0, 0.5), "d": (1.0, 0.5), "c": (0.5, 0.0), "b": (0.5, 1.0)}
DIR = {"e": (-1, 0), "d": (1, 0), "c": (0, -1), "b": (0, 1)}


def _g(v: float) -> float:
    return round(v / G) * G


def _texto_puro(s: str) -> str:
    """Para medir largura: tira tags, $$, comandos TeX e chaves."""
    s = re.sub(r"<br\s*/?>", "\n", str(s))
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("$$", "").replace("\\(", "").replace("\\)", "")
    s = re.sub(r"\\frac\{([^{}]*)\}\{([^{}]*)\}",
               lambda m: max(m.group(1), m.group(2), key=len), s)
    s = re.sub(r"\\[a-zA-Z]+", "x", s)
    s = re.sub(r"[{}^_]", "", s)
    return html.unescape(s)


def _largura(s: str) -> float:
    return max((len(l) for l in _texto_puro(s).split("\n")), default=0) * CHAR + 16


def _linhas(s: str) -> int:
    n = len(_texto_puro(s).split("\n"))
    return n + (1 if "\\frac" in str(s) else 0)


# --------------------------------------------------------------------------- #
# modelo
# --------------------------------------------------------------------------- #
@dataclass
class No:
    id: str
    tipo: str
    cx: float
    cy: float
    w: float
    h: float
    texto: str = ""
    rot: int = 0
    cor: str | None = None
    contem: list[str] = field(default_factory=list)
    rotulo: str = ""            # símbolo de circuito: texto ao lado (R = 1 Ω)

    @property
    def vw(self) -> float:      # caixa visível (girada)
        return self.h if self.rot in (90, 270) else self.w

    @property
    def vh(self) -> float:
        return self.w if self.rot in (90, 270) else self.h

    def ret(self):
        return (self.cx - self.vw / 2, self.cy - self.vh / 2, self.vw, self.vh)

    def porta(self, nome: str) -> tuple[float, float, str]:
        """(x, y, lado de saída). Lado: e/d/c/b; terminal de símbolo: o que ele aponta."""
        if nome in LADOS:
            fx, fy = LADOS[nome]
            x, y, w, h = self.ret()
            return x + fx * w, y + fy * h, nome
        term = SIMBOLOS[self.tipo][3]
        if nome not in term:
            raise ValueError(f"{self.id}: porta '{nome}' não existe (tem {sorted(term) + list(LADOS)})")
        fx, fy = term[nome]
        dx, dy = (fx - 0.5) * self.w, (fy - 0.5) * self.h
        for _ in range(self.rot // 90):          # draw.io gira no sentido horário
            dx, dy = -dy, dx
        if abs(dx) >= abs(dy):
            lado = "d" if dx > 0 else "e"
        else:
            lado = "b" if dy > 0 else "c"
        return self.cx + dx, self.cy + dy, lado


@dataclass
class Aresta:
    i: int
    de: str
    para: str
    pontos: list[tuple[float, float]]
    seta: bool
    rotulo: str = ""
    tracejada: bool = False


@dataclass
class Texto:                    # rótulo de aresta, sinal de somador, título de grupo
    id: str
    x: float
    y: float
    w: float
    h: float
    texto: str
    estilo: str = "texto"

    def ret(self):
        return (self.x, self.y, self.w, self.h)


@dataclass
class Desenho:
    titulo: str
    tipo: str
    nos: dict[str, No] = field(default_factory=dict)
    arestas: list[Aresta] = field(default_factory=list)
    textos: list[Texto] = field(default_factory=list)
    math: bool = False


# --------------------------------------------------------------------------- #
# spec -> desenho
# --------------------------------------------------------------------------- #
def _tamanho(tipo: str, d: dict) -> tuple[float, float]:
    if tipo in SIMBOLOS:
        return SIMBOLOS[tipo][1], SIMBOLOS[tipo][2]
    txt = d.get("texto", "")
    if tipo == "somador":
        return 30, 30
    if tipo in ("ramo", "juncao"):
        return 6, 6
    if tipo in ("entrada", "saida", "nota"):
        return _g(_largura(txt) + 5), 20 * _linhas(txt) + 4
    if tipo == "banco":
        return max(80, _g(_largura(txt) + 20)), 20 * _linhas(txt) + 40
    if tipo == "bloco":
        h = 40 if _linhas(txt) == 1 else 20 * _linhas(txt) + 16
        if "$$" in txt and _linhas(txt) > 1:      # MathJax é mais alto que uma linha
            h += 14 * txt.count("$$") // 2
        return max(60, _g(_largura(txt) + 15)), h
    raise ValueError(f"tipo de nó desconhecido: {tipo}")


def _endpoint(d: Desenho, ref: str, outro: No, eh_origem: bool):
    nid, _, porta = ref.partition(".")
    if nid not in d.nos:
        raise ValueError(f"aresta cita nó inexistente: {nid}")
    n = d.nos[nid]
    if not porta:
        if n.tipo in SIMBOLOS:      # terminal mais perto do outro nó
            nomes = list(SIMBOLOS[n.tipo][3])
            porta = min(nomes, key=lambda p: (n.porta(p)[0] - outro.cx) ** 2
                        + (n.porta(p)[1] - outro.cy) ** 2)
        else:
            dx, dy = outro.cx - n.cx, outro.cy - n.cy
            if abs(dx) >= abs(dy):
                porta = "d" if dx > 0 else "e"
            else:
                porta = "b" if dy > 0 else "c"
    if n.tipo in ("ramo", "juncao"):    # ponto: sai do centro, o lado só dá a direção
        lado = porta if porta in LADOS else "d"
        return (n.cx, n.cy, lado), n
    return n.porta(porta), n


def _rota(p0, lado0, p1, lado1, opc: dict, gx: float, gy: float) -> list[tuple[float, float]]:
    """Polilinha ortogonal de p0 a p1 (inclusive)."""
    if "pontos" in opc:
        meio = [(MARGEM + c * gx, MARGEM + l * gy) for c, l in opc["pontos"]]
        pts = [p0, *meio, p1]
        return _limpar(_manhattan(pts, lado0))
    (x0, y0), (x1, y1) = p0, p1
    a = (x0 + DIR[lado0][0] * SAIDA, y0 + DIR[lado0][1] * SAIDA)
    b = (x1 + DIR[lado1][0] * SAIDA, y1 + DIR[lado1][1] * SAIDA)
    if "por" in opc:            # realimentação: U por baixo/cima, na linha `nivel`
        ny = MARGEM + opc["nivel"] * gy if "nivel" in opc else None
        if ny is None:
            ny = (max(y0, y1) + gy * 0.6) if opc["por"] == "baixo" else (min(y0, y1) - gy * 0.6)
        ny = _g(ny)
        return _limpar([p0, a, (a[0], ny), (b[0], ny), b, p1])
    h0, h1 = lado0 in "ed", lado1 in "ed"
    if abs(y0 - y1) < 0.5 and h0 and h1 or abs(x0 - x1) < 0.5 and not h0 and not h1:
        return [p0, p1]
    if h0 and h1:
        xm = _g((x0 + x1) / 2)
        return _limpar([p0, (xm, y0), (xm, y1), p1])
    if not h0 and not h1:
        ym = _g((y0 + y1) / 2)
        return _limpar([p0, (x0, ym), (x1, ym), p1])
    if h0:
        return _limpar([p0, (x1, y0), p1])
    return _limpar([p0, (x0, y1), p1])


def _manhattan(pts, lado0):
    """Entre pontos dados, insere a dobra que falta (anda primeiro no eixo em que vinha)."""
    out = [pts[0]]
    horiz = lado0 in "ed"
    for q in pts[1:]:
        p = out[-1]
        if p[0] != q[0] and p[1] != q[1]:
            out.append((q[0], p[1]) if horiz else (p[0], q[1]))
            horiz = not horiz
        elif p != q:
            horiz = p[1] == q[1]
        out.append(q)
    return out


def _limpar(pts):
    """Tira pontos repetidos e os do meio de trechos colineares."""
    out = []
    for p in pts:
        p = (round(p[0], 1), round(p[1], 1))
        if out and p == out[-1]:
            continue
        if len(out) >= 2:
            a, b = out[-2], out[-1]
            if (a[0] == b[0] == p[0]) or (a[1] == b[1] == p[1]):
                out[-1] = p
                continue
        out.append(p)
    return out


def montar(spec: dict) -> Desenho:
    tipo = spec.get("tipo", "blocos")
    gx, gy = spec.get("grade", [160, 100])
    d = Desenho(spec.get("titulo", "diagrama"), tipo)
    grupos = {}
    for nid, nd in (spec.get("nos") or {}).items():
        nd = nd or {}
        t = nd.get("tipo", "bloco")
        if t == "grupo":
            grupos[nid] = nd
            continue
        col, lin = nd["pos"]
        w, h = _tamanho(t, nd)
        w, h = nd.get("w", w), nd.get("h", h)
        texto = str(nd.get("texto", ""))
        if "$$" in texto:
            d.math = True
        d.nos[nid] = No(nid, t, MARGEM + col * gx, MARGEM + lin * gy, w, h, texto,
                        int(nd.get("rot", 0)) % 360, nd.get("cor"),
                        rotulo=str(nd.get("rotulo", "")))
    # grupos: caixa em volta do que contêm (grupo dentro de grupo também)
    feitos: set[str] = set()

    def grupo(gid):
        if gid in feitos:
            return d.nos[gid]
        gd = grupos[gid]
        rets = []
        for m in gd.get("contem", []):
            if m in grupos:
                rets.append(grupo(m).ret())
            elif m in d.nos:
                n = d.nos[m]
                rets.append(n.ret())
                if n.tipo in SIMBOLOS and n.rotulo:
                    rets.append(_ret_rotulo(n))
            else:
                raise ValueError(f"grupo {gid} contém nó inexistente: {m}")
        pad = gd.get("folga", 20)
        x0 = min(r[0] for r in rets) - pad
        y0 = min(r[1] for r in rets) - pad - 22
        x1 = max(r[0] + r[2] for r in rets) + pad
        y1 = max(r[1] + r[3] for r in rets) + pad
        texto = str(gd.get("texto", gid))
        x1 = max(x1, x0 + _largura(texto) + 12)
        n = No(gid, "grupo", (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, texto,
               cor=gd.get("cor", "cinza"), contem=list(gd.get("contem", [])))
        d.nos[gid] = n
        feitos.add(gid)
        d.textos.append(Texto(f"{gid}__titulo", x0 + 6, y0 + 3, _largura(texto), 18,
                              f"<b>{html.escape(texto)}</b>", "titulo_grupo"))
        return n

    for gid in grupos:
        grupo(gid)

    for nid, n in d.nos.items():        # rótulo dos símbolos de circuito
        if n.tipo in SIMBOLOS and n.rotulo:
            x, y, w, h = _ret_rotulo(n)
            d.textos.append(Texto(f"{nid}__rotulo", x, y, w, h, n.rotulo))

    padrao_seta = tipo == "blocos"
    for i, a in enumerate(spec.get("arestas") or []):
        de, para, *resto = a
        opc = resto[0] if resto else {}
        n_de = d.nos[de.partition(".")[0]]
        n_para = d.nos[para.partition(".")[0]]
        if "sai" in opc:
            de = f"{de.partition('.')[0]}.{opc['sai']}"
        if "entra" in opc:
            para = f"{para.partition('.')[0]}.{opc['entra']}"
        (x0, y0, l0), _ = _endpoint(d, de, n_para, True)
        (x1, y1, l1), _ = _endpoint(d, para, n_de, False)
        pts = _rota((x0, y0), l0, (x1, y1), l1, opc, gx, gy)
        ar = Aresta(i, de.partition(".")[0], para.partition(".")[0], pts,
                    opc.get("seta", padrao_seta), str(opc.get("rotulo", "")),
                    opc.get("tracejada", False))
        d.arestas.append(ar)
        if ar.rotulo:
            d.textos.append(_texto_rotulo(ar, opc.get("lado_rotulo")))
            if "$$" in ar.rotulo:
                d.math = True
        if "sinal" in opc:
            d.textos.append(_texto_sinal(ar, str(opc["sinal"])))

    for k, v in (spec.get("textos") or {}).items():   # texto solto: {pos, texto}
        col, lin = v["pos"]
        w, h = _largura(v["texto"]), 20 * _linhas(v["texto"])
        d.textos.append(Texto(k, MARGEM + col * gx - w / 2, MARGEM + lin * gy - h / 2, w, h,
                              str(v["texto"])))

    if spec.get("legenda"):
        _legenda(d, spec["legenda"])
    return d


def _ret_rotulo(n: No):
    """Rótulo de símbolo: abaixo se o símbolo é horizontal, à direita se vertical."""
    w, h = _largura(n.rotulo), 18 * _linhas(n.rotulo)
    x, y, vw, vh = n.ret()
    if vw >= vh:
        return (n.cx - w / 2, y + vh + 2, w, h)
    return (x + vw + 4, n.cy - h / 2, w, h)


def _texto_rotulo(a: Aresta, lado: str | None) -> Texto:
    """No meio do trecho mais comprido: acima (horizontal) ou à direita (vertical)."""
    segs = list(zip(a.pontos, a.pontos[1:]))
    (xa, ya), (xb, yb) = max(segs, key=lambda s: abs(s[1][0] - s[0][0]) + abs(s[1][1] - s[0][1]))
    w, h = _largura(a.rotulo), 18 * _linhas(a.rotulo)
    mx, my = (xa + xb) / 2, (ya + yb) / 2
    if ya == yb:
        y = my + 3 if lado == "baixo" else my - h - 3
        return Texto(f"e{a.i}__rotulo", mx - w / 2, y, w, h, a.rotulo)
    x = mx - w - 4 if lado == "esquerda" else mx + 4
    return Texto(f"e{a.i}__rotulo", x, my - h / 2, w, h, a.rotulo)


def _texto_sinal(a: Aresta, s: str) -> Texto:
    """Sinal do somador perto da ponta da seta, fora da linha."""
    (xa, ya), (xb, yb) = a.pontos[-2], a.pontos[-1]
    s = s.replace("-", "−")
    if ya == yb:                                # chega na horizontal: sinal acima
        x = xb - 16 if xb > xa else xb + 4
        return Texto(f"e{a.i}__sinal", x, yb - 20, 12, 16, s, "sinal")
    y = yb + 4 if yb < ya else yb - 20         # chega na vertical: sinal à esquerda
    return Texto(f"e{a.i}__sinal", xb - 16, y, 12, 16, s, "sinal")


def _legenda(d: Desenho, leg: dict):
    _, _, _, y1 = _limites(d)
    td = 'style="border:1px solid #999;padding:2px 6px;text-align:left"'
    corpo = "".join(f"<tr><td {td}>{html.escape(str(k))}</td><td {td}>{html.escape(str(v))}</td></tr>"
                    for k, v in leg.items())
    tab = f'<table style="border-collapse:collapse;font-size:12px">{corpo}</table>'
    w = max(_largura(str(k)) for k in leg) + max(_largura(str(v)) for v in leg.values()) + 20
    d.textos.append(Texto("legenda", MARGEM, _g(y1 + 40), w, 22 * len(leg) + 6, tab, "legenda"))


def _limites(d: Desenho):
    rets = [n.ret() for n in d.nos.values()] + [t.ret() for t in d.textos]
    pts = [p for a in d.arestas for p in a.pontos]
    x0 = min([r[0] for r in rets] + [p[0] for p in pts])
    y0 = min([r[1] for r in rets] + [p[1] for p in pts])
    x1 = max([r[0] + r[2] for r in rets] + [p[0] for p in pts])
    y1 = max([r[1] + r[3] for r in rets] + [p[1] for p in pts])
    return x0, y0, x1, y1


# --------------------------------------------------------------------------- #
# checagem geométrica (núcleo comum; o GRAFCET do es925 também usa):
# linha sobre retângulo, linha sobre linha, cruzamento, retângulo sobre retângulo
# --------------------------------------------------------------------------- #
def _corta(seg, r, folga=1.0) -> bool:
    x1, y1, x2, y2 = seg
    rx, ry, rw, rh = r
    xa, xb = sorted((x1, x2))
    ya, yb = sorted((y1, y2))
    return xa < rx + rw - folga and xb > rx + folga and ya < ry + rh - folga and yb > ry + folga


def _sobrepoe(ra, rb) -> bool:
    return (ra[0] < rb[0] + rb[2] and rb[0] < ra[0] + ra[2]
            and ra[1] < rb[1] + rb[3] and rb[1] < ra[1] + ra[3])


def _dentro(ra, rb) -> bool:
    return (rb[0] <= ra[0] and ra[0] + ra[2] <= rb[0] + rb[2]
            and rb[1] <= ra[1] and ra[1] + ra[3] <= rb[1] + rb[3])


def conflitos(linhas, rets, juntas=None) -> list[tuple[str, tuple[int, ...]]]:
    """Núcleo da checagem. (mensagem, índices das linhas envolvidas).

    linhas: [(nome, pontos, ids de retângulo que ela pode tocar)]
    rets:   [(id, (x, y, w, h))]
    juntas(i, j) -> True: as linhas i e j podem correr juntas (mesmo feixe)."""
    probs = []
    segs = [(i, (p[0], p[1], q[0], q[1])) for i, (_, pts, _) in enumerate(linhas)
            for p, q in zip(pts, pts[1:]) if p != q]
    for i, seg in segs:
        nome, _, pode = linhas[i]
        for rid, r in rets:
            if rid not in pode and _corta(seg, r):
                probs.append((f"linha {nome} passa sobre {rid}", (i,)))
    for a in range(len(segs)):
        for b in range(a + 1, len(segs)):
            (i, s1), (j, s2) = segs[a], segs[b]
            if i == j or (juntas and juntas(i, j)):
                continue
            ni, nj = linhas[i][0], linhas[j][0]
            h1, h2 = s1[1] == s1[3], s2[1] == s2[3]
            if h1 == h2:
                f1, f2 = (s1[1], s2[1]) if h1 else (s1[0], s2[0])
                if abs(f1 - f2) > 0.5:
                    continue
                a1 = sorted((s1[0], s1[2]) if h1 else (s1[1], s1[3]))
                a2 = sorted((s2[0], s2[2]) if h2 else (s2[1], s2[3]))
                if min(a1[1], a2[1]) - max(a1[0], a2[0]) > 1:
                    probs.append((f"linhas sobrepostas: {ni} e {nj}", (i, j)))
            else:
                hz, vt = (s1, s2) if h1 else (s2, s1)
                if (min(hz[0], hz[2]) < vt[0] < max(hz[0], hz[2])
                        and min(vt[1], vt[3]) < hz[1] < max(vt[1], vt[3])):
                    probs.append((f"cruzamento: {ni} x {nj}", (i, j)))
    for a in range(len(rets)):
        for b in range(a + 1, len(rets)):
            (ia, ra), (ib, rb) = rets[a], rets[b]
            if _sobrepoe(ra, rb):
                probs.append((f"sobrepostos: {ia} e {ib}", ()))
    return probs


def colisoes(d: Desenho) -> list[str]:
    linhas = [(f"{a.de}->{a.para}", a.pontos,
               {a.de, a.para, f"e{a.i}__rotulo", f"e{a.i}__sinal"}) for a in d.arestas]
    rets = [(n.id, n.ret()) for n in d.nos.values() if n.tipo != "grupo"]
    rets += [(t.id, t.ret()) for t in d.textos]

    def juntas(i, j):   # só se encontram num ponto comum (junção, ramo, mesma porta)
        pa, pb = d.arestas[i].pontos, d.arestas[j].pontos
        return bool({pa[0], pa[-1]} & {pb[0], pb[-1]})

    probs = [m for m, _ in conflitos(linhas, rets, juntas)]
    # grupos: ou um contém o outro, ou não se tocam; nó de fora não entra no grupo
    grupos = [n for n in d.nos.values() if n.tipo == "grupo"]
    for i, ga in enumerate(grupos):
        for gb in grupos[i + 1:]:
            ra, rb = ga.ret(), gb.ret()
            if _sobrepoe(ra, rb) and not (_dentro(ra, rb) or _dentro(rb, ra)):
                probs.append(f"grupos se cruzam: {ga.id} e {gb.id}")
        membros = _membros(d, ga)
        for n in d.nos.values():
            if n.tipo != "grupo" and n.id not in membros and _sobrepoe(n.ret(), ga.ret()):
                probs.append(f"nó {n.id} invade o grupo {ga.id}")
    return probs


def _membros(d: Desenho, g: No) -> set[str]:
    out = set()
    for m in g.contem:
        out.add(m)
        if d.nos[m].tipo == "grupo":
            out |= _membros(d, d.nos[m])
    return out


# --------------------------------------------------------------------------- #
# saída draw.io
# --------------------------------------------------------------------------- #
_BASE = "html=1;whiteSpace=wrap;fontSize=12;"
_ESTILO = {
    "bloco": _BASE + "rounded=0;",
    "banco": _BASE + "shape=cylinder3;boundedLbl=1;backgroundOutline=1;size=10;",
    "somador": _BASE + "ellipse;aspect=fixed;",
    "ramo": "ellipse;aspect=fixed;fillColor=#000000;strokeColor=#000000;html=1;",
    "juncao": "ellipse;aspect=fixed;fillColor=#000000;strokeColor=#000000;html=1;",
    "entrada": "text;" + _BASE + "align=center;verticalAlign=middle;",
    "saida": "text;" + _BASE + "align=center;verticalAlign=middle;",
    "nota": "text;" + _BASE + "align=left;verticalAlign=top;strokeColor=#999999;dashed=1;spacingLeft=6;",
    "grupo": "rounded=1;arcSize=4;dashed=1;html=1;fontSize=12;container=0;",
    "texto": "text;html=1;align=center;verticalAlign=middle;fontSize=12;",
    "sinal": "text;html=1;align=center;verticalAlign=middle;fontSize=14;fontStyle=1;",
    "titulo_grupo": "text;html=1;align=left;verticalAlign=middle;fontSize=12;",
    "legenda": "text;html=1;align=left;verticalAlign=top;whiteSpace=wrap;fontSize=12;",
    "titulo": "text;html=1;align=left;verticalAlign=middle;fontSize=16;fontStyle=1;",
}


def _attr(s: str) -> str:
    return html.escape(s, quote=True)


def vertice(cid: str, valor: str, estilo: str, x: float, y: float, w: float, h: float) -> str:
    return (f'<mxCell id="{_attr(cid)}" value="{_attr(valor)}" style="{estilo}" vertex="1" '
            f'parent="1"><mxGeometry x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" '
            f'as="geometry"/></mxCell>')


def mxfile(paginas, host: str = "NoteProject/tools/diagrama.py") -> str:
    """paginas: [(nome, [células xml], math)] -> arquivo .drawio."""
    out = [f'<mxfile host="{_attr(host)}" type="device">']
    for n, (nome, celulas, math) in enumerate(paginas):
        out.append(f'<diagram name="{_attr(nome)}" id="p{n}"><mxGraphModel grid="1" '
                   f'gridSize="10" guides="1" connect="1" arrows="1" page="1" pageWidth="1654" '
                   f'pageHeight="1169" math="{1 if math else 0}" background="#ffffff"><root>'
                   '<mxCell id="0"/><mxCell id="1" parent="0"/>')
        out += celulas
        out.append("</root></mxGraphModel></diagram>")
    out.append("</mxfile>")
    return "\n".join(out)


def _estilo_no(n: No) -> str:
    if n.tipo in SIMBOLOS:
        s = SIMBOLOS[n.tipo][0]
    else:
        s = _ESTILO[n.tipo]
    if n.rot:
        s += f"rotation={n.rot};"
    if n.cor and n.tipo in ("bloco", "banco", "grupo", "somador"):
        fill, stroke = CORES[n.cor]
        s += f"fillColor={fill};strokeColor={stroke};"
        if n.tipo == "grupo":
            s += "opacity=60;"
    elif n.tipo == "grupo":
        s += "fillColor=none;strokeColor=#666666;"
    return s


def drawio(d: Desenho) -> str:
    x0, y0, _, _ = _limites(d)
    dx, dy = 20 - x0, 60 - y0         # 40 px de folga em cima para o título
    cel = []

    def v(cid, valor, estilo, x, y, w, h):
        cel.append(vertice(cid, valor, estilo, x + dx, y + dy, w, h))

    v("titulo", html.escape(d.titulo), _ESTILO["titulo"], x0, y0 - 45, _largura(d.titulo) * 1.3, 26)
    # grupos primeiro (ficam atrás), do maior para o menor
    for n in sorted((n for n in d.nos.values() if n.tipo == "grupo"), key=lambda n: -n.w * n.h):
        v(n.id, "", _estilo_no(n), *n.ret())
    for n in d.nos.values():
        if n.tipo != "grupo":
            v(n.id, "" if n.tipo in SIMBOLOS else n.texto, _estilo_no(n),
              n.cx - n.w / 2, n.cy - n.h / 2, n.w, n.h)
    for a in d.arestas:
        fim = "block;endFill=1" if a.seta else "none"
        estilo = f"html=1;rounded=0;endArrow={fim};startArrow=none;{'dashed=1;' if a.tracejada else ''}"
        (sx, sy), (tx, ty) = a.pontos[0], a.pontos[-1]
        meio = "".join(f'<mxPoint x="{x + dx:.0f}" y="{y + dy:.0f}"/>' for x, y in a.pontos[1:-1])
        arr = f'<Array as="points">{meio}</Array>' if meio else ""
        cel.append(f'<mxCell id="e{a.i}" style="{estilo}" edge="1" parent="1">'
                   f'<mxGeometry relative="1" as="geometry">'
                   f'<mxPoint x="{sx + dx:.0f}" y="{sy + dy:.0f}" as="sourcePoint"/>'
                   f'<mxPoint x="{tx + dx:.0f}" y="{ty + dy:.0f}" as="targetPoint"/>'
                   f'{arr}</mxGeometry></mxCell>')
    for t in d.textos:
        v(t.id, t.texto, _ESTILO[t.estilo], t.x, t.y, t.w, t.h)
    return mxfile([(d.titulo, cel, d.math)])


# --------------------------------------------------------------------------- #
# exportar com o draw.io desktop
# --------------------------------------------------------------------------- #
def drawio_cli() -> str | None:
    return shutil.which("drawio") or shutil.which("draw.io")


def exportar(arq: pathlib.Path, fmt: str, saida: pathlib.Path) -> bool:
    cli = drawio_cli()
    if not cli:
        return False
    extra = {"svg": ["--embed-diagram"], "png": ["-s", "2", "-b", "10"]}.get(fmt, [])
    cmd = [cli, "-x", "-f", fmt, *extra, "-o", str(saida), "--no-sandbox"]
    cmd.append(str(arq))
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return r.returncode == 0 and saida.exists()


# --------------------------------------------------------------------------- #
# cli
# --------------------------------------------------------------------------- #
def gerar(spec_path: pathlib.Path, pasta: pathlib.Path | None = None,
          png_dir: pathlib.Path | None = None) -> tuple[pathlib.Path, list[str], list[pathlib.Path]]:
    """Grava <nome>.drawio (+ .drawio.svg; + png se png_dir). Devolve (drawio, colisões, extras)."""
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    d = montar(spec)
    pasta = pasta or spec_path.parent
    pasta.mkdir(parents=True, exist_ok=True)
    arq = pasta / f"{spec_path.stem}.drawio"
    arq.write_text(drawio(d), encoding="utf-8")
    extras = []
    svg = pasta / f"{spec_path.stem}.drawio.svg"
    if exportar(arq, "svg", svg):
        extras.append(svg)
    if png_dir:
        png_dir.mkdir(parents=True, exist_ok=True)
        png = png_dir / f"{spec_path.stem}.png"
        if exportar(arq, "png", png):
            extras.append(png)
    return arq, colisoes(d), extras


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", type=pathlib.Path)
    ap.add_argument("-o", type=pathlib.Path, help="pasta de saída (padrão: a do yaml)")
    ap.add_argument("--png", type=pathlib.Path, nargs="?", const=pathlib.Path("build"),
                    help="também exporta PNG (padrão: build/)")
    a = ap.parse_args(argv)
    arq, probs, extras = gerar(a.spec, a.o, a.png)
    print(f"gravado {arq}")
    for e in extras:
        print(f"gravado {e}")
    if not drawio_cli():
        print("  aviso: draw.io desktop não encontrado (sudo pacman -S drawio-desktop): "
              "sem .drawio.svg/.png")
    for p in probs:
        print(f"  COLISAO {p}")
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main())
