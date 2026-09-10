#!/usr/bin/env python3
"""Folha A4 de ETIQUETAS pequenas para marcar os CABOS (dentro da caixa CTO).

Cada etiqueta: faixa da COR da ligação + NOME do roteador + IP/gateway.
Uma linha por roteador, várias cópias por linha.  Recortar, enrolar no cabo e
cobrir com fita transparente.  Gera docs/etiquetas_roteadores.pdf.

Renderizado em alta resolução (600 dpi) para não sair apagado na impressão.
"""
from PIL import Image, ImageDraw, ImageFont
from fibra_dados import ROUTERS, ROUTE_BY_KEY, IP_ROTEADOR
from paths import docs

FD = "/usr/share/fonts/truetype/dejavu/"
DPI = 600
S = DPI / 150.0                    # fator de escala sobre o layout base (150 dpi)

def _f(n, s):
    return ImageFont.truetype(FD + n, int(round(s * S)))

def u(v):                          # "unidades" do layout base -> pixels
    return int(round(v * S))

PW, PH = u(1240), u(1754)          # A4
MARGIN = u(48)
GUT = u(10)
COLS = 4                           # cópias por linha
BLOCKS = 2                         # repete a lista (mais cópias por folha)
INK = (16, 20, 28)
MUTE = (100, 110, 125)
LINE = (150, 158, 170)

ORDER = ["CTO", "MOTOR", "RANCHO", "PORTEIRA", "POMAR", "SEDE", "PISCINA", "MÃE", "LAZER"]
BY_NAME = {txt: lig for (_p, txt, _s, lig, _loc) in ROUTERS}

im = Image.new("RGB", (PW, PH), (255, 255, 255))
d = ImageDraw.Draw(im)

d.text((MARGIN, u(20)), "ETIQUETAS DOS CABOS  —  Rede de fibra · Fazenda Sagrada Família",
       font=_f("DejaVuSans-Bold.ttf", 16), fill=INK)
d.text((MARGIN, u(41)), "imprimir em A4 a 100% · recortar · enrolar no cabo e cobrir com fita transparente",
       font=_f("DejaVuSans.ttf", 11), fill=MUTE)

TOP = u(66)
ROWS = len(ORDER) * BLOCKS
CW = (PW - 2 * MARGIN - (COLS - 1) * GUT) / COLS
CH = (PH - TOP - MARGIN - (ROWS - 1) * GUT) / ROWS
BAND = CW * 0.30
F_NAME = _f("DejaVuSans-Bold.ttf", 30)
F_IP = _f("DejaVuSans-Bold.ttf", 17)
F_RJ = _f("DejaVuSans-Bold.ttf", 15)
LW = max(1, u(1))


def label(x, y, name):
    rt = ROUTE_BY_KEY[BY_NAME[name]]
    rgb = tuple(rt["rgb"])
    white = rgb == (255, 255, 255)

    d.rectangle([x, y, x + CW, y + CH], outline=LINE, width=LW)
    d.rectangle([x + LW, y + LW, x + BAND, y + CH - LW], fill=(232, 233, 235) if white else rgb)
    d.line([(x + BAND, y + LW), (x + BAND, y + CH - LW)], fill=LINE, width=LW)
    if white:
        w = d.textlength("RJ45", font=F_RJ)
        d.text((x + LW + (BAND - w) / 2, y + CH / 2 - u(9)), "RJ45", font=F_RJ, fill=(110, 120, 132))

    tx = x + BAND + u(14)
    d.text((tx, y + CH / 2 - u(30)), name, font=F_NAME, fill=INK)
    d.text((tx, y + CH / 2 + u(7)), IP_ROTEADOR.get(name, "—"), font=F_IP, fill=INK)


for b in range(BLOCKS):
    for i, name in enumerate(ORDER):
        y = TOP + (b * len(ORDER) + i) * (CH + GUT)
        for c in range(COLS):
            label(MARGIN + c * (CW + GUT), y, name)

out = docs("etiquetas_roteadores.pdf")
im.save(out, resolution=float(DPI))
print("salvo:", out, im.size, f"({DPI} dpi)")
