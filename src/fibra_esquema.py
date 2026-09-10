#!/usr/bin/env python3
"""Esquema (diagrama) da rede de fibra - serve de legenda e de topologia.
Pode rodar sozinho (gera fibra_esquema.png) ou ser desenhado dentro de outra imagem
via draw_schematic().
"""
import os
from PIL import Image, ImageDraw, ImageFont
from fibra_dados import ROUTE_BY_KEY, ROUTERS, LINK_EQUIP, rgb_hex

FD = "/usr/share/fonts/truetype/dejavu/"
def _f(name, size):
    return ImageFont.truetype(FD + name, size)

BG      = (15, 20, 32)
PANEL   = (23, 30, 46)
INK     = (238, 242, 250)
MUTE    = (165, 178, 198)
C_ATIVO = (35, 130, 255)
C_OBRA  = (255, 70, 70)

# ordem das colunas (ramais) no diagrama
COLS = ["rj45", "piscina", "pomar", "porteira", "mae", "lazer", "motor", "sede"]
ROUTER_BY_LINK = {lig: (txt, status, local) for (_p, txt, status, lig, local) in ROUTERS}


def _wrap(d, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if d.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def draw_schematic(d, ox, oy, w, h):
    f_h1   = _f("DejaVuSans-Bold.ttf", 30)
    f_box  = _f("DejaVuSans-Bold.ttf", 23)
    f_sm   = _f("DejaVuSans-Bold.ttf", 17)
    f_via  = _f("DejaVuSans.ttf", 15)
    f_key  = _f("DejaVuSans.ttf", 17)

    def box(x0, y0, x1, y1, border, fill=PANEL, wd=3, r=12):
        d.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=fill, outline=border, width=wd)

    def ctext(cx, y, text, font, fill=INK):
        tw = d.textlength(text, font=font)
        d.text((cx - tw / 2, y), text, font=font, fill=fill)

    d.text((ox + 24, oy + 16), "ESQUEMA DA REDE — cada cor é uma ligação", font=f_h1, fill=INK)

    pad = 60
    inner = w - 2 * pad
    ncol = len(COLS)
    col_w = inner / ncol
    col_cx = [ox + pad + col_w * (i + 0.5) for i in range(ncol)]

    chain_y = oy + 78
    ch = 58
    # Starlink
    sx0 = ox + pad
    box(sx0, chain_y, sx0 + 220, chain_y + ch, (150, 100, 240))
    ctext(sx0 + 110, chain_y + 16, "STARLINK", f_box)
    # Rancho
    rx0 = sx0 + 300
    _rancho_st = ROUTER_BY_LINK.get("backbone", (None, "ativo", None))[1]
    box(rx0, chain_y, rx0 + 240, chain_y + ch, C_OBRA if _rancho_st == "obra" else C_ATIVO)
    ctext(rx0 + 120, chain_y + 16, "Roteador RANCHO", _f("DejaVuSans-Bold.ttf", 19))
    # CTO
    cx0 = rx0 + 340
    box(cx0, chain_y - 6, cx0 + 430, chain_y + ch + 6, (0, 190, 110), fill=(14, 60, 40), wd=4)
    ctext(cx0 + 215, chain_y + 4, "CAIXA CTO — poste P9", f_box)
    ctext(cx0 + 215, chain_y + 32, "switch 8 fibra + 2 RJ45", f_sm, MUTE)

    bb = ROUTE_BY_KEY["backbone"]["rgb"]
    def arrow(x0, x1, y, color, wd=7):
        d.line([(x0, y), (x1, y)], fill=color, width=wd)
        d.polygon([(x1, y), (x1 - 14, y - 8), (x1 - 14, y + 8)], fill=color)
    arrow(sx0 + 220, rx0, chain_y + ch / 2, bb)
    arrow(rx0 + 240, cx0, chain_y + ch / 2, bb)
    ctext((rx0 + 240 + cx0) / 2, chain_y - 22, "conversor A", f_sm, INK)
    ctext((rx0 + 240 + cx0) / 2, chain_y - 4, "+ fibra", f_sm, MUTE)

    # barramento de distribuicao
    bus_y = oy + 210
    cto_cx = cx0 + 215
    d.line([(cto_cx, chain_y + ch + 6), (cto_cx, bus_y)], fill=MUTE, width=4)
    d.line([(col_cx[0], bus_y), (col_cx[-1], bus_y)], fill=MUTE, width=4)
    d.ellipse([cto_cx - 5, bus_y - 5, cto_cx + 5, bus_y + 5], fill=MUTE)

    node_y = bus_y + 90
    box_h = 74
    for i, key in enumerate(COLS):
        rt = ROUTE_BY_KEY[key]
        col = rt["rgb"]
        cx = col_cx[i]
        txt, status, local = ROUTER_BY_LINK[key]
        # conector colorido
        dash = rt.get("dash")
        if dash:
            yy = bus_y
            while yy < node_y:
                d.line([(cx, yy), (cx, min(yy + 10, node_y))], fill=col, width=6)
                yy += 18
        else:
            d.line([(cx, bus_y), (cx, node_y)], fill=(0, 0, 0), width=rt["w"] + 4)
            d.line([(cx, bus_y), (cx, node_y)], fill=col, width=rt["w"] + 1)
        d.ellipse([cx - 6, bus_y - 6, cx + 6, bus_y + 6], fill=col, outline=INK, width=2)

        bw = min(col_w - 16, 230)
        bcol = C_OBRA if status == "obra" else C_ATIVO
        box(cx - bw / 2, node_y, cx + bw / 2, node_y + box_h, bcol, wd=3)
        e = LINK_EQUIP[key]
        ctext(cx, node_y + 5, "Roteador " + txt, f_sm)
        ctext(cx, node_y + 26, "Mercusys MR60X", f_via, MUTE)
        pinfo = ("RJ45-1 do switch" if key == "rj45"
                 else "conversor de mídia + porta do switch" if e["porta"] == "?"
                 else f"conversor tipo {e['conv_tipo']} · porta {e['porta']}")
        ctext(cx, node_y + 45, pinfo, f_via, (140, 200, 255))

        # chip da cor + nome da ligacao
        chip_y = node_y + box_h + 12
        d.rounded_rectangle([cx - bw / 2, chip_y, cx - bw / 2 + 26, chip_y + 16], radius=3, fill=col)
        d.text((cx - bw / 2 + 34, chip_y - 2), rt["nome"].replace("Ligação ", "").replace("Backbone ", "BB "),
               font=f_via, fill=INK)

        # via (quebrado)
        for j, ln in enumerate(_wrap(d, "via " + rt["via"].split("→", 1)[-1].strip(), f_via, bw + 20)):
            ctext(cx, chip_y + 24 + j * 18, ln, f_via, MUTE)

        status_txt = "em operação" if status == "ativo" else "EM CONSTRUÇÃO"
        ctext(cx, node_y - 24, status_txt, f_via, bcol)

    # chave de status
    ky = oy + h - 42
    tem_obra = any(s == "obra" for (_p, _t, s, _l, _lo) in ROUTERS)
    d.rounded_rectangle([ox + pad, ky, ox + pad + 30, ky + 18], radius=4, outline=C_ATIVO, width=3)
    d.text((ox + pad + 40, ky - 1), "roteador em operação", font=f_key, fill=INK)
    xk = ox + pad + 320
    if tem_obra:
        d.rounded_rectangle([xk, ky, xk + 30, ky + 18], radius=4, outline=C_OBRA, width=3)
        d.text((xk + 40, ky - 1), "roteador em construção", font=f_key, fill=INK)
        xk += 380
    d.text((xk, ky - 1), "tracejado = cabo RJ45 (sem fibra)", font=f_key, fill=MUTE)


if __name__ == "__main__":
    W, H = 2560, 720
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    draw_schematic(d, 0, 0, W, H)
    from paths import img
    out = img("fibra_esquema.png")
    im.save(out, quality=95)
    print("salvo:", out, im.size)
