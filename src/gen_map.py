#!/usr/bin/env python3
"""Mapa da rede de fibra optica sobre satelite (Google Maps), com uma cor por ligacao
e o esquema da rede embaixo."""
import math, io, os, sys
import requests
from PIL import Image, ImageDraw, ImageFont, ImageStat
from fibra_dados import (POSTES, NAMED, ALL, ROUTES, ROUTE_BY_KEY, ROUTERS,
                         CTO_POINT, STARLINK_POINT, rgb_hex, map_points,
                         camera_list, CAMERA_MODEL_COUNT)
from fibra_esquema import draw_schematic

from paths import img
OUT = img("fibra_infra.png")

# ---------------------------------------------------------------- tiles
TILE = 256
def deg2num(lon, lat, z):
    lat_r = math.radians(lat); n = 2 ** z
    return ((lon + 180.0) / 360.0 * n,
            (1.0 - math.asinh(math.tan(lat_r)) / math.pi) / 2.0 * n)

GMAP_SRV = ["mt0", "mt1", "mt2", "mt3"]
def fetch_tile(z, x, y):
    srv = GMAP_SRV[(x + y) % 4]
    url = f"https://{srv}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
    r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    im = Image.open(io.BytesIO(r.content)).convert("RGB")
    if max(ImageStat.Stat(im).stddev) < 8:
        raise ValueError("placeholder tile")
    return im

# bounding box
pts_all = [p for r in ROUTES for p in (ALL[n] for n in r["nodes"])]
min_lon = min(p[0] for p in pts_all); max_lon = max(p[0] for p in pts_all)
min_lat = min(p[1] for p in pts_all); max_lat = max(p[1] for p in pts_all)
pad_lon = (max_lon - min_lon) * 0.16 + 0.00022
pad_lat = (max_lat - min_lat) * 0.12 + 0.00022
min_lon -= pad_lon; max_lon += pad_lon
min_lat -= pad_lat; max_lat += pad_lat

def build_base(z):
    x0f, y0f = deg2num(min_lon, max_lat, z)
    x1f, y1f = deg2num(max_lon, min_lat, z)
    x0, y0 = math.floor(x0f), math.floor(y0f)
    x1, y1 = math.ceil(x1f), math.ceil(y1f)
    canvas = Image.new("RGB", ((x1 - x0) * TILE, (y1 - y0) * TILE))
    ok = 0
    for tx in range(x0, x1):
        for ty in range(y0, y1):
            try:
                canvas.paste(fetch_tile(z, tx, ty), ((tx - x0) * TILE, (ty - y0) * TILE))
                ok += 1
            except Exception as e:
                print("tile fail", z, tx, ty, e)
    px0 = (x0f - x0) * TILE; py0 = (y0f - y0) * TILE
    img = canvas.crop((int(px0), int(py0),
                       int(px0 + (x1f - x0f) * TILE), int(py0 + (y1f - y0f) * TILE)))
    return img, z, ok

img, ZOOM = None, 19
for z in (19, 20, 18):
    cand, cz, ok = build_base(z)
    print(f"zoom {z}: {cand.size} tiles_ok={ok}")
    if ok >= 4:
        img, ZOOM = cand, cz
        break
if img is None:
    sys.exit("sem tiles")

SCALE = 2 if ZOOM >= 19 else 3
img = img.resize((img.size[0] * SCALE, img.size[1] * SCALE), Image.LANCZOS)
W, Hm = img.size

x0f, y0f = deg2num(min_lon, max_lat, ZOOM)
def to_px(lon, lat):
    xf, yf = deg2num(lon, lat, ZOOM)
    return ((xf - x0f) * TILE * SCALE, (yf - y0f) * TILE * SCALE)

# ---------------------------------------------------------------- linhas paralelas
overlay = Image.new("RGBA", (W, Hm), (0, 0, 0, 0))
d = ImageDraw.Draw(overlay)

def ekey(a, b):
    ra = (round(a[0], 8), round(a[1], 8)); rb = (round(b[0], 8), round(b[1], 8))
    return tuple(sorted([ra, rb]))

edge_users = {}
for ri, rt in enumerate(ROUTES):
    ns = rt["nodes"]
    if len(ns) < 2 or ns[0] == ns[1]:
        continue
    for a, b in zip(ns, ns[1:]):
        edge_users.setdefault(ekey(ALL[a], ALL[b]), []).append(ri)

SPACING = 6.0
def offset_polyline(rt, ri):
    ns = rt["nodes"]; n = len(ns); out = []
    for i in range(n):
        a, b = (ALL[ns[i]], ALL[ns[i + 1]]) if i < n - 1 else (ALL[ns[i - 1]], ALL[ns[i]])
        users = edge_users[ekey(a, b)]
        cnt = len(users); slot = users.index(ri)
        off = (slot - (cnt - 1) / 2.0) * SPACING
        ax, ay = to_px(*a); bx, by = to_px(*b)
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy) or 1.0
        pxn, pyn = -dy / L, dx / L
        x, y = to_px(*ALL[ns[i]])
        out.append((x + pxn * off, y + pyn * off))
    return out

def draw_dashed(poly, color, wd, dash=(11, 9)):
    for a, b in zip(poly, poly[1:]):
        seg = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
        ux, uy = (b[0] - a[0]) / seg, (b[1] - a[1]) / seg
        pos = 0.0
        while pos < seg:
            s, e = pos, min(pos + dash[0], seg)
            d.line([(a[0] + ux * s, a[1] + uy * s), (a[0] + ux * e, a[1] + uy * e)], fill=color, width=wd)
            pos += dash[0] + dash[1]

polys = []
for ri, rt in enumerate(ROUTES):
    ns = rt["nodes"]
    if len(ns) < 2 or ns[0] == ns[1]:
        polys.append(None); continue
    polys.append(offset_polyline(rt, ri))

# halos (finos, só p/ contraste — sem virar bloco preto nos feixes)
for ri, rt in enumerate(ROUTES):
    if polys[ri] is None:
        continue
    d.line(polys[ri], fill=(0, 0, 0, 170), width=rt["w"] + 2, joint="curve")
# cores (backbone por ultimo, mais grosso)
for ri, rt in sorted(enumerate(ROUTES), key=lambda t: t[1]["key"] == "backbone"):
    if polys[ri] is None:
        continue
    col = rt["rgb"] + (255,)
    if rt.get("dash"):
        draw_dashed(polys[ri], col, rt["w"])
    else:
        d.line(polys[ri], fill=col, width=rt["w"], joint="curve")

# ---------------------------------------------------------------- marcadores
FD = "/usr/share/fonts/truetype/dejavu/"
def font(nm, s):
    return ImageFont.truetype(FD + nm, s)
f_sub  = font("DejaVuSans.ttf", 20)
f_leg  = font("DejaVuSans.ttf", 21)
f_lbl  = font("DejaVuSans-Bold.ttf", 21)
f_pole = font("DejaVuSans-Bold.ttf", 16)
f_title = font("DejaVuSans-Bold.ttf", 34)

def dot(p, r, fill, outline=(255, 255, 255, 255), ow=2):
    x, y = to_px(*p)
    d.ellipse([x - r, y - r, x + r, y + r], fill=fill, outline=outline, width=ow)

def label(p, text, dx, dy, fnt, fg=(255, 255, 255), bg=(0, 0, 0, 190)):
    x, y = to_px(*p); x += dx; y += dy
    bb = d.textbbox((0, 0), text, font=fnt)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    d.rounded_rectangle([x - 5, y - 5, x + w + 5, y + h + 5], radius=5, fill=bg)
    d.text((x - bb[0], y - bb[1]), text, font=fnt, fill=fg)

f_badge = font("DejaVuSans-Bold.ttf", 17)
C_ATIVO = (35, 130, 255)
C_OBRA = (255, 70, 70)

def ic_pole(cx, cy, s=1.0):
    d.line([(cx, cy - 10 * s), (cx, cy + 10 * s)], fill=(240, 240, 245), width=max(2, int(3 * s)))
    d.line([(cx - 8 * s, cy - 6 * s), (cx + 8 * s, cy - 6 * s)], fill=(240, 240, 245), width=max(2, int(3 * s)))
    d.ellipse([cx - 9 * s, cy - 9 * s, cx - 5 * s, cy - 5 * s], fill=(210, 210, 215))
    d.ellipse([cx + 5 * s, cy - 9 * s, cx + 9 * s, cy - 5 * s], fill=(210, 210, 215))

def ic_cto(cx, cy, s=1.0):
    # caixa CTO (armario de fibra): corpo verde + porta + dobradiças + espiral de fibra
    d.rounded_rectangle([cx - 10 * s, cy - 11 * s, cx + 10 * s, cy + 11 * s], radius=3,
                        fill=(0, 175, 100, 255), outline=(255, 255, 255, 255), width=2)
    d.line([(cx + 3 * s, cy - 11 * s), (cx + 3 * s, cy + 11 * s)], fill=(255, 255, 255, 255), width=2)  # vinco da porta
    d.line([(cx - 10 * s, cy - 5 * s), (cx - 7 * s, cy - 5 * s)], fill=(255, 255, 255, 255), width=2)   # dobradiça
    d.line([(cx - 10 * s, cy + 5 * s), (cx - 7 * s, cy + 5 * s)], fill=(255, 255, 255, 255), width=2)
    d.arc([cx - 6 * s, cy - 6 * s, cx + 1 * s, cy + 6 * s], 20, 320, fill=(255, 255, 255, 255), width=2)  # fibra

def ic_router(cx, cy, color, s=1.0):
    for ax in (-6, -2, 2, 6):
        d.line([(cx + ax * s, cy - 2 * s), (cx + ax * s * 1.5, cy - 11 * s)], fill=color + (255,), width=2)
    d.polygon([(cx, cy - 4 * s), (cx + 10 * s, cy + 3 * s), (cx, cy + 10 * s), (cx - 10 * s, cy + 3 * s)],
              fill=(28, 28, 34, 255), outline=color + (255,), width=2)

C_CAM = (95, 220, 255)

def ic_cam(cx, cy, s=1.0, color=C_CAM):
    """Camera de seguranca (corpo + lente + 'ondas' Wi-Fi)."""
    d.rounded_rectangle([cx - 9 * s, cy - 6 * s, cx + 6 * s, cy + 6 * s], radius=2,
                        fill=(20, 26, 38, 255), outline=color + (255,), width=2)
    d.ellipse([cx - 4 * s, cy - 3.5 * s, cx + 3 * s, cy + 3.5 * s], outline=color + (255,), width=2)
    d.line([(cx + 6 * s, cy - 4 * s), (cx + 11 * s, cy - 7 * s)], fill=color + (255,), width=2)
    d.line([(cx + 6 * s, cy + 4 * s), (cx + 11 * s, cy + 7 * s)], fill=color + (255,), width=2)
    d.arc([cx + 6 * s, cy - 10 * s, cx + 18 * s, cy + 10 * s], -50, 50, fill=color + (200,), width=2)

def cam_marker(lon, lat, big, dx=0, dy=0):
    x, y = to_px(lon, lat)
    x += dx; y += dy
    s = 1.35 if big else 1.05
    if dx or dy:                       # ligacao ate o ponto real
        px, py = to_px(lon, lat)
        d.line([(px, py), (x, y)], fill=(0, 0, 0, 150), width=3)
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=C_CAM + (255,), outline=(0, 0, 0, 255))
    d.ellipse([x - 15 * s, y - 15 * s, x + 15 * s, y + 15 * s], fill=(12, 16, 26, 210),
              outline=C_CAM + (255,), width=2)
    ic_cam(x - 1 * s, y, s)

def target(lon, lat, poste, rot, cto, bdx=0, bdy=-54):
    x, y = to_px(lon, lat)
    rc = tuple(rot["rgb"]) if rot else (255, 255, 255)
    # reticula
    d.ellipse([x - 13, y - 13, x + 13, y + 13], outline=(0, 0, 0, 210), width=5)
    d.ellipse([x - 13, y - 13, x + 13, y + 13], outline=rc + (255,), width=3)
    for ex, ey in ((0, -1), (0, 1), (-1, 0), (1, 0)):
        d.line([(x + ex * 10, y + ey * 10), (x + ex * 19, y + ey * 19)], fill=rc + (255,), width=3)
    d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=rc + (255,), outline=(0, 0, 0, 255))
    # etiqueta / icones
    icons = []
    if poste:
        icons.append(("pole", None))
    if cto:
        icons.append(("cto", None))
    if rot:
        icons.append(("router", tuple(rot["rgb"])))
    txt = poste or ""
    if rot and not cto:
        txt = f"{poste} · {rot['nome']}" if poste else rot["nome"]
    elif cto:
        txt = f"{poste} · CTO"
    tw = d.textlength(txt, font=f_badge) if txt else 0
    bw = 14 + len(icons) * 22 + (tw + 8 if txt else 0)
    bh = 30
    bx0 = x + bdx - bw / 2
    by0 = y + bdy - bh
    d.line([(x, y - 12), (x + bdx, by0 + bh)], fill=(0, 0, 0, 170), width=3)
    obra = rot and rot["status"] == "obra"
    bg = (150, 25, 25, 235) if obra else (18, 24, 38, 235)
    d.rounded_rectangle([bx0, by0, bx0 + bw, by0 + bh], radius=7, fill=bg, outline=rc + (255,), width=2)
    ix = bx0 + 13
    for kind, col in icons:
        cy = by0 + bh / 2
        if kind == "pole":
            ic_pole(ix, cy)
        elif kind == "cto":
            ic_cto(ix, cy)
        else:
            ic_router(ix, cy, col)
        ix += 22
    if txt:
        d.text((ix - 4, by0 + bh / 2 - 9), txt, font=f_badge, fill=(245, 248, 252))

# deslocamentos p/ evitar sobreposicao nos pontos aglomerados (perto da CTO)
BOFF = {
    "P9": (60, -60), "P8": (36, 40), "P10": (-70, -30), "P11": (-64, 20),
    "P7": (44, -8), "P6": (-58, -20), "P12": (44, 30), "P13": (44, 4),
    "P5": (44, 0), "P4": (44, 0), "P3": (44, 0), "P2": (44, 0), "P1": (40, 34),
    "P14": (44, 30), "P15": (40, 30), "P16": (40, 30), "P17": (40, 30),
    "P18": (44, 6), "P19": (48, -6), "P20": (40, -44),
}
for mp in map_points():
    if mp["poste"] is None:  # nós (rancho/sede/mae/lazer)
        nm = mp["rot"]["nome"]
        off = {"RANCHO": (44, -14), "SEDE": (46, -8), "MÃE": (-96, 40), "LAZER": (64, 10)}.get(nm, (44, 0))
    else:
        off = BOFF.get(mp["poste"], (30, -30))
    target(mp["lon"], mp["lat"], mp["poste"], mp["rot"], mp["cto"], off[0], off[1])

# Starlink
dx0, dy0 = to_px(*STARLINK_POINT)
d.ellipse([dx0 - 13, dy0 - 13, dx0 + 13, dy0 + 13], outline=(0, 0, 0, 210), width=5)
d.ellipse([dx0 - 13, dy0 - 13, dx0 + 13, dy0 + 13], outline=(150, 100, 240, 255), width=3)
d.regular_polygon((dx0, dy0, 8), n_sides=4, fill=(150, 100, 240, 255), outline=(255, 255, 255), width=2)
label(STARLINK_POINT, "STARLINK", -30, 20, f_lbl, bg=(90, 50, 160, 230))
label(CTO_POINT, "CAIXA CTO • switch 8SC2E (8 fibra + 2 RJ45)", 66, -96, f_sub, bg=(0, 120, 65, 240))

# cameras de seguranca (Wi-Fi, fora da fibra) — deslocadas do ponto, no lado
# OPOSTO ao badge de poste/roteador (BOFF), p/ nao encavalar
_CAM_LEFT_BADGE = {"P6", "P10", "P11"}     # badges que saem p/ esquerda (ver BOFF); resto p/ direita
_camn = {}
for c in camera_list(spread_m=9):
    k = c["poste"] or c["local"]
    i = _camn.get(k, 0); _camn[k] = i + 1
    if c["poste"] is None:
        cdx, cdy = 0, 0
    else:
        cdx = 46 if c["poste"] in _CAM_LEFT_BADGE else -46
        cdy = -40 + i * 40
    cam_marker(c["lon"], c["lat"], c["modelo"] == "kapbom", cdx, cdy)

base = Image.alpha_composite(img.convert("RGBA"), overlay)

# ---------------------------------------------------------------- painel do esquema
PANEL_H = 690
canvas = Image.new("RGB", (W, Hm + PANEL_H), (15, 20, 32))
canvas.paste(base.convert("RGB"), (0, 0))
d = ImageDraw.Draw(canvas)

d.rectangle([0, 0, W, 92], fill=(15, 20, 30))
d.text((22, 12), "PROJETO DE INFRAESTRUTURA — REDE DE FIBRA ÓPTICA", font=f_title, fill=(255, 255, 255))
d.text((24, 56), "Fazenda Sagrada Família  •  satélite Google  •  uma cor por ligação  •  postes P1…P20 na sequência da fibra",
       font=f_sub, fill=(205, 214, 228))

# chave de cores compacta (sobre o mapa, canto inf. esquerdo)
def _short(nome):
    return nome.replace("Ligação ", "").replace(" (Starlink → CTO)", "")
keys = [(r["rgb"], _short(r["nome"]), r["via"]) for r in ROUTES]
f_via = font("DejaVuSans.ttf", 15)
lh = 31
kb_h = lh * len(keys) + 20
kb_w = 940
ky = Hm - kb_h - 20
d.rounded_rectangle([18, ky, 18 + kb_w, ky + kb_h], radius=10, fill=(15, 20, 30))
d.text((30, ky + 8), "CORES DAS LIGAÇÕES", font=font("DejaVuSans-Bold.ttf", 16), fill=(180, 192, 210))
for i, (col, nome, via) in enumerate(keys):
    yy = ky + 34 + i * lh
    d.rounded_rectangle([30, yy + 3, 62, yy + 21], radius=4, fill=col)
    d.text((74, yy), nome, font=f_leg, fill=(240, 244, 250))
    d.text((372, yy + 3), via, font=f_via, fill=(172, 184, 202))

# legenda de símbolos (marcador "alvo")
sy_h = 178
sy = ky - sy_h - 14
d.rounded_rectangle([18, sy, 18 + 470, sy + sy_h], radius=10, fill=(15, 20, 30))
d.text((30, sy + 8), "SÍMBOLOS  (marcador no ponto da coordenada)", font=font("DejaVuSans-Bold.ttf", 15), fill=(180, 192, 210))
_si = [
    ("reticula", "ponto exato da coordenada"),
    ("pole", "poste (P1…P20)"),
    ("cto", "caixa CTO — switch 8SC2E"),
    ("router", "roteador Mercusys MR60X"),
    ("cam", f"câmera de segurança Wi-Fi 360°  ({sum(CAMERA_MODEL_COUNT.values())})"),
]
for i, (kind, txt) in enumerate(_si):
    yy = sy + 36 + i * 27
    cxm = 44
    if kind == "reticula":
        d.ellipse([cxm - 9, yy + 2, cxm + 9, yy + 20], outline=(255, 255, 255, 255), width=2)
        d.ellipse([cxm - 2, yy + 9, cxm + 2, yy + 13], fill=(255, 255, 255, 255))
    elif kind == "pole":
        ic_pole(cxm, yy + 11)
    elif kind == "cto":
        ic_cto(cxm, yy + 11)
    elif kind == "cam":
        ic_cam(cxm - 2, yy + 11, 0.95)
    else:
        ic_router(cxm, yy + 11, (120, 180, 255))
    d.text((66, yy + 2), txt, font=f_via, fill=(232, 238, 246))

# barra de escala
m_per_px = (40075016.686 * math.cos(math.radians((min_lat + max_lat) / 2)) / (2 ** ZOOM * TILE)) / SCALE
target_m = 50
bar = target_m / m_per_px
bx, by = W - bar - 40, Hm - 46
d.rectangle([bx - 2, by - 2, bx + bar + 2, by + 12], fill=(15, 20, 30))
d.rectangle([bx, by, bx + bar, by + 8], fill=(255, 255, 255))
d.text((bx, by - 24), f"{target_m} m", font=f_leg, fill=(255, 255, 255))

draw_schematic(d, 0, Hm, W, PANEL_H)

canvas.save(OUT, quality=92)
print("salvo:", OUT, canvas.size)
