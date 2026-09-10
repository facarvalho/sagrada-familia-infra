#!/usr/bin/env python3
"""Gera fibra_infra_projeto.pdf — documento completo do projeto de fibra optica.
Usa as imagens ja geradas (rodar gen_map / fibra_esquema / fibra_equipamentos antes)."""
import os
from PIL import Image, ImageDraw, ImageFont
from fibra_dados import (ROUTES, ROUTE_BY_KEY, ROUTERS, LINK_EQUIP, PORTAS, EQUIP,
                         IP_ROTEADOR, REDE_NOTA, ROTEADORES_A_DISTRIBUIR,
                         camera_list, CAMERA_MODELS, CAMERA_COUNT, CAMERA_MODEL_COUNT,
                         CAMERA_NOTA)

from paths import docs, img as imgpath
FD = "/usr/share/fonts/truetype/dejavu/"
def _f(n, s):
    return ImageFont.truetype(FD + n, s)

PW, PH = 1240, 1754                       # A4 @ ~150 dpi
MARGIN = 70
BG = (255, 255, 255)
INK = (24, 28, 36)
MUTE = (95, 105, 120)
ACCENT = (20, 90, 170)
OKc = (20, 140, 70)
WARNc = (190, 120, 0)

DEPARA = {"P1": 21, "P2": 20, "P3": 19, "P4": 17, "P5": 16, "P6": 14, "P7": 13, "P8": 12,
          "P9": 11, "P10": 10, "P11": 9, "P12": 8, "P13": 7, "P14": 6, "P15": 5, "P16": 4,
          "P17": 3, "P18": 2, "P19": 1, "P20": 15}
NOME = {"backbone": "RANCHO", "porteira": "PORTEIRA", "pomar": "POMAR", "piscina": "PISCINA",
        "motor": "MOTOR", "sede": "SEDE", "mae": "MÃE", "lazer": "LAZER", "rj45": "CTO"}
_LOCAL = {lig: loc for _p, _t, _s, lig, loc in ROUTERS}
_COR = {lig: ROUTE_BY_KEY[lig]["rgb"] for _p, _t, _s, lig, _l in ROUTERS}

pages = []


def new_page(titulo, subtitulo=""):
    im = Image.new("RGB", (PW, PH), BG)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, PW, 96], fill=(17, 24, 38))
    d.text((MARGIN, 22), titulo, font=_f("DejaVuSans-Bold.ttf", 30), fill=(255, 255, 255))
    if subtitulo:
        d.text((MARGIN, 62), subtitulo, font=_f("DejaVuSans.ttf", 16), fill=(200, 210, 225))
    d.text((PW - 300, PH - 40), "Rede de fibra — Fazenda Sagrada Família", font=_f("DejaVuSans.ttf", 12), fill=MUTE)
    return im, d


def place_image(d, im, path, top):
    src = Image.open(path).convert("RGB")
    if src.width > src.height * 1.25:                 # paisagem -> girar
        src = src.rotate(-90, expand=True)
    avail_w = PW - 2 * MARGIN
    avail_h = PH - top - MARGIN
    sc = min(avail_w / src.width, avail_h / src.height)
    w, h = int(src.width * sc), int(src.height * sc)
    src = src.resize((w, h), Image.LANCZOS)
    x = (PW - w) // 2
    im.paste(src, (x, top))
    d.rectangle([x - 1, top - 1, x + w, top + h], outline=(210, 214, 222), width=1)


def para(d, x, y, text, f, fill=INK, lh=26, maxw=PW - 2 * MARGIN):
    words = text.split()
    line = ""
    for w in words:
        t = (line + " " + w).strip()
        if d.textlength(t, font=f) <= maxw:
            line = t
        else:
            d.text((x, y), line, font=f, fill=fill); y += lh; line = w
    if line:
        d.text((x, y), line, font=f, fill=fill); y += lh
    return y


def table(d, x, y, headers, rows, widths, rowh=40, hh=42):
    f_h = _f("DejaVuSans-Bold.ttf", 16)
    f_r = _f("DejaVuSans.ttf", 16)
    tw = sum(widths)
    d.rectangle([x, y, x + tw, y + hh], fill=(38, 52, 78))
    cx = x
    for htxt, w in zip(headers, widths):
        d.text((cx + 10, y + 12), htxt, font=f_h, fill=(255, 255, 255)); cx += w
    y += hh
    for i, row in enumerate(rows):
        d.rectangle([x, y, x + tw, y + rowh], fill=(238, 242, 248) if i % 2 == 0 else (255, 255, 255))
        cx = x
        for cell, w in zip(row, widths):
            if isinstance(cell, tuple) and cell and cell[0] == "swatch":
                d.rounded_rectangle([cx + 10, y + rowh / 2 - 9, cx + 40, y + rowh / 2 + 9], radius=4, fill=cell[1])
            else:
                s = str(cell)
                col = OKc if s in ("confirmado", "CONFIRMADO") else WARNc if s in ("a definir", "definir roteador", "?") else INK
                d.text((cx + 10, y + rowh / 2 - 10), s, font=f_r, fill=col)
            cx += w
        y += rowh
    d.rectangle([x, y - rowh * len(rows) - hh, x + tw, y], outline=(200, 205, 214), width=1)
    return y


# ============ P1 — capa / resumo
im, d = new_page("PROJETO DE INFRAESTRUTURA — REDE DE FIBRA ÓPTICA", "Fazenda Sagrada Família  ·  documento técnico")
y = 150
y = para(d, MARGIN, y, "Rede de distribuição de internet por fibra óptica ligando os pontos da fazenda a partir "
         "de um link Starlink. O sinal entra no Roteador RANCHO, passa por um conversor de mídia (tipo A) e chega "
         "por fibra ao switch 8SC2E na Caixa CTO (poste P9). O switch distribui para 8 conversores de mídia — 1 por "
         "porta — e cada um alimenta o roteador Mercusys MR60X de um local. O roteador CTO liga direto no RJ45-1.",
         _f("DejaVuSans.ttf", 17), lh=27)
y += 20
d.text((MARGIN, y), "EQUIPAMENTOS", font=_f("DejaVuSans-Bold.ttf", 19), fill=ACCENT); y += 34
for k in ("fonte", "roteador", "conversor", "switch"):
    y = para(d, MARGIN + 10, y, "•  " + EQUIP[k], _f("DejaVuSans.ttf", 16), lh=25)
y += 24
d.text((MARGIN, y), "CAMINHO DA INTERNET", font=_f("DejaVuSans-Bold.ttf", 19), fill=ACCENT); y += 34
y = para(d, MARGIN + 10, y, REDE_NOTA, _f("DejaVuSans.ttf", 16), lh=25)
y += 24
d.text((MARGIN, y), "CONTEÚDO", font=_f("DejaVuSans-Bold.ttf", 19), fill=ACCENT); y += 34
for ln in ["2 — Mapa geral (satélite) com o traçado da fibra e os roteadores",
           "3 — Esquema da rede (topologia: Starlink → CTO → ramais)",
           "4 — Ligação do switch de fibra 8SC2E (portas, conversores, roteadores)",
           "5 — Tabelas: endereçamento IP · portas do switch · de-para dos postes",
           "6 — Detalhe por roteador",
           f"7 — Câmeras de segurança ({CAMERA_COUNT} câmeras Wi-Fi 360°)"]:
    y = para(d, MARGIN + 10, y, "•  " + ln, _f("DejaVuSans.ttf", 16), lh=26)
y += 20
d.text((MARGIN, y), "PENDÊNCIA", font=_f("DejaVuSans-Bold.ttf", 19), fill=WARNc); y += 34
y = para(d, MARGIN + 10, y, "Definir em qual porta do switch (1–4 e 6–8) entra o conversor de cada roteador: "
         + ", ".join(ROTEADORES_A_DISTRIBUIR) + ".  Confirmado: porta 5 = RANCHO, RJ45-1 = CTO.",
         _f("DejaVuSans.ttf", 16), lh=25)
pages.append(im)

# ============ P2 — mapa
im, d = new_page("2 · MAPA GERAL", "imagem de satélite Google · uma cor por ligação · postes P1…P20 na sequência da fibra")
place_image(d, im, imgpath("fibra_infra.png"), 120)
pages.append(im)

# ============ P3 — esquema
im, d = new_page("3 · ESQUEMA DA REDE", "topologia lógica: Starlink → Roteador Rancho → Caixa CTO (P9) → ramais")
place_image(d, im, imgpath("fibra_esquema.png"), 120)
pages.append(im)

# ============ P4 — ligacao switch
im, d = new_page("4 · LIGAÇÃO DO SWITCH DE FIBRA 8SC2E", "switch → porta SC → conversor de mídia → roteador Mercusys MR60X")
place_image(d, im, imgpath("fibra_equipamentos.png"), 120)
pages.append(im)

# ============ P5 — tabelas
im, d = new_page("5 · TABELAS", "endereçamento IP · portas do switch · de-para dos postes")
y = 140
d.text((MARGIN, y), "ENDEREÇAMENTO IP  (cada roteador é independente — NAT/DHCP próprio)", font=_f("DejaVuSans-Bold.ttf", 18), fill=ACCENT)
y += 34
ip_rows = [[f"Roteador {n}", ip] for n, ip in IP_ROTEADOR.items()]
y = table(d, MARGIN, y, ["Roteador (Mercusys MR60X)", "IP de gerência / gateway"], ip_rows, [430, 360], rowh=34, hh=38)
y += 40
d.text((MARGIN, y), "PORTAS DO SWITCH 8SC2E (Caixa CTO / poste P9)", font=_f("DejaVuSans-Bold.ttf", 18), fill=ACCENT)
y += 34
prows = []
for pi in PORTAS:
    prows.append([str(pi["porta"]), f"SC {pi['tipo']}", f"tipo {pi['conv_tipo']}",
                  ("Roteador " + pi["roteador"]) if pi["conf"] else "?  (definir)",
                  "confirmado" if pi["conf"] else "definir roteador"])
prows.append(["RJ45-1", "—", "— (RJ45)", "Roteador CTO", "confirmado"])
prows.append(["RJ45-2", "—", "—", "reserva / livre", "—"])
y = table(d, MARGIN, y, ["Porta", "Tipo", "Conversor", "Roteador (MR60X)", "Status"],
          prows, [110, 110, 150, 380, 250], rowh=34, hh=38)
y += 12
y = para(d, MARGIN, y, "Regra BiDi: porta SC A ↔ conversor tipo B  |  porta SC B ↔ conversor tipo A. "
         "O tipo da porta e do conversor já estão definidos; falta só o nome do roteador das portas 1–4 e 6–8.",
         _f("DejaVuSans.ttf", 14), fill=MUTE, lh=20)
pages.append(im)

# ============ P6 — de-para + detalhe por roteador
im, d = new_page("6 · DETALHE POR ROTEADOR  ·  DE-PARA DOS POSTES", "")
y = 140
d.text((MARGIN, y), "DE-PARA DOS POSTES  (novo P1…P20  ↔  numeração do KML original)", font=_f("DejaVuSans-Bold.ttf", 18), fill=ACCENT)
y += 34
items = list(DEPARA.items())
dp_rows = [[f"{items[i][0]} = {items[i][1]}",
            f"{items[i+1][0]} = {items[i+1][1]}" if i + 1 < len(items) else "",
            f"{items[i+2][0]} = {items[i+2][1]}" if i + 2 < len(items) else "",
            f"{items[i+3][0]} = {items[i+3][1]}" if i + 3 < len(items) else ""]
           for i in range(0, len(items), 4)]
y = table(d, MARGIN, y, ["", "", "", ""], dp_rows, [275, 275, 275, 275], rowh=34, hh=10)
y += 44
d.text((MARGIN, y), "ROTEADORES", font=_f("DejaVuSans-Bold.ttf", 18), fill=ACCENT)
y += 34
rt_rows = []
order = ["backbone", "porteira", "pomar", "piscina", "motor", "sede", "mae", "lazer", "rj45"]
for k in order:
    nm = NOME[k]
    e = LINK_EQUIP[k]
    porta = e["porta"] if e["conf"] else "definir"
    rt_rows.append([f"Roteador {nm}", IP_ROTEADOR.get(nm, "—"), _LOCAL.get(k, "—"),
                    ("Backbone" if k == "backbone" else "RJ45" if k == "rj45" else ROUTE_BY_KEY[k]["nome"].replace("Ligação ", "")),
                    str(porta)])
y = table(d, MARGIN, y, ["Roteador", "IP", "Local", "Ligação / ramal", "Porta switch"],
          rt_rows, [230, 170, 240, 230, 160], rowh=36, hh=40)
y += 16
y = para(d, MARGIN, y, "Todos os roteadores em operação. Cada roteador recebe internet na WAN (vinda do CTO) e "
         "serve o Wi-Fi local com sua própria faixa de IP.", _f("DejaVuSans.ttf", 14), fill=MUTE, lh=20)
pages.append(im)

# ============ P7 — cameras de seguranca
im, d = new_page("7 · CÂMERAS DE SEGURANÇA", f"{CAMERA_COUNT} câmeras Wi-Fi 360° · não usam a fibra")
y = 140
tipos = "   ·   ".join(f"{n}× {CAMERA_MODELS[k]['curto']}" for k, n in CAMERA_MODEL_COUNT.items())
d.text((MARGIN, y), "MODELOS", font=_f("DejaVuSans-Bold.ttf", 18), fill=ACCENT); y += 32
for k, n in CAMERA_MODEL_COUNT.items():
    y = para(d, MARGIN + 10, y, f"•  {n}×  {CAMERA_MODELS[k]['desc']}", _f("DejaVuSans.ttf", 15), lh=23)
y += 22
d.text((MARGIN, y), "POSIÇÕES E ASSOCIAÇÃO Wi-Fi", font=_f("DejaVuSans-Bold.ttf", 18), fill=ACCENT); y += 34
cam_rows = []
for c in camera_list():
    onde = f"poste {c['poste']}" if c["poste"] else f"{c['lat']:.5f}, {c['lon']:.5f}"
    wifi = f"Roteador {c['wifi']}" + (f"  ({c['wifi_dist_txt']})" if c["wifi_dist_txt"] else "")
    cam_rows.append([c["local"], onde, c["modelo_nome"], wifi])
y = table(d, MARGIN, y, ["Local", "Poste / coordenada", "Modelo", "Wi-Fi (roteador MR60X)"],
          cam_rows, [230, 270, 250, 350], rowh=34, hh=38)
y += 16
y = para(d, MARGIN, y, CAMERA_NOTA, _f("DejaVuSans.ttf", 14), fill=MUTE, lh=20)
pages.append(im)

# ---- salvar
out = docs("fibra_infra_projeto.pdf")
pages[0].save(out, save_all=True, append_images=pages[1:], resolution=150.0)
print("salvo:", out, f"({len(pages)} páginas)")
