#!/usr/bin/env python3
"""Dados da rede de fibra optica - Fazenda Sagrada Familia.
Modulo sem efeitos colaterais, importado por gen_map / gen_kml / fibra_esquema / etc.

Alem da rede de fibra, este modulo tambem descreve as CAMERAS de seguranca
(Wi-Fi) - posicao, modelo e roteador MR60X mais proximo (associacao Wi-Fi estimada).

Postes RENUMERADOS na sequencia da fibra (head-end -> CTO -> ramal mais longo).
Mapa de-para com o KML original 'coordenadas.kml':
   P1=21  P2=20  P3=19  P4=17  P5=16  P6=14  P7=13  P8=12  P9=11(CTO)
   P10=10 P11=9  P12=8(Piscina)  P13=7  P14=6(Pomar)  P15=5  P16=4
   P17=3  P18=2  P19=1(Porteira)      P20=15(Motor)
"""

# postes: nome -> (lon, lat)
POSTES = {
    "P1":  (-45.98868059349096, -21.35450049562633),
    "P2":  (-45.98885593652164, -21.35436095821785),
    "P3":  (-45.98906166860465, -21.35421232308776),
    "P4":  (-45.98907897701980, -21.35401357589824),
    "P5":  (-45.98904729789601, -21.35375894113647),
    "P6":  (-45.98896743892824, -21.35317869372432),
    "P7":  (-45.98925025525992, -21.35303342324684),
    "P8":  (-45.98963298877072, -21.35284203389719),
    "P9":  (-45.98991992842048, -21.35266884561628),   # CTO
    "P10": (-45.99011160660755, -21.35290960479607),
    "P11": (-45.99031024768407, -21.35317121611656),
    "P12": (-45.99012546615439, -21.35355275854047),   # R. Piscina
    "P13": (-45.98992436609476, -21.35395688669237),
    "P14": (-45.98965962803340, -21.35452129447635),   # R. Pomar
    "P15": (-45.98936247259595, -21.35483242978097),
    "P16": (-45.98908733010949, -21.35514349755645),
    "P17": (-45.98880807467447, -21.35544153390790),
    "P18": (-45.98852066425261, -21.35513071897358),
    "P19": (-45.98825054872155, -21.35483510781873),   # R. Porteira
    "P20": (-45.98892529983523, -21.35264618545030),   # R. Motor
}
NAMED = {
    "starlink": (-45.98857358781736, -21.35440008645269),
    "rancho":   (-45.98851647255972, -21.35428287231589),
    "mae":      (-45.98995021862738, -21.35287304011150),
    "sede":     (-45.98867006307438, -21.35373487196040),
    "lazer":    (-45.98974910941658, -21.35265317092606),
}
ALL = {**POSTES, **NAMED}
def pt(name):
    return ALL[name]
def pth(*names):
    return [ALL[n] for n in names]

# ligacoes (cada uma com sua cor)
#   cor em RGB; ordem da lista = ordem dos "trilhos" paralelos nos trechos compartilhados
ROUTES = [
    dict(key="backbone", nome="Backbone (Starlink → CTO)", rgb=(255, 208, 0), w=8,
         nodes=["starlink", "rancho", "P1","P2","P3","P4","P5","P6","P7","P8","P9"],
         via="Starlink → Rancho → P1·P2·P3·P4·P5·P6·P7·P8 → CTO (P9)"),
    dict(key="porteira", nome="Ligação Porteira", rgb=(255, 59, 48), w=5,
         nodes=["P9","P10","P11","P12","P13","P14","P15","P16","P17","P18","P19"],
         via="CTO (P9) → P10·P11·P12·P13·P14·P15·P16·P17·P18 → P19"),
    dict(key="pomar", nome="Ligação Pomar", rgb=(255, 140, 0), w=5,
         nodes=["P9","P10","P11","P12","P13","P14"],
         via="CTO (P9) → P10·P11·P12·P13 → P14"),
    dict(key="piscina", nome="Ligação Piscina", rgb=(255, 61, 170), w=5,
         nodes=["P9","P10","P11","P12"],
         via="CTO (P9) → P10·P11 → P12"),
    dict(key="motor", nome="Ligação Motor", rgb=(0, 200, 255), w=5,
         nodes=["P9","P8","P7","P6","P20"],
         via="CTO (P9) → P8·P7·P6 → P20"),
    dict(key="sede", nome="Ligação Sede", rgb=(170, 110, 255), w=5,
         nodes=["P9","P8","P7","P6","sede"],
         via="CTO (P9) → P8·P7·P6 → Sede"),
    dict(key="mae", nome="Ligação Mãe", rgb=(40, 220, 110), w=5,
         nodes=["P9","P10","mae"],
         via="CTO (P9) → P10 → Mãe"),
    dict(key="lazer", nome="Ligação Lazer", rgb=(200, 240, 0), w=5,
         nodes=["P9","lazer"],
         via="CTO (P9) → Lazer (direto)"),
    dict(key="rj45", nome="CTO — cabo RJ45", rgb=(255, 255, 255), w=4, dash=True,
         nodes=["P9","P9"],
         via="no próprio poste P9 (cabo RJ45, sem lançamento)"),
]
ROUTE_BY_KEY = {r["key"]: r for r in ROUTES}

# roteadores: (ponto, NOME do local, status, ligacao, local)
#   'nome' e so o local (RANCHO, POMAR...). Para exibir use roteador_label() -> "Roteador RANCHO".
#   status: 'ativo' | 'obra'
ROUTERS = [
    (pt("P19"), "PORTEIRA", "ativo", "porteira", "poste P19"),
    (pt("P14"), "POMAR",    "ativo", "pomar",    "poste P14"),
    (pt("P12"), "PISCINA",  "ativo", "piscina",  "poste P12"),
    (pt("P9"),  "CTO",      "ativo", "rj45",     "poste P9 (na caixa CTO)"),
    (pt("P20"), "MOTOR",    "ativo", "motor",    "poste P20"),
    (pt("mae"),    "MÃE",    "ativo", "mae",      "nó de rede"),
    (pt("sede"),   "SEDE",   "ativo", "sede",     "nó de rede"),
    (pt("rancho"), "RANCHO", "ativo", "backbone", "nó — head-end do Starlink"),
    (pt("lazer"),  "LAZER",  "ativo", "lazer",    "nó de rede"),
]
def roteador_label(nome, curto=False):
    return f"Roteador {nome}" if not curto else nome

CTO_POINT = pt("P9")
STARLINK_POINT = pt("starlink")

# ---------------------------------------------------------------- equipamentos
# Modelos reais usados no projeto
EQUIP = dict(
    switch    = "Switch de fibra 8SC2E — 8×SC 1.25G (placa 4A + 4B) + 2×RJ45 10/100/1000",
    switch_curto = "Switch 8SC2E",
    conversor = "Conversor de mídia Gigabit — 1 SC (fibra) + 1 RJ45 (10/100/1000), plug & play",
    conversor_curto = "Conversor de mídia",
    roteador  = "Roteador Mercusys MR60X — Wi-Fi 6 AX1500 (4 antenas)",
    roteador_curto = "Mercusys MR60X",
    fonte     = "Starlink",
)

# REGRA DE PAREAMENTO (BiDi / WDM) — o conversor entra na porta do TIPO OPOSTO:
#   porta tipo A  <->  conversor tipo B
#   porta tipo B  <->  conversor tipo A
PAREAMENTO = {"A": "B", "B": "A", "?": "?", "—": "—"}
def conv_tipo(porta_tipo):
    return PAREAMENTO.get(porta_tipo, "?")

# Tipo de cada porta SC do switch (placa 4A + 4B), conforme serigrafia "SC A" / "SC B".
PORT_TYPES = {1: "A", 2: "A", 3: "A", 4: "A", 5: "B", 6: "B", 7: "B", 8: "B"}

# Estado de cada porta de fibra do switch.
#   tipo/conv_tipo sao CONHECIDOS (regra A<->B).  So falta o NOME do roteador de cada porta.
#   CONFIRMADO: porta 5 (tipo B) -> conversor tipo A -> Roteador RANCHO (uplink Starlink).
PORTAS = []
for _n in range(1, 9):
    _tp = PORT_TYPES[_n]
    PORTAS.append(dict(porta=_n, tipo=_tp, conv_tipo=conv_tipo(_tp),
                       roteador=("RANCHO" if _n == 5 else "?"),
                       conf=(_n == 5)))
RJ45_1 = dict(porta="RJ45-1", roteador="CTO", nota="patch curto no poste P9 (sem fibra)")
# Roteadores que ainda faltam ser atribuidos a uma porta (todos menos RANCHO e CTO):
ROTEADORES_A_DISTRIBUIR = ["PORTEIRA", "POMAR", "PISCINA", "MOTOR", "SEDE", "MÃE", "LAZER"]

# ---------------------------------------------------------------- rede / IP
# Cada roteador Mercusys MR60X funciona de forma INDEPENDENTE (NAT/DHCP proprio):
# recebe internet na WAN, vinda do roteador CTO, que vem do roteador RANCHO (Starlink).
# Cada roteador tem sua PROPRIA sub-rede /24 (nao ha mais conflito de faixa):
# gateway .1, 3o octeto = numero do roteador. O 192.168.1.0/24 fica sem uso (reserva).
IP_ROTEADOR = {
    "CTO":      "192.168.0.1",
    "MOTOR":    "192.168.2.1",
    "RANCHO":   "192.168.3.1",
    "PORTEIRA": "192.168.4.1",
    "POMAR":    "192.168.5.1",
    "SEDE":     "192.168.6.1",
    "PISCINA":  "192.168.7.1",
    "MÃE":      "192.168.8.1",
    "LAZER":    "192.168.9.1",
}
REDE_NOTA = ("Caminho da internet:  Starlink → Roteador RANCHO → conversor de mídia tipo A → "
             "switch de fibra 8SC2E → 1 conversor de mídia por porta → roteador Mercusys MR60X de cada "
             "local → Wi-Fi (LAN própria).  O switch só faz a ligação da fibra; cada roteador é "
             "independente (NAT/DHCP próprio) e tem sua própria sub-rede 192.168.x.0/24 "
             "(gateway .1). O roteador CTO liga direto no RJ45-1 do switch.")

# Ligacao de fibra -> porta do switch (na Caixa CTO / poste P9).
#   CONFIRMADO pelo cliente: R. Rancho -> conversor tipo A -> 1a porta tipo B (= porta 5).
#   Restante: destino conhecido, PORTA a definir pelo cliente ('vou atualizar').
LINK_EQUIP = {
    "backbone": dict(porta="5", porta_tipo="B", sentido="entra", destino="Roteador RANCHO  (uplink Starlink)", conf=True),
    "porteira": dict(porta="?", porta_tipo="?", sentido="sai",   destino="Roteador PORTEIRA  ·  poste P19",     conf=False),
    "pomar":    dict(porta="?", porta_tipo="?", sentido="sai",   destino="Roteador POMAR  ·  poste P14",        conf=False),
    "piscina":  dict(porta="?", porta_tipo="?", sentido="sai",   destino="Roteador PISCINA  ·  poste P12",      conf=False),
    "motor":    dict(porta="?", porta_tipo="?", sentido="sai",   destino="Roteador MOTOR  ·  poste P20",        conf=False),
    "sede":     dict(porta="?", porta_tipo="?", sentido="sai",   destino="Roteador SEDE",                      conf=False),
    "mae":      dict(porta="?", porta_tipo="?", sentido="sai",   destino="Roteador MÃE",                       conf=False),
    "lazer":    dict(porta="?", porta_tipo="?", sentido="sai",   destino="Roteador LAZER",                     conf=False),
    "rj45":     dict(porta="RJ45-1", porta_tipo="—", sentido="sai", destino="Roteador CTO  ·  mesmo poste P9",  conf=True),
}
for _e in LINK_EQUIP.values():
    _e["conv_tipo"] = conv_tipo(_e["porta_tipo"])
# RJ45-2 do switch: reserva / livre

def rgb_hex(rgb):
    return "#%02x%02x%02x" % rgb


# ---------------------------------------------------------------- cameras de seguranca
import math, re

def dms(s):
    """Converte '21°21\\'15.37\"S' (graus/min/seg) para grau decimal. S e W = negativo."""
    g, m, sec, hemi = re.match(r"\s*(\d+)\D+(\d+)\D+([\d.]+)\D*([NSEW])", s).groups()
    val = float(g) + float(m) / 60.0 + float(sec) / 3600.0
    return -val if hemi in ("S", "W") else val

def dmsll(lat_s, lon_s):
    """Par ('lat DMS', 'lon DMS') -> (lon, lat) decimal, no formato usado aqui."""
    return (dms(lon_s), dms(lat_s))

# Modelos de camera usados no projeto (todas Wi-Fi, 360°).
CAMERA_MODELS = {
    "kapbom": dict(
        nome="Câmera IP Wi-Fi Kapbom 360° 1080p HD",
        curto="Kapbom Wi-Fi 360°",
        desc="Câmera IP para poste · Wi-Fi · 360° · 1080p HD · visão noturna · 3 antenas",
    ),
    "e27": dict(
        nome="Câmera Wi-Fi soquete lâmpada E27 360° HD (branca)",
        curto="Soquete E27 360°",
        desc="Câmera Wi-Fi de soquete de lâmpada E27 · 360° · HD · visão noturna · branca",
    ),
}

# Cada camera: (ponto (lon,lat), local, modelo, poste|None, wifi|None).
#   O poste e so referencia de montagem; a camera liga por Wi-Fi (nao na fibra).
#   wifi=None  -> roteador MR60X mais proximo (cam_wifi); um nome fixa a associacao
#   (usado onde o local ja diz o roteador e a distancia pura enganaria — cluster Mae/CTO/Lazer).
CAMERAS = [
    (pt("P19"), "Porteira",     "kapbom", "P19", None),
    (pt("P1"),  "Galinheiro",   "kapbom", "P1",  None),
    (pt("P17"), "Chuchu",       "e27",    "P17", None),
    (pt("P14"), "Pomar Cima",   "e27",    "P14", None),
    (pt("P14"), "Pomar Baixo",  "e27",    "P14", None),
    (pt("P11"), "Piscina",      "e27",    "P11", None),
    (pt("P9"),  "Mãe Lateral",  "e27",    "P9",  "MÃE"),
    (pt("P8"),  "Mãe Frente",   "e27",    "P8",  "MÃE"),
    (pt("P20"), "Motor",        "e27",    "P20", None),
    (pt("P6"),  "Chiqueiro",    "e27",    "P6",  None),
    (pt("P5"),  "Sede",         "e27",    "P5",  None),
    (dmsll('21°21\'15.37"S', '45°59\'18.42"W'), "Rancho Entrada",  "e27", None, None),
    (dmsll('21°21\'15.77"S', '45°59\'18.83"W'), "Cozinha Entrada", "e27", None, None),
    (dmsll('21°21\'09.96"S', '45°59\'23.65"W'), "Mãe Cozinha",     "e27", None, "MÃE"),
    (dmsll('21°21\'10.39"S', '45°59\'23.50"W'), "Mãe Varanda",     "e27", None, "MÃE"),
    (dmsll('21°21\'09.58"S', '45°59\'23.10"W'), "Lazer Cozinha",   "e27", None, None),
    (dmsll('21°21\'09.32"S', '45°59\'23.19"W'), "Lazer Sala",      "e27", None, None),
]

def _dist_m(a, b):
    lon1, lat1, lon2, lat2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = (math.sin((lat2 - lat1) / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
    return 2 * 6371000 * math.asin(math.sqrt(h))

def cam_wifi(point):
    """(nome, metros) do roteador MR60X mais proximo — associacao Wi-Fi estimada."""
    best, bd = None, float("inf")
    for _p, _nome, *_r in ROUTERS:
        dd = _dist_m(point, _p)
        if dd < bd:
            best, bd = _nome, dd
    return best, round(bd)

def camera_list(spread_m=0.0):
    """Lista de dicts: lon, lat, local, modelo, modelo_nome, poste, wifi, wifi_m, wifi_fix.
    spread_m>0 afasta levemente cameras na mesma coordenada (so p/ marcadores no mapa)."""
    recs = []
    for point, local, modelo, poste, wifi in CAMERAS:
        near, dist = cam_wifi(point)
        # dist_txt: '' quando fixado ou praticamente no mesmo ponto do roteador
        dist_txt = "" if (wifi or dist < 8) else f"~{dist} m"
        recs.append(dict(lon=point[0], lat=point[1], local=local, modelo=modelo,
                         modelo_nome=CAMERA_MODELS[modelo]["curto"], poste=poste,
                         wifi=wifi or near, wifi_m=dist, wifi_fix=bool(wifi),
                         wifi_dist_txt=dist_txt))
    if spread_m:
        groups = {}
        for r in recs:
            groups.setdefault((round(r["lon"], 7), round(r["lat"], 7)), []).append(r)
        for g in groups.values():
            if len(g) < 2:
                continue
            for i, r in enumerate(g):
                ang = 2 * math.pi * i / len(g)
                dlat = spread_m / 111320.0
                r["lat"] += math.cos(ang) * dlat
                r["lon"] += math.sin(ang) * dlat / math.cos(math.radians(r["lat"]))
    return recs

CAMERA_COUNT = len(CAMERAS)
CAMERA_MODEL_COUNT = {k: sum(1 for _c in CAMERAS if _c[2] == k) for k in CAMERA_MODELS}
CAMERA_NOTA = ("Câmeras Wi-Fi 360° — não usam a fibra: cada uma conecta no Wi-Fi do roteador "
               "Mercusys MR60X mais próximo (associação estimada por distância; confirmar o sinal "
               "no local). As de poste usam o modelo Kapbom (externo, 3 antenas); as demais são de "
               "soquete de lâmpada E27.")


# ---------------------------------------------------------------- pontos do mapa
# o que existe em cada coordenada: poste / roteador / cto  (para o marcador "alvo")
_ROT_AT = {(round(_p[0], 8), round(_p[1], 8)): dict(nome=_txt, status=_st, lig=_lig)
           for (_p, _txt, _st, _lig, _loc) in ROUTERS}

def _router_info(r):
    if not r:
        return None
    rgb = ROUTE_BY_KEY[r["lig"]]["rgb"]
    return dict(nome=r["nome"], status=r["status"], lig=r["lig"],
                rgb=list(rgb), cor=rgb_hex(rgb))

def map_points():
    """Lista de dicts: lon, lat, poste(str|None), rot(dict|None), cto(bool)."""
    pts = []
    for name, (lon, lat) in POSTES.items():
        r = _ROT_AT.get((round(lon, 8), round(lat, 8)))
        pts.append(dict(lon=lon, lat=lat, poste=name, rot=_router_info(r), cto=(name == "P9")))
    for key in ("rancho", "sede", "mae", "lazer"):
        lon, lat = NAMED[key]
        r = _ROT_AT.get((round(lon, 8), round(lat, 8)))
        pts.append(dict(lon=lon, lat=lat, poste=None, rot=_router_info(r), cto=False))
    return pts
def kml_color(rgb, alpha=255):
    r, g, b = rgb
    return "%02x%02x%02x%02x" % (alpha, b, g, r)
