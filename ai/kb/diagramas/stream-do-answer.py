"""GIF do caminho de uma resposta do POST /chat dentro do `answer` (lonzo).

Uso: uv run --with pillow python ai/kb/diagramas/stream-do-answer.py [saida.gif]
Sem argumento, grava em ai/obsidian/IA no projeto/Figuras/stream-do-answer.gif.
"""

import sys
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[3]
SAIDA = RAIZ / "ai/obsidian/IA no projeto/Figuras/stream-do-answer.gif"

W, H = 1280, 760
MONO = "/usr/share/fonts/TTF/JetBrainsMonoNerdFontMono-Regular.ttf"
MONO_B = "/usr/share/fonts/TTF/JetBrainsMonoNerdFontMono-Bold.ttf"
SANS = "/usr/share/fonts/noto/NotoSans-Regular.ttf"
SANS_B = "/usr/share/fonts/noto/NotoSans-Bold.ttf"

F_CODE = ImageFont.truetype(MONO, 15)
F_CODE_B = ImageFont.truetype(MONO_B, 15)
F_LANE = ImageFont.truetype(SANS_B, 19)
F_SUB = ImageFont.truetype(SANS, 14)
F_STAT = ImageFont.truetype(SANS, 15)
F_PKT = ImageFont.truetype(MONO_B, 14)
F_CAP = ImageFont.truetype(SANS, 21)
F_CAP_B = ImageFont.truetype(SANS_B, 21)
F_BR = ImageFont.truetype(MONO, 13)
F_BR_TXT = ImageFont.truetype(SANS, 20)

BG = "#f6f5f2"
INK = "#1f2328"
MUTED = "#6b7078"
LIB = "#dfe3e8"
MINE = "#ffe7b8"
MINE_EDGE = "#d08a00"
HL = "#ffd36b"
PKT_REQ = "#3b6fd9"
PKT_DATA = "#1f9d55"
PKT_ERR = "#c43c3c"
CODE_BG = "#ffffff"

# Raias: nome, subtítulo, centro x, é código do usuário?
RAIAS = [
    ("Navegador", "front", 160, False),
    ("StreamingResponse", "lib (Starlette)", 480, False),
    ("answer()", "SEU código", 800, True),
    ("Anthropic", "via SDK (lib)", 1120, False),
]
NAV, SR, ANS, ANT = 0, 1, 2, 3

CODIGO = [
    (42, "async def answer(question, client):"),
    (44, '    yield event("message_start", {"model": MODEL})'),
    (46, "    try:"),
    (47, "        async with client.messages.stream("),
    (48, "            model=MODEL, max_tokens=MAX_TOKENS,"),
    (50, '            system=RULES_PATH.read_text(...),'),
    (51, '            messages=[{"role": "user", ...}],'),
    (52, "        ) as stream:"),
    (53, "            async for text in stream.text_stream:"),
    (54, '                yield event("text_delta", {"text": text})'),
    (56, "            final = await stream.get_final_message()"),
    (58, "    except APIError as error:"),
    (59, '        yield event("error", {...})'),
    (61, "        return"),
    (63, "    usage = {...input_tokens, output_tokens...}"),
    (67, '    yield event("message_end",'),
    (68, '        {"stop_reason": ..., "usage": usage})'),
]


@dataclass
class Passo:
    legenda: str
    linhas: tuple[int, ...] = ()
    pacote: tuple[int, int, str, str] | None = None  # de, para, texto, cor
    status: dict[int, str] = field(default_factory=dict)
    eventos: tuple[str, ...] = ()  # eventos novos que o navegador recebe
    texto: str = ""  # texto novo na tela do navegador
    segura: int = 2600  # ms parado no fim
    so_eventos: tuple[str, ...] | None = None  # cena à parte (erro)
    so_tela: str | None = None


PASSOS = [
    Passo(
        "**chat()** devolveu StreamingResponse(answer(...)). "
        "O answer foi chamado, mas **nada dele rodou:** é só um gerador parado.",
        status={SR: "tem o gerador guardado", ANS: "parado antes da linha 42"},
        segura=3600,
    ),
    Passo(
        "A lib já mandou os headers (200, text/event-stream). "
        "Agora **pede o 1º item** ao gerador.",
        pacote=(SR, ANS, "next()", PKT_REQ),
        status={NAV: "recebeu 200, espera", SR: "esperando item"},
        linhas=(42,),
    ),
    Passo(
        "O answer roda até o **1º yield** (linha 44) e entrega o texto do "
        "evento. **Para ali.**",
        pacote=(ANS, SR, "message_start", PKT_DATA),
        linhas=(44,),
        status={ANS: "PARADO no yield (44)"},
    ),
    Passo(
        "A lib escreve o evento na conexão com o navegador.",
        pacote=(SR, NAV, "message_start", PKT_DATA),
        linhas=(44,),
        eventos=("event: message_start",),
        status={SR: "enviou", ANS: "PARADO no yield (44)"},
    ),
    Passo(
        "A lib **pede o próximo item**: o answer continua depois da linha 44.",
        pacote=(SR, ANS, "next()", PKT_REQ),
        linhas=(46, 47),
        status={SR: "esperando item"},
    ),
    Passo(
        "Linhas 47–52: o SDK abre **uma** request HTTP para a Anthropic, "
        "com as regras e a pergunta, pedindo stream.",
        pacote=(ANS, ANT, "POST /v1/messages", PKT_REQ),
        linhas=(47, 48, 50, 51, 52),
        status={ANT: "gerando texto...", SR: "esperando item"},
    ),
    Passo(
        "Linha 53: o loop **espera** o próximo pedaço. "
        "A Anthropic manda o 1º: \"O ichiro\".",
        pacote=(ANT, ANS, '"O ichiro"', PKT_DATA),
        linhas=(53,),
        status={ANS: "esperando pedaço (53)", ANT: "gerando texto...",
                SR: "esperando item"},
    ),
    Passo(
        "Linha 54: embrulha o pedaço em SSE e entrega no yield. "
        "**Para de novo.**",
        pacote=(ANS, SR, "text_delta", PKT_DATA),
        linhas=(54,),
        status={ANS: "PARADO no yield (54)", ANT: "gerando texto..."},
    ),
    Passo(
        "A lib envia; o navegador já mostra o começo do texto.",
        pacote=(SR, NAV, "text_delta", PKT_DATA),
        linhas=(54,),
        eventos=('event: text_delta  "O ichiro"',),
        texto="O ichiro",
        status={ANS: "PARADO no yield (54)", ANT: "gerando texto..."},
    ),
    Passo(
        "A lib pede o próximo: o answer **volta para a linha 53** "
        "(próxima volta do loop).",
        pacote=(SR, ANS, "next()", PKT_REQ),
        linhas=(53,),
        status={ANS: "esperando pedaço (53)", ANT: "gerando texto...",
                SR: "esperando item"},
        segura=1600,
    ),
    Passo(
        "Mesmo ciclo: pedaço chega (53), yield (54), lib envia ao navegador.",
        pacote=(ANT, ANS, '" é a API de notas."', PKT_DATA),
        linhas=(53,),
        status={ANS: "esperando pedaço (53)", ANT: "gerando texto...",
                SR: "esperando item"},
        segura=1400,
    ),
    Passo(
        "Mesmo ciclo: pedaço chega (53), yield (54), lib envia ao navegador.",
        pacote=(ANS, SR, "text_delta", PKT_DATA),
        linhas=(54,),
        status={ANS: "PARADO no yield (54)", ANT: "gerando texto..."},
        segura=1000,
    ),
    Passo(
        "Mesmo ciclo: pedaço chega (53), yield (54), lib envia ao navegador.",
        pacote=(SR, NAV, "text_delta", PKT_DATA),
        linhas=(54,),
        eventos=('event: text_delta  " é a API de notas."',),
        texto=" é a API de notas.",
        status={ANS: "PARADO no yield (54)", ANT: "gerando texto..."},
        segura=2000,
    ),
    Passo(
        "Próximo item: volta à linha 53, mas a Anthropic **terminou**. "
        "O loop acaba.",
        pacote=(ANT, ANS, "fim do stream", PKT_REQ),
        linhas=(53,),
        status={ANT: "terminou", SR: "esperando item"},
    ),
    Passo(
        "Linha 56: pede ao SDK a mensagem completa, de onde saem "
        "stop_reason e os tokens gastos.",
        linhas=(56,),
        status={ANT: "conexão fechada", SR: "esperando item",
                ANS: "montando o fim"},
    ),
    Passo(
        "Linhas 63–68: o **último yield**, com o resumo.",
        pacote=(ANS, SR, "message_end", PKT_DATA),
        linhas=(63, 67, 68),
        status={ANT: "conexão fechada", ANS: "PARADO no yield (67)"},
    ),
    Passo(
        "A lib envia o último evento ao navegador.",
        pacote=(SR, NAV, "message_end", PKT_DATA),
        linhas=(67, 68),
        eventos=("event: message_end",),
        status={ANT: "conexão fechada", ANS: "PARADO no yield (67)"},
    ),
    Passo(
        "Pede mais um item: a função **acaba**. A lib vê o fim do gerador "
        "e fecha a resposta.",
        pacote=(SR, NAV, "fim do corpo", PKT_REQ),
        status={ANS: "terminou", SR: "fechou a resposta",
                NAV: "resposta completa", ANT: "conexão fechada"},
        segura=3000,
    ),
    Passo(
        "**Outro caso, com erro** (key errada, limite, rede): a linha 58 "
        "pega o erro, o yield da 59 manda o evento **error** e o return "
        "(61) encerra. O 200 já saiu, então o erro vai como evento.",
        so_eventos=("event: message_start", "event: error"),
        so_tela="(só a mensagem de erro)",
        linhas=(58, 59, 61),
        status={ANS: "caminho de erro", NAV: "resposta completa",
                ANT: "conexão fechada", SR: "fechou a resposta"},
        segura=4500,
    ),
]

Y_RAIA = 24
Y_PKT = 175
Y_PAINEL = 240
Y_LEG = 668


def texto_rico(d: ImageDraw.ImageDraw, x: int, y: int, s: str,
               largura: int) -> None:
    """Escreve com **negrito**, quebrando linha na largura."""
    pedacos: list[tuple[str, bool]] = []
    for i, parte in enumerate(s.split("**")):
        for palavra in parte.split(" "):
            if palavra:
                pedacos.append((palavra, i % 2 == 1))
    cx, cy = x, y
    for palavra, negrito in pedacos:
        f = F_CAP_B if negrito else F_CAP
        w = d.textlength(palavra + " ", font=f)
        if cx + w > x + largura:
            cx, cy = x, cy + 30
        d.text((cx, cy), palavra, font=f, fill=INK)
        cx += w


def desenha(p: Passo, t: float, eventos: list[str], tela: str) -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # Raias
    for i, (nome, sub, cx, meu) in enumerate(RAIAS):
        x0, x1 = cx - 140, cx + 140
        d.rounded_rectangle(
            (x0, Y_RAIA, x1, Y_RAIA + 74), 12,
            fill=MINE if meu else LIB,
            outline=MINE_EDGE if meu else "#b8bec6", width=3 if meu else 1,
        )
        d.text((cx, Y_RAIA + 26), nome, font=F_LANE, fill=INK, anchor="mm")
        d.text((cx, Y_RAIA + 52), sub, font=F_SUB,
               fill=MINE_EDGE if meu else MUTED, anchor="mm")
        st = p.status.get(i, "")
        if st:
            cor = PKT_ERR if "PARADO" in st or "erro" in st else MUTED
            d.text((cx, Y_RAIA + 98), st, font=F_STAT, fill=cor, anchor="mm")
        d.line((cx, Y_RAIA + 112, cx, Y_PKT + 30), fill="#c9cdd3", width=2)

    # Pacote em movimento
    if p.pacote:
        de, para, rot, cor = p.pacote
        xa, xb = RAIAS[de][2], RAIAS[para][2]
        d.line((xa, Y_PKT, xb, Y_PKT), fill="#c9cdd3", width=2)
        seta = 1 if xb > xa else -1
        d.polygon([(xb, Y_PKT), (xb - 12 * seta, Y_PKT - 7),
                   (xb - 12 * seta, Y_PKT + 7)], fill="#9aa0a8")
        x = xa + (xb - xa) * t
        w = d.textlength(rot, font=F_PKT) + 22
        d.rounded_rectangle((x - w / 2, Y_PKT - 16, x + w / 2, Y_PKT + 16),
                            8, fill=cor)
        d.text((x, Y_PKT), rot, font=F_PKT, fill="white", anchor="mm")

    # Painel de código
    cx0, cx1 = 20, 770
    d.rounded_rectangle((cx0, Y_PAINEL, cx1, Y_LEG - 16), 10,
                        fill=CODE_BG, outline="#d0d4da")
    d.text((cx0 + 14, Y_PAINEL + 10), "apps/lonzo/src/lonzo/routers/chat.py",
           font=F_SUB, fill=MUTED)
    y = Y_PAINEL + 36
    for n, linha in CODIGO:
        ativo = n in p.linhas
        if ativo:
            d.rectangle((cx0 + 4, y - 2, cx1 - 4, y + 19), fill=HL)
        d.text((cx0 + 12, y), f"{n:>3}", font=F_CODE, fill=MUTED)
        d.text((cx0 + 52, y), linha, font=F_CODE_B if ativo else F_CODE,
               fill=INK)
        y += 21

    # Painel do navegador
    bx0, bx1 = 790, 1260
    d.rounded_rectangle((bx0, Y_PAINEL, bx1, Y_LEG - 16), 10,
                        fill=CODE_BG, outline="#d0d4da")
    d.rectangle((bx0 + 1, Y_PAINEL + 1, bx1 - 1, Y_PAINEL + 30), fill=LIB)
    d.text((bx0 + 14, Y_PAINEL + 8), "Navegador — o que chegou",
           font=F_SUB, fill=INK)
    d.text((bx0 + 14, Y_PAINEL + 42), "eventos SSE:", font=F_SUB, fill=MUTED)
    y = Y_PAINEL + 64
    if p.so_eventos is not None:
        eventos, tela = list(p.so_eventos), p.so_tela or ""
    for e in eventos:
        d.text((bx0 + 18, y), e, font=F_BR, fill=INK)
        y += 20
    d.text((bx0 + 14, Y_PAINEL + 230), "na tela:", font=F_SUB, fill=MUTED)
    d.text((bx0 + 18, Y_PAINEL + 254), tela or "…", font=F_BR_TXT, fill=INK)

    # Legenda
    texto_rico(d, 24, Y_LEG, p.legenda, W - 48)
    return img


def main() -> None:
    saida = Path(sys.argv[1]) if len(sys.argv) > 1 else SAIDA
    quadros: list[Image.Image] = []
    tempos: list[int] = []
    eventos: list[str] = []
    tela = ""
    for p in PASSOS:
        if p.pacote:
            for k in range(10):
                quadros.append(desenha(p, k / 9, eventos, tela))
                tempos.append(55)
        eventos += list(p.eventos)
        tela += p.texto
        quadros.append(desenha(p, 1.0, eventos, tela))
        tempos.append(p.segura)
    quadros = [q.quantize(colors=128, dither=Image.Dither.NONE)
               for q in quadros]
    saida.parent.mkdir(parents=True, exist_ok=True)
    quadros[0].save(saida, save_all=True, append_images=quadros[1:],
                    duration=tempos, loop=0, optimize=True)
    print(saida, f"{len(quadros)} quadros", f"{sum(tempos) / 1000:.0f}s")


if __name__ == "__main__":
    main()
