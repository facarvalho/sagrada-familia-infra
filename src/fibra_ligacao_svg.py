#!/usr/bin/env python3
"""Versao SVG (vetorial) do diagrama de ligacao do switch de fibra 8SC2E.

Mesmo conteudo do painel 'DIAGRAMA DE LIGACAO' de fibra_equipamentos.py, mas em SVG
para dar zoom no celular sem perder qualidade.  Gera docs/img/fibra_ligacao.svg e
expoe build_svg() -> string, usada inline por gen_html.py.
"""
from fibra_dados import (PORTAS, RJ45_1, ROTEADORES_A_DISTRIBUIR, ROUTE_BY_KEY,
                         ROUTERS, EQUIP, rgb_hex)

INK, MUTE = "#eef2fa", "#a6b4c8"
OK, WARN = "#3cc878", "#ffb642"
TA, TB = "#5696eb", "#f0a546"
PANEL, PCB, PCB_E = "#1b2440", "#14467a", "#4286cd"
BG = "#0f1420"

_COR = {t: rgb_hex(ROUTE_BY_KEY[l]["rgb"]) for _p, t, _s, l, _lo in ROUTERS}

ROW_ORDER = [8, 7, 6, 5, 4, 3, 2, 1]           # tipo B (5-8) em cima, tipo A (1-4) em baixo

W = 1200
X_SW0, X_SW1 = 44, 330
X_CONV0, CONV_W = 556, 208
X_RT = X_CONV0 + CONV_W + 56
RT_W = W - X_RT - 24
SW_Y0 = 160                 # topo do switch (deixa o cabeçalho + caixa do Roteador CTO acima)
STEP = 116
Y0 = SW_Y0 + 70            # 1ª porta SC
CTO_Y = 100                # caixa "Roteador CTO" (RJ45-1), abaixo do subtítulo


def _esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def build_svg():
    rows_y = [Y0 + i * STEP for i in range(8)]
    sw_y0, sw_y1 = SW_Y0, rows_y[-1] + 78
    H = sw_y1 + 250
    o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
             f'font-family="system-ui,Segoe UI,Roboto,sans-serif" width="100%">')
    o.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="{BG}"/>')
    o.append(f'<text x="28" y="40" fill="{INK}" font-size="30" font-weight="700">'
             f'Ligação do switch de fibra 8SC2E</text>')
    o.append(f'<text x="28" y="68" fill="{MUTE}" font-size="15">'
             f'cada porta SC → 1 conversor de mídia → 1 cabo RJ45 → 1 roteador Mercusys MR60X'
             f'  ·  Caixa CTO (poste P9)</text>')

    # ---- Roteador CTO (RJ45-1), acima de tudo
    o.append(f'<path d="M {X_SW0+70} {sw_y0} V {CTO_Y+23} H {X_RT}" '
             f'fill="none" stroke="#98a2b3" stroke-width="3"/>')
    o.append(f'<rect x="{X_RT}" y="{CTO_Y}" width="{RT_W}" height="46" rx="8" '
             f'fill="#10331e" stroke="{OK}" stroke-width="3"/>')
    o.append(f'<rect x="{X_RT+12}" y="{CTO_Y+14}" width="26" height="18" rx="3" fill="#ffffff"/>')
    o.append(f'<text x="{X_RT+48}" y="{CTO_Y+29}" fill="{INK}" font-size="15" font-weight="700">'
             f'Roteador CTO · poste P9 · RJ45-1 (sem fibra) ✔</text>')

    # ---- corpo do switch
    o.append(f'<rect x="{X_SW0}" y="{sw_y0}" width="{X_SW1-X_SW0}" height="{sw_y1-sw_y0}" rx="14" '
             f'fill="{PCB}" stroke="{PCB_E}" stroke-width="3"/>')
    o.append(f'<text x="{(X_SW0+X_SW1)/2}" y="{sw_y0+34}" fill="#cde2fa" font-size="21" '
             f'font-weight="700" text-anchor="middle">SWITCH 8SC2E</text>')
    for j in range(2):
        yy = sw_y0 + 66 + j * 46
        o.append(f'<rect x="{X_SW0+22}" y="{yy}" width="44" height="30" rx="4" '
                 f'fill="#1c1c20" stroke="#a0a6b2" stroke-width="2"/>')
        o.append(f'<rect x="{X_SW0+30}" y="{yy+7}" width="28" height="16" fill="#cdaf3c"/>')
        lbl = "RJ45-1" if j == 0 else "RJ45-2 (reserva)"
        col = "#96c8ff" if j == 0 else MUTE
        o.append(f'<text x="{X_SW0+74}" y="{yy+20}" fill="{col}" font-size="14" '
                 f'font-weight="{700 if j==0 else 400}">{lbl}</text>')
    o.append(f'<rect x="{X_SW0+22}" y="{sw_y1-56}" width="34" height="34" rx="5" '
             f'fill="#141418" stroke="#969ca8" stroke-width="2"/>')
    o.append(f'<text x="{X_SW0+64}" y="{sw_y1-34}" fill="#96c8ff" font-size="14" '
             f'font-weight="700">POWER 12 V / 2 A</text>')

    # ---- 8 portas SC -> conversor -> roteador
    for k, p in enumerate(ROW_ORDER):
        info = PORTAS[p - 1]
        py = rows_y[k]
        tp, ct, conf, nome = info["tipo"], info["conv_tipo"], info["conf"], info["roteador"]
        tcol = TA if tp == "A" else TB
        line = OK if conf else "#98a2b3"
        # gaiola SC + numero
        o.append(f'<polygon points="{X_SW1},{py-20} {X_SW1},{py+20} {X_SW1+46},{py+14} '
                 f'{X_SW1+46},{py-14}" fill="#1a1a1e" stroke="#aab0bc" stroke-width="2"/>')
        o.append(f'<circle cx="{X_SW1-19}" cy="{py}" r="16" fill="{PCB}" stroke="{INK}" stroke-width="2"/>')
        o.append(f'<text x="{X_SW1-19}" y="{py+6}" fill="{INK}" font-size="19" font-weight="700" '
                 f'text-anchor="middle">{p}</text>')
        o.append(f'<rect x="{X_SW1+52}" y="{py-15}" width="52" height="30" rx="4" fill="{tcol}"/>')
        o.append(f'<text x="{X_SW1+78}" y="{py+5}" fill="#0c1018" font-size="14" font-weight="700" '
                 f'text-anchor="middle">SC {tp}</text>')
        # porta -> conversor
        o.append(f'<line x1="{X_SW1+104}" y1="{py}" x2="{X_CONV0}" y2="{py}" '
                 f'stroke="{line}" stroke-width="{4 if conf else 3}"/>')
        # conversor
        o.append(f'<rect x="{X_CONV0}" y="{py-34}" width="{CONV_W}" height="68" rx="8" '
                 f'fill="#787c82" stroke="{OK if conf else "#5f6470"}" stroke-width="{3 if conf else 2}"/>')
        o.append(f'<rect x="{X_CONV0+8}" y="{py-28}" width="{CONV_W-16}" height="8" fill="#eb7828"/>')
        o.append(f'<text x="{X_CONV0+14}" y="{py-6}" fill="#16161a" font-size="12">Conversor de mídia</text>')
        o.append(f'<rect x="{X_CONV0+12}" y="{py+4}" width="86" height="26" rx="5" '
                 f'fill="{TA if ct=="A" else TB}"/>')
        o.append(f'<text x="{X_CONV0+55}" y="{py+22}" fill="#0c1018" font-size="16" font-weight="700" '
                 f'text-anchor="middle">tipo {ct}</text>')
        # conversor -> roteador
        o.append(f'<line x1="{X_CONV0+CONV_W}" y1="{py}" x2="{X_RT}" y2="{py}" '
                 f'stroke="{line}" stroke-width="3"/>')
        # roteador
        if conf:
            rgb = _COR.get(nome, "#ffd000")
            o.append(f'<rect x="{X_RT}" y="{py-30}" width="{RT_W}" height="60" rx="8" '
                     f'fill="#10331e" stroke="{OK}" stroke-width="3"/>')
            o.append(f'<rect x="{X_RT+12}" y="{py-10}" width="28" height="18" rx="3" fill="{rgb}"/>')
            o.append(f'<text x="{X_RT+50}" y="{py-4}" fill="{INK}" font-size="17" font-weight="700">'
                     f'Roteador {_esc(nome)} ✔</text>')
            o.append(f'<text x="{X_RT+50}" y="{py+18}" fill="{MUTE}" font-size="13">'
                     f'Mercusys MR60X · head-end (Starlink)</text>')
        else:
            o.append(f'<rect x="{X_RT}" y="{py-30}" width="{RT_W}" height="60" rx="8" '
                     f'fill="#262014" stroke="{WARN}" stroke-width="2"/>')
            o.append(f'<text x="{X_RT+18}" y="{py-4}" fill="{WARN}" font-size="17" font-weight="700">'
                     f'Roteador ?</text>')
            o.append(f'<text x="{X_RT+18}" y="{py+18}" fill="{MUTE}" font-size="13">'
                     f'Mercusys MR60X — definir o nome do roteador</text>')

    # ---- notas de rodape
    ny = sw_y1 + 40
    notas = [
        (MUTE, "Portas tipo B (5–8) em cima, tipo A (1–4) em baixo — conforme serigrafia 'SC A' / 'SC B' da placa."),
        (INK,  "Conversor SEMPRE do tipo oposto ao da porta (já preenchido). Falta só o NOME do roteador de cada porta:"),
        (WARN, "roteadores a distribuir →  " + "   ·   ".join(ROTEADORES_A_DISTRIBUIR)),
        (OK,   "Confirmado:  porta 5 (SC B) → conversor tipo A → Roteador RANCHO (recebe o Starlink).  RJ45-1 → Roteador CTO."),
    ]
    for i, (col, txt) in enumerate(notas):
        o.append(f'<text x="28" y="{ny + i*30}" fill="{col}" font-size="15" '
                 f'font-weight="{700 if col in (INK, WARN) else 400}">{_esc(txt)}</text>')

    o.append('</svg>')
    return "\n".join(o)


if __name__ == "__main__":
    from paths import img
    out = img("fibra_ligacao.svg")
    open(out, "w").write(build_svg())
    print("salvo:", out)
