#!/usr/bin/env python3
"""KML da rede de fibra (uma cor por ligacao, postes renumerados). Google Earth / My Maps."""
import os
from fibra_dados import (POSTES, ALL, ROUTES, ROUTERS, LINK_EQUIP, CTO_POINT,
                         STARLINK_POINT, kml_color, camera_list, CAMERA_MODELS)

from paths import docs
OUT = docs("fibra_infra.kml")

def coords(nodes):
    return " ".join(f"{ALL[n][0]},{ALL[n][1]},0" for n in nodes)

x = ['<?xml version="1.0" encoding="UTF-8"?>',
     '<kml xmlns="http://www.opengis.net/kml/2.2"><Document>',
     '<name>Rede de Fibra Optica - Fazenda Sagrada Familia</name>']

for r in ROUTES:
    x.append(f'<Style id="{r["key"]}"><LineStyle><color>{kml_color(r["rgb"])}</color>'
             f'<width>{max(3, r["w"]-1)}</width></LineStyle></Style>')
x.append('<Style id="rot_ativo"><IconStyle><color>ffff8223</color>'
         '<Icon><href>http://maps.google.com/mapfiles/kml/paddle/blu-circle.png</href></Icon></IconStyle></Style>')
x.append('<Style id="rot_obra"><IconStyle><color>ff4646ff</color>'
         '<Icon><href>http://maps.google.com/mapfiles/kml/paddle/red-circle.png</href></Icon></IconStyle></Style>')
x.append('<Style id="cto"><IconStyle><color>ff6ebe00</color><scale>1.3</scale>'
         '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/square.png</href></Icon></IconStyle></Style>')
x.append('<Style id="poste"><IconStyle><scale>0.55</scale>'
         '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon></IconStyle></Style>')
x.append('<Style id="cam_kapbom"><IconStyle><color>ff3cd2ff</color>'
         '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/camera.png</href></Icon></IconStyle></Style>')
x.append('<Style id="cam_e27"><IconStyle><color>ff78dcff</color><scale>0.9</scale>'
         '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/camera.png</href></Icon></IconStyle></Style>')

x.append('<Folder><name>Ligacoes (uma cor cada)</name>')
for r in ROUTES:
    if len(r["nodes"]) < 2 or r["nodes"][0] == r["nodes"][1]:
        x.append(f'<Placemark><name>{r["nome"]}</name><description>{r["via"]}</description>'
                 f'<styleUrl>#{r["key"]}</styleUrl><Point><coordinates>{ALL[r["nodes"][0]][0]},{ALL[r["nodes"][0]][1]},0</coordinates></Point></Placemark>')
        continue
    x.append(f'<Placemark><name>{r["nome"]}</name><description>{r["via"]}</description>'
             f'<styleUrl>#{r["key"]}</styleUrl>'
             f'<LineString><tessellate>1</tessellate><coordinates>{coords(r["nodes"])}</coordinates></LineString></Placemark>')
x.append('</Folder>')

x.append('<Folder><name>Roteadores (Mercusys MR60X)</name>')
for p, txt, status, lig, local in ROUTERS:
    st = "rot_obra" if status == "obra" else "rot_ativo"
    e = LINK_EQUIP[lig]
    porta = f"porta {e['porta']} (tipo {e['porta_tipo']})" if e["conf"] else "porta a definir"
    conv = "conversor tipo A" if lig == "backbone" else ("RJ45 (sem fibra)" if lig == "rj45" else f"conversor tipo {e['conv_tipo']}")
    desc = (f"{local} - {'EM CONSTRUCAO' if status=='obra' else 'em operacao'} - "
            f"ligacao {lig} - {conv} - switch {porta}")
    x.append(f'<Placemark><name>Roteador {txt}</name><description>{desc}</description>'
             f'<styleUrl>#{st}</styleUrl><Point><coordinates>{p[0]},{p[1]},0</coordinates></Point></Placemark>')
x.append('</Folder>')

x.append(f'<Placemark><name>Caixa CTO (poste P9)</name>'
         f'<description>Ponto de distribuicao - switch de fibra 8 portas fibra + 2 portas RJ45</description>'
         f'<styleUrl>#cto</styleUrl><Point><coordinates>{CTO_POINT[0]},{CTO_POINT[1]},0</coordinates></Point></Placemark>')
x.append(f'<Placemark><name>Starlink (origem do sinal)</name><styleUrl>#cto</styleUrl>'
         f'<Point><coordinates>{STARLINK_POINT[0]},{STARLINK_POINT[1]},0</coordinates></Point></Placemark>')

x.append('<Folder><name>Postes (P1..P20 na sequencia da fibra)</name>')
for n, (lon, lat) in POSTES.items():
    x.append(f'<Placemark><name>{n}</name><styleUrl>#poste</styleUrl>'
             f'<Point><coordinates>{lon},{lat},0</coordinates></Point></Placemark>')
x.append('</Folder>')

x.append('<Folder><name>Cameras de seguranca (Wi-Fi 360)</name>')
for c in camera_list():
    onde = f"poste {c['poste']}" if c["poste"] else f"{c['lat']:.6f}, {c['lon']:.6f}"
    wifi = (f"Wi-Fi: Roteador {c['wifi']}"
            + (f" ({c['wifi_dist_txt']}, estimado)" if c["wifi_dist_txt"]
               else "" if c["wifi_fix"] else " (estimado)"))
    desc = f"{CAMERA_MODELS[c['modelo']]['desc']} - {onde} - {wifi}"
    x.append(f'<Placemark><name>Camera {c["local"]}</name><description>{desc}</description>'
             f'<styleUrl>#cam_{c["modelo"]}</styleUrl>'
             f'<Point><coordinates>{c["lon"]},{c["lat"]},0</coordinates></Point></Placemark>')
x.append('</Folder>')

x.append('</Document></kml>')
open(OUT, "w").write("\n".join(x))
print("salvo:", OUT)
