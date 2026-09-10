#!/usr/bin/env python3
"""Esquema VERTICAL de ligacao do SWITCH DE FIBRA 8SC2E.
   switch (coluna esquerda) -> 8 portas SC (tipo B em cima / tipo A em baixo)
   -> conversor de midia (tipo CONHECIDO: oposto da porta) -> roteador Mercusys MR60X.
   So falta definir QUAL roteador entra em cada porta.
Gera fibra_equipamentos.png.
"""
import os
from PIL import Image, ImageDraw, ImageFont
from fibra_dados import (PORTAS, RJ45_1, ROTEADORES_A_DISTRIBUIR, ROUTE_BY_KEY,
                         ROUTERS, EQUIP)

FD = "/usr/share/fonts/truetype/dejavu/"
def _f(n, s):
    return ImageFont.truetype(FD + n, s)

BG   = (15, 20, 32)
PANEL = (23, 30, 46)
INK  = (238, 242, 250)
MUTE = (170, 182, 202)
OK   = (60, 200, 120)
WARN = (255, 182, 66)
TA   = (86, 150, 235)
TB   = (240, 165, 70)
PCB  = (20, 70, 122)
PCB_E = (66, 134, 205)

# cor do ramal por nome de roteador
_COR = {}
for _p, _txt, _s, _lig, _loc in ROUTERS:
    _COR[_txt] = ROUTE_BY_KEY[_lig]["rgb"]
_LOCAL = {_txt: _loc for _p, _txt, _s, _lig, _loc in ROUTERS}

# ordem de cima p/ baixo: portas tipo B (5-8) em cima, tipo A (1-4) em baixo
ROW_ORDER = [8, 7, 6, 5, 4, 3, 2, 1]


def _ct(d, cx, y, t, f, fill=INK):
    d.text((cx - d.textlength(t, font=f) / 2, y), t, font=f, fill=fill)


def build(diagrama_only=False):
    W, H = 1560, (1470 if diagrama_only else 2140)
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    f_h1 = _f("DejaVuSans-Bold.ttf", 30)
    f_h2 = _f("DejaVuSans-Bold.ttf", 21)
    f_tx = _f("DejaVuSans.ttf", 15)
    f_txb = _f("DejaVuSans-Bold.ttf", 15)
    f_p  = _f("DejaVuSans-Bold.ttf", 20)
    f_ab = _f("DejaVuSans-Bold.ttf", 18)

    d.text((28, 16), "LIGAÇÃO DO SWITCH DE FIBRA 8SC2E", font=f_h1, fill=INK)
    d.text((30, 52), EQUIP["switch"] + "   ·   Caixa CTO (poste P9)", font=f_tx, fill=MUTE)

    # ============ painel A
    ax, ay, aw, ah = 34, 84, W - 68, 1330
    d.rounded_rectangle([ax, ay, ax + aw, ay + ah], radius=12, fill=PANEL)
    d.text((ax + 24, ay + 16), "DIAGRAMA DE LIGAÇÃO", font=f_h2, fill=INK)
    d.text((ax + 24, ay + 46), "cada porta SC → 1 conversor de mídia → 1 cabo RJ45 → 1 roteador Mercusys MR60X.", font=f_tx, fill=MUTE)

    swx0, swy0, swx1 = ax + 40, ay + 96, ax + 320
    swy1 = ay + ah - 150
    convx0 = swx1 + 280
    convw = 200
    rtx = convx0 + convw + 44
    RBW = 470                     # largura das caixas de roteador
    d.rounded_rectangle([swx0, swy0, swx1, swy1], radius=14, fill=PCB, outline=PCB_E, width=3)
    _ct(d, (swx0 + swx1) / 2, swy0 + 12, "SWITCH  8SC2E", f_h2, (205, 226, 250))

    # --- 2x RJ45 dentro do switch, alinhados à ESQUERDA, empilhados na vertical
    rjx = swx0 + 22
    rjy = swy0 + 58
    for j in range(2):
        yy = rjy + j * 54
        d.rounded_rectangle([rjx, yy - 17, rjx + 44, yy + 17], radius=4, fill=(28, 28, 32),
                            outline=(160, 166, 178), width=2)
        d.rectangle([rjx + 7, yy - 10, rjx + 37, yy + 10], fill=(205, 175, 60))
        d.text((rjx + 56, yy - 8), f"RJ45-{j+1}" + ("" if j == 0 else "  (reserva)"),
               font=f_txb if j == 0 else f_tx, fill=(150, 200, 255) if j == 0 else MUTE)
    # RJ45-1 -> Roteador CTO  (sobe pelo topo do jack e vai por cima das portas de fibra)
    topline = swy0 - 6
    d.line([(rjx + 22, rjy - 17), (rjx + 22, topline), (rtx - 6, topline), (rtx - 6, rjy)],
           fill=(150, 160, 178), width=3)
    d.rounded_rectangle([rtx, rjy - 24, rtx + RBW, rjy + 24], radius=8, fill=(16, 44, 30), outline=OK, width=3)
    d.rounded_rectangle([rtx + 12, rjy - 9, rtx + 36, rjy + 9], radius=3, fill=(255, 255, 255))
    d.text((rtx + 46, rjy - 8), "Roteador CTO  ·  poste P9  (RJ45, sem fibra)  ✔", font=f_txb, fill=INK)

    # --- POWER 12V/2A na parte inferior do switch
    d.rounded_rectangle([swx0 + 24, swy1 - 54, swx0 + 56, swy1 - 20], radius=5, fill=(20, 20, 24),
                        outline=(150, 156, 168), width=2)
    d.ellipse([swx0 + 34, swy1 - 45, swx0 + 46, swy1 - 33], fill=(60, 62, 70))
    d.text((swx0 + 66, swy1 - 50), "POWER  12 V / 2 A", font=f_txb, fill=(150, 200, 255))

    # --- 8 portas SC empilhadas (tipo B em cima, tipo A em baixo)
    p_top = swy0 + 190
    p_step = (swy1 - p_top - 70) / 7
    row_y = {p: p_top + k * p_step for k, p in enumerate(ROW_ORDER)}
    for p in ROW_ORDER:
        info = PORTAS[p - 1]
        py = row_y[p]
        tp = info["tipo"]
        ct = info["conv_tipo"]
        tcol = TA if tp == "A" else TB
        conf = info["conf"]
        nome = info["roteador"]
        # gaiola SC
        d.polygon([(swx1, py - 20), (swx1, py + 20), (swx1 + 46, py + 14), (swx1 + 46, py - 14)],
                  fill=(26, 26, 30), outline=(170, 176, 188), width=2)
        d.rectangle([swx1 + 6, py - 12, swx1 + 14, py + 12], fill=(184, 190, 200))
        d.ellipse([swx1 - 34, py - 15, swx1 - 4, py + 15], fill=PCB, outline=INK, width=2)
        _ct(d, swx1 - 19, py - 13, str(p), f_p)
        d.rounded_rectangle([swx1 + 52, py - 15, swx1 + 100, py + 15], radius=4, fill=tcol)
        _ct(d, swx1 + 76, py - 12, f"SC {tp}", f_txb, (12, 16, 24))

        # linha porta -> conversor
        x_from = swx1 + 104
        lc = OK if conf else (150, 160, 178)
        d.line([(x_from, py), (convx0, py)], fill=lc, width=4 if conf else 3)

        # conversor (tipo CONHECIDO)
        d.rounded_rectangle([convx0, py - 34, convx0 + convw, py + 34], radius=8,
                            fill=(120, 124, 130), outline=OK if conf else (95, 100, 112), width=3 if conf else 2)
        d.rectangle([convx0 + 8, py - 28, convx0 + convw - 8, py - 21], fill=(235, 120, 40))
        d.text((convx0 + 12, py - 16), "Conversor de mídia", font=_f("DejaVuSans.ttf", 12), fill=(22, 22, 26))
        d.rounded_rectangle([convx0 + 12, py + 2, convx0 + 96, py + 28], radius=5, fill=(TA if ct == "A" else TB))
        _ct(d, convx0 + 54, py + 4, f"tipo {ct}", f_ab, (12, 16, 24))

        # roteador
        d.line([(convx0 + convw, py), (rtx, py)], fill=lc, width=3)
        if conf:
            rgb = _COR.get(nome, (255, 208, 0))
            d.rounded_rectangle([rtx, py - 30, rtx + RBW, py + 30], radius=8, fill=(16, 44, 30), outline=OK, width=3)
            d.rounded_rectangle([rtx + 12, py - 10, rtx + 38, py + 8], radius=3, fill=rgb)
            d.text((rtx + 48, py - 22), "Roteador " + nome + "  ✔", font=f_ab, fill=INK)
            d.text((rtx + 48, py + 6), "Mercusys MR60X  ·  head-end (Starlink)", font=f_tx, fill=MUTE)
        else:
            d.rounded_rectangle([rtx, py - 30, rtx + RBW, py + 30], radius=8, fill=(38, 32, 20),
                                outline=WARN, width=2)
            d.text((rtx + 18, py - 22), "Roteador  ?", font=f_ab, fill=WARN)
            d.text((rtx + 18, py + 6), "Mercusys MR60X  —  definir o nome do roteador", font=f_tx, fill=MUTE)

    d.text((ax + 24, swy1 + 20),
           "Portas tipo B (5–8) em cima, tipo A (1–4) em baixo — conforme serigrafia 'SC A' / 'SC B' da placa.",
           font=f_tx, fill=MUTE)
    d.text((ax + 24, swy1 + 44),
           "Conversor SEMPRE do tipo oposto ao da porta (já preenchido).  Falta só o NOME do roteador de cada porta:",
           font=f_txb, fill=INK)
    d.text((ax + 24, swy1 + 70),
           "roteadores a distribuir →  " + "   ·   ".join(ROTEADORES_A_DISTRIBUIR),
           font=f_txb, fill=WARN)
    d.text((ax + 24, swy1 + 100),
           "Confirmado:  porta 5 (SC B) → conversor tipo A → Roteador RANCHO (recebe o Starlink).",
           font=f_tx, fill=OK)

    if diagrama_only:
        from paths import img
        out = img("fibra_ligacao.png")
        im.crop((0, 0, W, ay + ah + 20)).save(out, quality=95)
        print("salvo:", out)
        return

    # ============ painel B: regra
    by0 = ay + ah + 20
    d.rounded_rectangle([34, by0, W - 34, by0 + 116], radius=12, fill=PANEL)
    d.text((54, by0 + 12), "REGRA DE PAREAMENTO (BiDi) — o conversor é do TIPO OPOSTO ao da porta", font=f_h2, fill=INK)
    for i, (p_, c_) in enumerate([("A", "B"), ("B", "A")]):
        rx = 54 + i * 470
        d.rounded_rectangle([rx, by0 + 46, rx + 430, by0 + 98], radius=8, fill=(28, 36, 54), outline=(80, 92, 120), width=2)
        d.text((rx + 16, by0 + 60), f"porta SC {p_}", font=f_ab, fill=INK)
        d.text((rx + 180, by0 + 58), "◄──►", font=f_ab, fill=WARN)
        d.text((rx + 260, by0 + 60), f"conversor tipo {c_}", font=f_ab, fill=INK)
    d.text((1010, by0 + 52), "Isso já está no diagrama.", font=f_txb, fill=OK)
    d.text((1010, by0 + 74), "Só o nome do roteador é editável.", font=f_tx, fill=(206, 214, 226))

    # ============ painel C: tabela por PORTA
    ty = by0 + 140
    d.text((28, ty), "TABELA — por porta do switch   (coluna ROTEADOR: o cliente preenche o nome)", font=f_h2, fill=INK)
    ty += 36
    cols = [("PORTA", 130), ("TIPO PORTA", 150), ("CONVERSOR", 180), ("ROTEADOR (Mercusys MR60X)", 430),
            ("COR", 90), ("STATUS", 250)]
    x = 28
    tw = sum(c[1] for c in cols)
    d.rectangle([x, ty, x + tw, ty + 36], fill=(40, 52, 78))
    cx = x
    for name, wd in cols:
        d.text((cx + 10, ty + 9), name, font=f_txb, fill=INK); cx += wd
    ty += 36
    rows = [(str(pi["porta"]), f"SC {pi['tipo']}", f"tipo {pi['conv_tipo']}",
             ("Roteador " + pi["roteador"]) if pi["conf"] else "?  (definir)",
             pi["roteador"] if pi["conf"] else None,
             "CONFIRMADO" if pi["conf"] else "definir roteador") for pi in PORTAS]
    rows.append(("RJ45-1", "—", "— (RJ45)", "Roteador CTO", "CTO", "CONFIRMADO"))
    for idx, (porta, tp, cv, rot, cor_nome, st) in enumerate(rows):
        rh = 46
        d.rectangle([x, ty, x + tw, ty + rh], fill=(28, 36, 54) if idx % 2 == 0 else (23, 30, 46))
        cx = x
        vals = [porta, tp, cv, rot, None, st]
        for (name, wd), v in zip(cols, vals):
            if name == "COR":
                if cor_nome:
                    d.rounded_rectangle([cx + 10, ty + rh / 2 - 9, cx + 40, ty + rh / 2 + 9], radius=4,
                                        fill=_COR.get(cor_nome, (200, 200, 200)))
            elif v is not None:
                col = OK if st == "CONFIRMADO" and name == "STATUS" else \
                      WARN if v in ("definir roteador", "?  (definir)") else INK
                fnt = f_txb if name in ("PORTA", "TIPO PORTA", "CONVERSOR", "STATUS") else f_tx
                d.text((cx + 10, ty + rh / 2 - 8), str(v), font=fnt, fill=col)
            cx += wd
        ty += rh

    ty += 12
    for i, nt in enumerate([
        "O tipo da porta e o tipo do conversor JÁ estão definidos (regra A↔B). Só falta o nome do roteador de cada porta.",
        "Confirmado: porta 5 = Roteador RANCHO.   RJ45-1 = Roteador CTO (poste P9).   RJ45-2 = reserva.",
    ]):
        d.ellipse([32, ty + 5 + i * 24, 40, ty + 13 + i * 24], fill=MUTE)
        d.text((50, ty + i * 24), nt, font=f_tx, fill=(206, 214, 226))

    from paths import img
    out = img("fibra_equipamentos.png")
    im.save(out, quality=95)
    print("salvo:", out, im.size)


if __name__ == "__main__":
    build()
    build(diagrama_only=True)
