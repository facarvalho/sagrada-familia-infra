#!/usr/bin/env python3
"""Gera docs/index.html — pagina inicial navegavel do projeto (GitHub Pages)."""
from fibra_dados import (EQUIP, IP_ROTEADOR, REDE_NOTA, PORTAS, ROTEADORES_A_DISTRIBUIR,
                         ROUTE_BY_KEY, ROUTERS, rgb_hex, camera_list, CAMERA_MODELS,
                         CAMERA_COUNT, CAMERA_MODEL_COUNT, CAMERA_NOTA)
from paths import docs

_LOCAL = {lig: loc for _p, _t, _s, lig, loc in ROUTERS}
NOME = {"backbone": "RANCHO", "porteira": "PORTEIRA", "pomar": "POMAR", "piscina": "PISCINA",
        "motor": "MOTOR", "sede": "SEDE", "mae": "MÃE", "lazer": "LAZER", "rj45": "CTO"}

def _lig_of(nome):
    for _p, txt, _s, lig, _l in ROUTERS:
        if txt == nome:
            return lig
    return None

ip_rows = "".join(
    f"<tr><td>Roteador <b>{n}</b></td><td><code>{ip}</code></td>"
    f"<td>{_LOCAL.get(_lig_of(n), '')}</td></tr>"
    for n, ip in IP_ROTEADOR.items()
)

porta_rows = ""
for p in PORTAS:
    cor = rgb_hex(ROUTE_BY_KEY['backbone']['rgb']) if p['roteador'] == 'RANCHO' else 'transparent'
    rot = f"<b>Roteador {p['roteador']}</b>" if p['conf'] else "<span class='w'>? definir</span>"
    st = "<span class='ok'>✔</span>" if p['conf'] else "<span class='w'>definir</span>"
    porta_rows += (f"<tr><td><b>{p['porta']}</b></td><td>SC {p['tipo']}</td>"
                   f"<td>tipo {p['conv_tipo']}</td><td><i style='background:{cor}'></i></td>"
                   f"<td>{rot}</td><td>{st}</td></tr>")
porta_rows += ("<tr><td><b>RJ45-1</b></td><td>—</td><td>—</td><td><i style='background:#fff'></i></td>"
               "<td><b>Roteador CTO</b> · P9</td><td><span class='ok'>✔</span></td></tr>"
               "<tr><td><b>RJ45-2</b></td><td>—</td><td>—</td><td></td><td>reserva</td><td>—</td></tr>")

cam_rows = ""
for c in camera_list():
    onde = f"poste {c['poste']}" if c["poste"] else f"{c['lat']:.5f}, {c['lon']:.5f}"
    wifi = f"Roteador <b>{c['wifi']}</b>" + (
        f" <span class='w'>{c['wifi_dist_txt']}</span>" if c["wifi_dist_txt"] else "")
    cam_rows += (f"<tr><td><b>{c['local']}</b></td><td>{onde}</td>"
                 f"<td>{c['modelo_nome']}</td><td>{wifi}</td></tr>")
cam_tipos = " · ".join(f"{n}× {CAMERA_MODELS[k]['curto']}" for k, n in CAMERA_MODEL_COUNT.items())

HTML = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Rede de Fibra Óptica — Fazenda Sagrada Família</title>
<style>
  :root{{color-scheme:dark}}
  *{{box-sizing:border-box}}
  body{{margin:0;font-family:system-ui,Segoe UI,Roboto,sans-serif;background:#0f1420;color:#e9eef5;line-height:1.55}}
  .wrap{{max-width:960px;margin:0 auto;padding:24px 16px 60px}}
  h1{{font-size:22px;margin:0 0 4px}}
  h2{{font-size:15px;letter-spacing:.04em;text-transform:uppercase;color:#9fb3cc;margin:34px 0 12px}}
  p.sub{{color:#9fb0c8;margin:0 0 20px;font-size:14px}}
  .cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}}
  a.card{{display:block;background:#182135;border:1px solid #2b3856;border-radius:12px;padding:16px;
    text-decoration:none;color:#e9eef5;transition:border-color .15s}}
  a.card:hover{{border-color:#4f8fe0}}
  a.card .ic{{font-size:24px}}
  a.card b{{display:block;margin:6px 0 2px;font-size:15px}}
  a.card span{{color:#9fb0c8;font-size:13px}}
  table{{border-collapse:collapse;width:100%;font-size:13px;margin-top:4px;overflow:hidden;border-radius:8px}}
  th,td{{padding:7px 9px;text-align:left;border-bottom:1px solid #26324c}}
  th{{background:#1b2740;color:#cdd8ea}}
  tr:nth-child(even) td{{background:#141d30}}
  td i{{display:inline-block;width:16px;height:16px;border-radius:3px;vertical-align:middle}}
  code{{background:#0c1524;padding:1px 6px;border-radius:5px;color:#8fd0ff;font-size:12.5px}}
  .ok{{color:#4bd07f;font-weight:700}} .w{{color:#ffb648;font-weight:700}}
  ul{{margin:6px 0;padding-left:20px}} li{{margin:3px 0}}
  .note{{background:#151f33;border-left:3px solid #ffb648;padding:10px 14px;border-radius:6px;font-size:13px;margin-top:10px}}
  footer{{margin-top:44px;color:#6f7d92;font-size:12px}}
  img.thumb{{width:100%;border-radius:10px;border:1px solid #26324c;margin-top:8px}}
</style>
</head>
<body>
<div class="wrap">
  <h1>Rede de Fibra Óptica — Fazenda Sagrada Família</h1>
  <p class="sub">Projeto de infraestrutura: distribuição de internet por fibra óptica a partir de um link Starlink.</p>

  <div class="cards">
    <a class="card" href="mapa.html"><div class="ic">🗺️</div><b>Mapa interativo</b>
      <span>satélite + traçado da fibra, postes e roteadores. Toque nos marcadores.</span></a>
    <a class="card" href="fibra_infra_projeto.pdf"><div class="ic">📄</div><b>PDF do projeto</b>
      <span>documento completo (7 páginas): mapa, esquema, ligação, tabelas, câmeras.</span></a>
    <a class="card" href="etiquetas_roteadores.pdf"><div class="ic">🏷️</div><b>Etiquetas dos cabos</b>
      <span>folha A4 para imprimir: cor da ligação + nome do roteador + IP.</span></a>
    <a class="card" href="img/fibra_equipamentos.png"><div class="ic">🔌</div><b>Ligação do switch 8SC2E</b>
      <span>portas SC A/B, conversores de mídia e roteadores.</span></a>
    <a class="card" href="img/fibra_esquema.png"><div class="ic">🌐</div><b>Esquema da rede</b>
      <span>topologia: Starlink → CTO → ramais.</span></a>
    <a class="card" href="img/fibra_infra.png"><div class="ic">🛰️</div><b>Mapa (imagem)</b>
      <span>versão estática do mapa para impressão.</span></a>
    <a class="card" href="fibra_infra.kml"><div class="ic">📍</div><b>KML (Google Earth)</b>
      <span>traçado, pontos e câmeras para abrir no Google Earth / My Maps.</span></a>
    <a class="card" href="#cameras"><div class="ic">📷</div><b>Câmeras de segurança</b>
      <span>{CAMERA_COUNT} câmeras Wi-Fi 360° — posição, modelo e roteador.</span></a>
  </div>

  <h2>Caminho da internet</h2>
  <p style="font-size:14px">{REDE_NOTA}</p>

  <h2>Equipamentos</h2>
  <ul>
    <li>{EQUIP['fonte']}</li>
    <li>{EQUIP['roteador']}</li>
    <li>{EQUIP['conversor']}</li>
    <li>{EQUIP['switch']}</li>
  </ul>

  <h2>Endereçamento IP</h2>
  <table><thead><tr><th>Roteador (Mercusys MR60X)</th><th>IP de gerência</th><th>Local</th></tr></thead>
  <tbody>{ip_rows}</tbody></table>
  <p style="font-size:13px;color:#9fb0c8">Cada roteador é independente (NAT/DHCP próprio).</p>

  <h2>Portas do switch 8SC2E (Caixa CTO / poste P9)</h2>
  <table><thead><tr><th>Porta</th><th>Tipo</th><th>Conversor</th><th></th><th>Roteador</th><th>Status</th></tr></thead>
  <tbody>{porta_rows}</tbody></table>
  <div class="note"><b>Pendência:</b> definir o roteador das portas 1–4 e 6–8 —
    {' · '.join(ROTEADORES_A_DISTRIBUIR)}. Confirmado: porta 5 = RANCHO, RJ45-1 = CTO.<br>
    Regra BiDi: porta SC A ↔ conversor tipo B | porta SC B ↔ conversor tipo A.</div>

  <img class="thumb" src="img/fibra_ligacao.png" alt="Diagrama de ligação do switch">

  <h2 id="cameras">Câmeras de segurança</h2>
  <p style="font-size:14px">{CAMERA_COUNT} câmeras Wi-Fi 360° &mdash; {cam_tipos}.</p>
  <table><thead><tr><th>Local</th><th>Poste / coordenada</th><th>Modelo</th><th>Wi-Fi</th></tr></thead>
  <tbody>{cam_rows}</tbody></table>
  <div class="note">{CAMERA_NOTA}</div>

  <footer>Gerado a partir de <code>src/</code> · veja o README para reconstruir.</footer>
</div>
</body>
</html>
"""

open(docs("index.html"), "w").write(HTML)
print("salvo:", docs("index.html"))
