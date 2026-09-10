#!/usr/bin/env python3
"""Mapa interativo (Leaflet + satelite Google): uma cor por ligacao, marcador "alvo"
com icone de poste / CTO / roteador MR60X, tabela porta<->conversor, tabela de IPs
e o diagrama de ligacao do switch."""
import json, os, base64
from urllib.parse import quote
from fibra_dados import (POSTES, ALL, ROUTES, ROUTE_BY_KEY, ROUTERS, LINK_EQUIP, EQUIP,
                         PORTAS, IP_ROTEADOR, ROTEADORES_A_DISTRIBUIR, REDE_NOTA,
                         CTO_POINT, STARLINK_POINT, rgb_hex, map_points,
                         camera_list, CAMERA_MODELS, CAMERA_MODEL_COUNT, CAMERA_NOTA)
from fibra_ligacao_svg import build_svg

from paths import docs, img
OUT = docs("mapa.html")

DIAG_SVG = build_svg()
def ll(p):
    return [p[1], p[0]]

routes_js = [{
    "key": r["key"], "nome": r["nome"], "cor": rgb_hex(r["rgb"]), "w": r["w"],
    "dash": bool(r.get("dash")), "via": r["via"], "equip": LINK_EQUIP[r["key"]],
    "pts": [ll(ALL[n]) for n in r["nodes"]],
} for r in ROUTES]

points_js = [{
    "ll": [p["lat"], p["lon"]], "poste": p["poste"], "cto": p["cto"],
    "rot": p["rot"], "equip": LINK_EQUIP[p["rot"]["lig"]] if p["rot"] else None,
    "ip": IP_ROTEADOR.get(p["rot"]["nome"]) if p["rot"] else None,
} for p in map_points()]

portas_js = [{
    "porta": pi["porta"], "tipo": pi["tipo"], "conv_tipo": pi["conv_tipo"],
    "roteador": pi["roteador"], "conf": pi["conf"],
    "cor": rgb_hex(ROUTE_BY_KEY["backbone"]["rgb"]) if pi["roteador"] == "RANCHO" else None,
} for pi in PORTAS]

# Nos pontos que já têm marcador (poste / CTO / roteador), o badge sai para um lado
# (ver OFF no JS). A câmera vai para o lado OPOSTO para não encavalar.
_BADGE_LEFT = {"P6", "P10", "P11", "MÃE"}   # pontos cujo badge fica à ESQUERDA
def _cam_side(c):
    key = (c["poste"] or c["wifi"] or "").upper()
    return "R" if key in _BADGE_LEFT else "L"

def _cam_foto(local):
    """Caminho relativo da foto real da câmera, se existir em docs/img/camera/."""
    for ext in (".jpeg", ".jpg", ".png", ".webp"):
        if os.path.exists(img("camera/" + local + ext)):
            return "img/camera/" + quote(local + ext)
    return None

# câmeras coincidentes (mesmo poste) são afastadas geograficamente por camera_list(spread_m)
# e recebem um empurrão vertical extra (dy) para as pills não se tocarem
_cams = camera_list(spread_m=8)
_n = {}
cams_js = []
for c in _cams:
    k = c["poste"] or c["local"]
    idx = _n.get(k, 0); _n[k] = idx + 1
    cams_js.append({
        "ll": [c["lat"], c["lon"]], "local": c["local"], "modelo": c["modelo"],
        "modelo_nome": c["modelo_nome"], "modelo_desc": CAMERA_MODELS[c["modelo"]]["desc"],
        "poste": c["poste"], "wifi": c["wifi"], "wifi_fix": c["wifi_fix"],
        "wifi_dist_txt": c["wifi_dist_txt"], "side": _cam_side(c), "dy": idx * 20,
        "foto": _cam_foto(c["local"]),
    })

DATA = {
    "routes": routes_js, "points": points_js, "portas": portas_js,
    "a_distribuir": ROTEADORES_A_DISTRIBUIR, "cams": cams_js,
    "cam_models": CAMERA_MODELS, "cam_count": CAMERA_MODEL_COUNT, "cam_nota": CAMERA_NOTA,
    "starlink": ll(STARLINK_POINT), "cto": ll(CTO_POINT), "equip": EQUIP,
    "ips": IP_ROTEADOR, "rede_nota": REDE_NOTA,
}

HTML = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Rede de Fibra Óptica — Fazenda Sagrada Família</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">
<style>
  html,body{margin:0;height:100%;font-family:system-ui,Segoe UI,Roboto,sans-serif;background:#0f1420;
    -webkit-text-size-adjust:100%}
  #map{position:absolute;inset:0}
  .leaflet-popup-content{font-size:13px;line-height:1.5}
  .leaflet-popup-content b{font-size:13.5px}
  .campop img.camfoto{width:100%;display:block;border-radius:6px;margin:6px 0 2px;
    aspect-ratio:16/9;object-fit:cover;border:1px solid #2b3550;background:#0e1626}
  .campop .cammeta{font-size:12px;color:#dfe6f0}
  .row{display:flex;align-items:center;gap:8px;margin:2px 0}
  .row i{flex:0 0 26px;height:5px;border-radius:2px}
  .row i.dash{background:repeating-linear-gradient(90deg,#fff 0 5px,transparent 5px 9px)!important}
  .row .g{flex:0 0 22px;display:flex;justify-content:center}
  .ok{color:#3ecb7d;font-weight:700}.warn{color:#ffb43c;font-weight:700}
  .eq{font-size:11px;color:#9fb0c8;line-height:1.5;margin-top:6px}
  code{background:#0e1626;padding:1px 5px;border-radius:4px;color:#9ad0ff}

  /* ---- barra de botões ---- */
  .btns{position:absolute;top:8px;left:8px;right:8px;z-index:1200;display:flex;gap:6px;flex-wrap:wrap}
  .btns button,.btns .btn-a{background:rgba(20,28,44,.94);color:#eef2f8;border:1px solid #33405f;border-radius:8px;
    padding:9px 13px;font-size:13px;line-height:1;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,.35);
    text-decoration:none;display:inline-block}
  .btns button.on{background:#2b60b0;border-color:#4f8fe0}
  .btns .sp{flex:1}

  /* ---- painéis (drawers) ---- */
  .drawer{position:absolute;z-index:1150;background:rgba(14,19,30,.97);color:#eef2f8;border:1px solid #2b3550;
    border-radius:12px;box-shadow:0 8px 30px rgba(0,0,0,.55);display:none;overflow:auto;
    top:54px;left:8px;width:min(430px,calc(100vw - 16px));max-height:calc(100vh - 66px)}
  .drawer.show{display:block}
  .drawer .hd{position:sticky;top:0;background:rgba(14,19,30,.98);display:flex;align-items:center;
    gap:8px;padding:10px 12px;border-bottom:1px solid #263049}
  .drawer .hd h2{flex:1;font-size:12px;letter-spacing:.04em;color:#cbd4e2;margin:0;text-transform:uppercase}
  .drawer .hd button{background:none;border:0;color:#9fb0c8;font-size:20px;line-height:1;cursor:pointer;padding:2px 6px}
  .drawer .bd{padding:12px 14px;font-size:12.5px;line-height:1.5}
  .drawer table{border-collapse:collapse;width:100%;font-size:12px;margin-bottom:8px}
  .drawer th,.drawer td{padding:5px 7px;text-align:left;border-bottom:1px solid #263049}
  .drawer th{color:#cbd4e2;background:#1a2338}
  .drawer .c{width:15px;height:15px;border-radius:3px;display:inline-block;vertical-align:middle}
  .drawer img{width:100%;border-radius:8px;display:block}
  .drawer a{color:#7cc0ff;text-decoration:none}
  .drawer a:hover{text-decoration:underline}
  /* linhas/itens que levam a um ponto do mapa */
  .drawer [data-feat]{cursor:pointer}
  .drawer tr[data-feat]:hover td{background:#22304e}
  .drawer .row[data-feat]:hover{background:#22304e;border-radius:5px}
  .drawer tr[data-feat] td:first-child::after,
  .drawer .row[data-feat]>span::after{content:" ⌖";color:#6f89ad;font-weight:400}
  .drawer .legb em{font-style:normal;font-weight:400;text-transform:none;letter-spacing:0;color:#7a8aa0;font-size:9.5px}
  .drawer .legb{display:block;margin:10px 0 4px;font-size:10.5px;letter-spacing:.06em;color:#9fb0c8}
  .drawer .legb:first-child{margin-top:0}
  @media (min-width:900px){
    .drawer{left:auto;right:8px;width:560px}
    #d-leg{left:8px;right:auto;width:360px;top:auto;bottom:8px}
  }

  .alvo{position:relative;width:54px;height:54px}
  .alvo .ret{position:absolute;left:50%;top:50%;width:26px;height:26px;margin:-13px 0 0 -13px;
    border:2.5px solid var(--c);border-radius:50%;box-shadow:0 0 0 2px rgba(0,0,0,.55)}
  .alvo .ret::before,.alvo .ret::after{content:"";position:absolute;background:var(--c)}
  .alvo .ret::before{left:50%;top:-8px;width:2px;height:7px;margin-left:-1px;box-shadow:0 33px 0 var(--c)}
  .alvo .ret::after{top:50%;left:-8px;height:2px;width:7px;margin-top:-1px;box-shadow:33px 0 0 var(--c)}
  .alvo .dot{position:absolute;left:50%;top:50%;width:5px;height:5px;margin:-2.5px 0 0 -2.5px;
    border-radius:50%;background:var(--c)}
  .alvo.r .pulse{position:absolute;left:50%;top:50%;width:16px;height:16px;margin:-8px 0 0 -8px;
    border-radius:50%;background:var(--c);animation:apulse 2.1s ease-out infinite}
  .alvo.r .pulse.b{animation-delay:1.05s}
  @keyframes apulse{0%{transform:scale(.5);opacity:.7}70%{transform:scale(3);opacity:0}100%{opacity:0}}
  .badge{position:absolute;left:34px;top:2px;display:flex;align-items:center;gap:4px;white-space:nowrap;
    background:rgba(16,22,36,.92);border:1.5px solid var(--c);border-radius:7px;padding:3px 7px 3px 5px;
    font:700 11.5px system-ui;color:#eef3f8}
  .badge svg{display:block}
  .led{animation:blk 1.1s steps(1) infinite}@keyframes blk{0%,49%{opacity:1}50%,100%{opacity:.15}}
  @media (max-width:760px){.badge{font-size:10.5px}}

  /* ---- marcadores de câmera (pill deslocada do ponto, lado oposto ao badge) ---- */
  .camwrap{position:relative;width:0;height:0}
  .camwrap::before{content:"";position:absolute;left:-3px;top:-3px;width:6px;height:6px;border-radius:50%;
    background:var(--cc);box-shadow:0 0 0 1.5px rgba(0,0,0,.6)}
  .cam{position:absolute;top:-9px;display:flex;align-items:center;gap:4px;white-space:nowrap;
    background:rgba(12,18,30,.92);border:1.5px solid var(--cc);border-radius:7px;padding:2px 6px 2px 4px;
    font:700 11px system-ui;color:#eaf3fb;box-shadow:0 1px 6px rgba(0,0,0,.5)}
  .cam.sR{left:9px}
  .cam.sL{right:9px;flex-direction:row-reverse;padding:2px 4px 2px 6px}
  .cam svg{display:block;flex:0 0 auto}
  .cam.k{font-size:11.5px;border-width:2px}
  @media (max-width:760px){.cam{font-size:10px}.cam span{display:none}.cam.k span{display:inline}}

  /* ---- diagrama SVG com zoom ---- */
  .diag-vp{overflow:hidden;background:#0f1420;touch-action:none;cursor:grab;
    height:min(74vh,calc(100vh - 120px))}
  .diag-vp:active{cursor:grabbing}
  .diag-stage{transform-origin:0 0;width:100%}
  .diag-stage svg{display:block;width:100%;height:auto}
  .diag-hint{padding:8px 12px;font-size:11px;color:#8fa0b8;border-top:1px solid #263049;background:rgba(14,19,30,.98)}
  #d-diag .hd button.zb{background:#1f2942;border:1px solid #33405f;color:#dfe7f2;font-size:16px;
    line-height:1;cursor:pointer;padding:3px 9px;border-radius:6px;font-weight:700}
  #diag-fit{background:none;border:0;color:#9fb0c8;font-size:17px;line-height:1;cursor:pointer;padding:2px 6px}

  /* botão dentro de popup / link p/ abrir painel */
  .leaflet-popup-content .popbtn{margin-top:8px;display:block;width:100%;background:#2b60b0;color:#fff;
    border:1px solid #4f8fe0;border-radius:6px;padding:7px 10px;font-size:12px;cursor:pointer;text-align:center}
  .drawer .lnk{background:none;border:0;color:#7cc0ff;cursor:pointer;padding:0;font:inherit;text-decoration:underline}
</style>
</head>
<body>
<div class="btns">
  <a class="btn-a" href="./" title="Início">🏠</a>
  <button id="b-leg">🎨 Legenda</button>
  <button id="b-cam">📷 Câmeras</button>
  <button id="b-portas">🔌 Portas</button>
  <button id="b-ip">🌐 IPs</button>
  <button id="b-diag">▦ Diagrama</button>
  <span class="sp"></span>
  <button id="b-info">ℹ︎</button>
</div>

<div class="drawer" id="d-info"><div class="hd"><h2>Projeto</h2><button data-close>×</button></div>
  <div class="bd"><b>Projeto de infraestrutura — Rede de fibra óptica</b><br>
  Fazenda Sagrada Família · imagem de satélite Google · uma cor por ligação · postes P1…P20 na sequência da fibra.<br><br>
  Toque nos marcadores do mapa para ver detalhes de cada poste / roteador. Use os botões acima para abrir a legenda,
  a tabela de portas do switch, os IPs e o diagrama de ligação. Toque de novo no botão (ou no ×) para fechar e ver o mapa.</div></div>

<div class="drawer" id="d-leg"><div class="hd"><h2>Legenda</h2><button data-close>×</button></div>
  <div class="bd" id="leg-bd"></div></div>

<div class="drawer" id="d-portas"><div class="hd"><h2>Portas do switch 8SC2E</h2><button data-close>×</button></div>
  <div class="bd" id="portas-bd"></div></div>

<div class="drawer" id="d-ip"><div class="hd"><h2>Endereçamento IP</h2><button data-close>×</button></div>
  <div class="bd" id="ip-bd"></div></div>

<div class="drawer" id="d-cam"><div class="hd"><h2>Câmeras de segurança</h2><button data-close>×</button></div>
  <div class="bd" id="cam-bd"></div></div>

<div class="drawer" id="d-diag"><div class="hd"><h2>Diagrama</h2>
  <button class="zb" id="diag-zout" title="Menos zoom">−</button>
  <button class="zb" id="diag-zin" title="Mais zoom">+</button>
  <button id="diag-fit" title="Ajustar à tela">⤢</button><button data-close>×</button></div>
  <div class="bd" style="padding:0">
    <div id="diag-vp" class="diag-vp">
      <div id="diag-stage" class="diag-stage">__DIAG__</div>
    </div>
    <div class="diag-hint">+ / − ou pinça / roda do mouse para dar zoom · arraste para mover · SVG vetorial (não perde qualidade)</div>
  </div></div>

<div id="map"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<script>
const DATA = __DATA__;
const ROUTE = {}; DATA.routes.forEach(r=>ROUTE[r.key]=r);

const map = L.map('map',{zoomControl:true});
L.tileLayer('https://mt{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
  {subdomains:['0','1','2','3'],maxZoom:22,maxNativeZoom:19,attribution:'Imagens © Google'}).addTo(map);
// (a imagem de satélite da fazenda vai até z19; acima disso amplia a mesma imagem — fica mais perto do ponto)
const grupo = L.featureGroup().addTo(map);
const FEAT = {};   // chave ("rot:MOTOR", "cam:Piscina", "poste:P9", "lig:motor") -> marcador/linha

function goToFeature(key){
  const f = FEAT[key];
  if(!f) return;
  // fecha o painel p/ ver o mapa (no desktop mantém a Legenda aberta p/ clicar em várias ligações)
  if(window.matchMedia('(max-width:899px)').matches || !key.startsWith('lig:')) setOpen(null);
  if(f.getLatLng){
    map.flyTo(f.getLatLng(), 21, {duration:.6});            // ~alguns metros do ponto
  }else if(f.getBounds){
    map.flyToBounds(f.getBounds().pad(0.15), {duration:.6, maxZoom:20});
  }
  setTimeout(()=>f.openPopup && f.openPopup(), 90);
}
document.addEventListener('click', e=>{
  const ob = e.target.closest('[data-open]');     // abrir um painel (ex.: ▦ Diagrama)
  if(ob){
    const b = ob.getAttribute('data-open');
    setOpen(b);
    if(b==='b-diag' && window._diagOpen) setTimeout(window._diagOpen, 60);
    if(map) map.closePopup();
    return;
  }
  if(e.target.closest('a[href]')) return;         // deixa links (fotos) funcionarem
  const el = e.target.closest('[data-feat]');
  if(el) goToFeature(el.getAttribute('data-feat'));
});

const SVG_POLE = c=>`<svg width="14" height="16" viewBox="0 0 14 16"><line x1="7" y1="1" x2="7" y2="15" stroke="#e9e9ee" stroke-width="2"/><line x1="1" y1="4" x2="13" y2="4" stroke="#e9e9ee" stroke-width="2"/><circle cx="2.5" cy="4" r="1.3" fill="#cfcfd6"/><circle cx="11.5" cy="4" r="1.3" fill="#cfcfd6"/></svg>`;
const SVG_CTO = `<svg width="16" height="17" viewBox="0 0 16 17"><rect x="1.5" y="1.5" width="13" height="14" rx="2" fill="#00af64" stroke="#fff" stroke-width="1.5"/><line x1="10" y1="1.5" x2="10" y2="15.5" stroke="#fff" stroke-width="1.4"/><line x1="1.5" y1="5" x2="4" y2="5" stroke="#fff" stroke-width="1.4"/><line x1="1.5" y1="11" x2="4" y2="11" stroke="#fff" stroke-width="1.4"/><path d="M4 5 A3 3 0 1 0 7 8" fill="none" stroke="#fff" stroke-width="1.4"/></svg>`;
const SVG_ROUTER = c=>`<svg width="18" height="16" viewBox="0 0 18 16"><line x1="4" y1="6" x2="2" y2="1" stroke="${c}" stroke-width="1.6"/><line x1="7.5" y1="5" x2="6.5" y2="1" stroke="${c}" stroke-width="1.6"/><line x1="10.5" y1="5" x2="11.5" y2="1" stroke="${c}" stroke-width="1.6"/><line x1="14" y1="6" x2="16" y2="1" stroke="${c}" stroke-width="1.6"/><path d="M9 5 L16 9 L9 13 L2 9 Z" fill="#1c1c22" stroke="${c}" stroke-width="1.7"/><circle class="led" cx="7" cy="9" r="1.1" fill="#39d353"/><circle cx="11" cy="9" r="1.1" fill="${c}"/></svg>`;
const CAM_C = {kapbom:'#ffd23c', e27:'#5ee0ff'};
const SVG_CAM = c=>`<svg width="15" height="13" viewBox="0 0 15 13"><rect x="1" y="3" width="9" height="7" rx="1.5" fill="#0d1420" stroke="${c}" stroke-width="1.5"/><circle cx="5.5" cy="6.5" r="2" fill="none" stroke="${c}" stroke-width="1.3"/><path d="M10 4.5 L13 3 M10 8.5 L13 10" stroke="${c}" stroke-width="1.3"/><path d="M11.4 2.2 A4 4 0 0 1 11.4 10.8" fill="none" stroke="${c}" stroke-width="1.1" opacity=".8"/></svg>`;

function portaTxt(e){
  if(!e) return '';
  if(e.porta==='RJ45-1') return 'ligado no <b>RJ45-1</b> do switch (patch curto no poste P9)';
  if(e.conf) return 'porta <b>'+e.porta+'</b> (SC '+e.porta_tipo+') → conversor tipo <b>'+e.conv_tipo+'</b> <span class="ok">✔ confirmado</span>';
  return 'porta do switch: <b>a definir</b> · conversor será do tipo oposto <span class="warn">⚠</span>';
}

// -------- ligacoes: linhas PARALELAS (todas as cores nos trechos compartilhados) --------
const SPACING = 4;                              // px entre trilhos paralelos
const drawRoutes = DATA.routes.filter(r => r.pts.length >= 2 &&
   !(r.pts.length === 2 && JSON.stringify(r.pts[0]) === JSON.stringify(r.pts[1])));
const ekey = p => p[0].toFixed(7) + ',' + p[1].toFixed(7);
const edgeUsers = {};                           // aresta -> [indices de rota, na ordem de DATA.routes]
drawRoutes.forEach((r, ri) => {
  for (let i = 0; i < r.pts.length - 1; i++) {
    const a = ekey(r.pts[i]), b = ekey(r.pts[i + 1]);
    const k = a < b ? a + '|' + b : b + '|' + a;
    (edgeUsers[k] = edgeUsers[k] || []).push(ri);
  }
});
function edgeInfo(ri, p, q) {
  const a = ekey(p), b = ekey(q);
  const k = a < b ? a + '|' + b : b + '|' + a;
  const u = edgeUsers[k] || [ri];
  return { slot: u.indexOf(ri), count: u.length };
}
function offsetLatLngs(r, ri) {
  const P = r.pts.map(ll => map.latLngToLayerPoint(L.latLng(ll[0], ll[1])));
  const out = [];
  for (let i = 0; i < P.length; i++) {
    const a = i < P.length - 1 ? P[i] : P[i - 1];
    const b = i < P.length - 1 ? P[i + 1] : P[i];
    const pa = i < P.length - 1 ? r.pts[i] : r.pts[i - 1];
    const pb = i < P.length - 1 ? r.pts[i + 1] : r.pts[i];
    const info = edgeInfo(ri, pa, pb);
    const dx = b.x - a.x, dy = b.y - a.y, len = Math.hypot(dx, dy) || 1;
    const px = -dy / len, py = dx / len;
    const off = (info.slot - (info.count - 1) / 2) * SPACING;
    out.push(map.layerPointToLatLng(L.point(P[i].x + px * off, P[i].y + py * off)));
  }
  return out;
}
const coloredLines = [];
const casings = drawRoutes.map(r =>
  L.polyline(r.pts, { color: '#000', weight: r.w + 3, opacity: .55, lineCap: 'round' }).addTo(grupo));
drawRoutes.forEach((r, ri) => {
  const ln = L.polyline(r.pts, { color: r.cor, weight: r.w, opacity: 1,
      dashArray: r.dash ? '10 8' : null, lineJoin: 'round', lineCap: 'round' }).addTo(grupo);
  ln.bindPopup('<b style="color:' + r.cor + '">■</b> <b>' + r.nome + '</b><br>' + r.via + '<br>' + portaTxt(r.equip));
  FEAT['lig:' + r.key] = ln;
  coloredLines.push({ ln, cas: casings[ri], r, ri });
});
function reflowLines() {
  coloredLines.forEach(({ ln, cas, r, ri }) => {
    const o = offsetLatLngs(r, ri);
    cas.setLatLngs(o); ln.setLatLngs(o);
  });
}
map.on('zoomend viewreset', reflowLines);

// -------- marcadores "alvo" --------
const OFF = {P9:[34,-30],P8:[34,14],P10:[-160,-6],P11:[-130,10],P7:[34,-4],P6:[-130,-6],
 rancho:[34,-6],sede:[34,-4],'mãe':[-130,12],lazer:[34,10]};
function alvo(pt){
  const rot = pt.rot, cor = rot ? rot.cor : '#ffffff';
  let icons = '';
  if(pt.poste) icons += SVG_POLE(cor);
  if(pt.cto)   icons += SVG_CTO;
  if(rot)      icons += SVG_ROUTER(cor);
  let txt = pt.poste || '';
  if(rot && !pt.cto) txt = (pt.poste ? pt.poste+' · ' : '') + 'Roteador '+rot.nome;
  else if(pt.cto)    txt = pt.poste+' · Caixa CTO';
  const key = (pt.poste || (rot?rot.nome.toLowerCase():'')).toLowerCase();
  const o = OFF[key] || [34,-6];
  const html = `<div class="alvo ${rot?'r':''}" style="--c:${cor}">
     ${rot?'<div class="pulse"></div><div class="pulse b"></div>':''}
     <div class="ret"></div><div class="dot"></div>
     <div class="badge" style="left:${27+o[0]}px;top:${27+o[1]}px">${icons}<span>${txt}</span></div></div>`;
  const m = L.marker(pt.ll,{icon:L.divIcon({className:'',html,iconSize:[54,54],iconAnchor:[27,27]}),
                            zIndexOffset: rot?600:300}).addTo(grupo);
  if(pt.poste) FEAT['poste:'+pt.poste] = m;
  if(rot)      FEAT['rot:'+rot.nome]   = m;
  let pop = '<b>'+(pt.poste?('Poste '+pt.poste):'')+'</b>';
  if(pt.cto) pop += (pt.poste?'<br>':'')+'<b>Caixa CTO</b> — '+DATA.equip.switch;
  if(rot){
    pop += '<br><b>Roteador '+rot.nome+'</b>'+(pt.poste||pt.cto?'':'  (nó de rede)')+
           '<br>Equipamento: '+DATA.equip.roteador_curto+
           (pt.ip?('<br>IP: <code>'+pt.ip+'</code>'):'')+
           '<br>Ligação: <b style="color:'+cor+'">'+ROUTE[rot.lig].nome.replace('Ligação ','')+'</b>'+
           '<br>'+portaTxt(pt.equip)+'<br><span style="color:#2b8cff">● em operação</span>';
  }
  if(pt.cto) pop += '<button class="popbtn" data-open="b-diag">▦ Ver diagrama de ligação (com zoom)</button>';
  m.bindPopup(pop);
}
DATA.points.forEach(alvo);

// -------- marcadores de câmera --------
const camLayer = L.featureGroup().addTo(map);
DATA.cams.forEach(c=>{
  const cc = CAM_C[c.modelo] || '#5ee0ff';
  const html = `<div class="camwrap" style="--cc:${cc}"><div class="cam s${c.side||'L'} ${c.modelo==='kapbom'?'k':''}" style="top:${-9+(c.dy||0)}px">${SVG_CAM(cc)}<span>${c.local}</span></div></div>`;
  const m = L.marker(c.ll,{icon:L.divIcon({className:'',html,iconSize:[1,1],iconAnchor:[0,0]}),
                           zIndexOffset:450}).addTo(camLayer);
  FEAT['cam:'+c.local] = m;
  const onde = c.poste ? ('poste '+c.poste) : (c.ll[0].toFixed(5)+', '+c.ll[1].toFixed(5));
  const wifi = 'Roteador <b>'+c.wifi+'</b>'+(c.wifi_dist_txt?' <span class="warn">'+c.wifi_dist_txt+'</span>':'');
  const foto = c.foto ? ('<a href="'+c.foto+'" target="_blank" rel="noopener" title="abrir imagem">'+
                         '<img class="camfoto" src="'+c.foto+'" alt="Vista da câmera '+c.local+'" loading="lazy"></a>') : '';
  m.bindPopup('<div class="campop"><b>Câmera '+c.local+'</b>'+foto+
              '<div class="cammeta">'+c.modelo_desc+'<br>Local: '+onde+'<br>Wi-Fi: '+wifi+
              '<br><span style="color:#2b8cff">● Wi-Fi (fora da fibra)</span></div></div>',
              {maxWidth: c.foto ? 340 : 300});
});

FEAT['lig:rj45'] = FEAT['rot:CTO'];   // ligação RJ45 não tem traçado -> aponta pro roteador CTO

FEAT['starlink'] = L.marker(DATA.starlink,{icon:L.divIcon({className:'',iconSize:[40,40],iconAnchor:[20,20],
  html:`<div class="alvo" style="--c:#9a5cff"><div class="ret"></div><div class="dot"></div>
    <div class="badge" style="left:34px;top:20px">
    <svg width="18" height="14" viewBox="0 0 18 14"><polygon points="1,10 16,3 14,10 3,12" fill="#d4d6e0" stroke="#8a8c94"/><line x1="8" y1="11" x2="8" y2="14" stroke="#8a8c94" stroke-width="2"/></svg>
    <span>Starlink</span></div></div>`}),zIndexOffset:500})
 .addTo(grupo).bindPopup('<b>Starlink</b><br>Origem do sinal. Entra na WAN do Roteador RANCHO.');

map.fitBounds(grupo.getBounds().pad(0.06));
reflowLines();

// -------- legenda --------
let h = '<span class="legb">CORES DAS LIGAÇÕES <em>· toque para ver no mapa</em></span>';
DATA.routes.forEach(r=>{ h += '<div class="row" data-feat="lig:'+r.key+'" title="ver no mapa">'+
  '<i class="'+(r.dash?'dash':'')+'" style="background:'+r.cor+'"></i>'+
  '<span>'+r.nome.replace('Ligação ','')+'</span></div>'; });
h += '<span class="legb">SÍMBOLOS (marcador no ponto da coordenada)</span>'+
 '<div class="row"><span class="g"><svg width="18" height="18" viewBox="0 0 18 18"><circle cx="9" cy="9" r="6" fill="none" stroke="#fff" stroke-width="2"/><circle cx="9" cy="9" r="1.6" fill="#fff"/></svg></span>ponto exato da coordenada</div>'+
 '<div class="row"><span class="g">'+SVG_POLE('#fff')+'</span>poste (P1…P20)</div>'+
 '<div class="row"><span class="g">'+SVG_CTO+'</span>Caixa CTO — switch 8SC2E</div>'+
 '<div class="row"><span class="g">'+SVG_ROUTER('#7cc0ff')+'</span>Roteador Mercusys MR60X (anel pulsa na cor da ligação)</div>'+
 '<span class="legb">CÂMERAS DE SEGURANÇA (Wi-Fi — fora da fibra)</span>'+
 '<div class="row"><span class="g">'+SVG_CAM(CAM_C.kapbom)+'</span>Kapbom IP 360° — poste ('+DATA.cam_count.kapbom+')</div>'+
 '<div class="row"><span class="g">'+SVG_CAM(CAM_C.e27)+'</span>Soquete lâmpada E27 360° ('+DATA.cam_count.e27+')</div>';
document.getElementById('leg-bd').innerHTML = h;

// -------- drawer: câmeras --------
let ct2='<table><thead><tr><th>Local</th><th>Poste / coord.</th><th>Modelo</th><th>Wi-Fi</th></tr></thead><tbody>';
DATA.cams.forEach(c=>{
  const onde = c.poste ? c.poste : (c.ll[0].toFixed(5)+', '+c.ll[1].toFixed(5));
  const wifi = '<b>'+c.wifi+'</b>'+(c.wifi_dist_txt?' <span class="warn">'+c.wifi_dist_txt+'</span>':'');
  const nome = (c.foto ? ('<a href="'+c.foto+'" target="_blank" rel="noopener">📷</a> ') : '') + c.local;
  ct2+='<tr data-feat="cam:'+c.local+'" title="ver no mapa"><td><b>'+nome+'</b></td><td>'+onde+
       '</td><td>'+c.modelo_nome+'</td><td>Rot. '+wifi+'</td></tr>';
});
ct2+='</tbody></table><div class="eq">Toque numa câmera para ir até ela no mapa · 📷 abre a foto real.<br>'+DATA.cam_nota+'</div>';
document.getElementById('cam-bd').innerHTML=ct2;

// -------- drawer: portas (reflete o diagrama de ligação) --------
let t='<table><thead><tr><th>Porta</th><th>Tipo</th><th>Conversor</th><th></th><th>Roteador (MR60X)</th><th>Status</th></tr></thead><tbody>';
DATA.portas.forEach(p=>{
  t+='<tr'+(p.conf?' data-feat="rot:'+p.roteador+'" title="ver no mapa"':'')+'><td><b>'+p.porta+'</b></td><td>SC '+p.tipo+'</td><td>tipo '+p.conv_tipo+'</td>'+
     '<td>'+(p.cor?('<span class="c" style="background:'+p.cor+'"></span>'):'')+'</td>'+
     '<td>'+(p.conf?('<b>Roteador '+p.roteador+'</b>'):'<span class="warn">? definir</span>')+'</td>'+
     '<td class="'+(p.conf?'ok':'warn')+'">'+(p.conf?'✔ confirmado':'definir')+'</td></tr>';
});
t+='<tr data-feat="rot:CTO" title="ver no mapa"><td><b>RJ45-1</b></td><td>—</td><td>— (RJ45)</td><td><span class="c" style="background:#fff"></span></td>'+
   '<td><b>Roteador CTO</b> · poste P9</td><td class="ok">✔ confirmado</td></tr>'+
   '<tr><td><b>RJ45-2</b></td><td>—</td><td>—</td><td></td><td>reserva / livre</td><td>—</td></tr>';
t+='</tbody></table><div class="eq">Linhas com ⌖ (porta 5, RJ45-1) levam ao roteador no mapa.<br>'+
 'Reflete o <button class="lnk" data-open="b-diag">▦ diagrama de ligação</button> (abre com zoom). '+
 'Regra BiDi: porta SC A ↔ conversor tipo B  |  porta SC B ↔ conversor tipo A — <b>já definido</b>.<br>'+
 'Falta só o <b>nome do roteador</b> das portas 1–4 e 6–8: '+DATA.a_distribuir.join(' · ')+'.<br>'+
 'Confirmado: porta 5 = Roteador RANCHO · RJ45-1 = Roteador CTO.</div>';
document.getElementById('portas-bd').innerHTML=t;

// -------- drawer: IPs --------
let ipr = Object.entries(DATA.ips).map(([n,ip])=>
  '<tr data-feat="rot:'+n+'" title="ver no mapa"><td>Roteador <b>'+n+'</b></td><td><code>'+ip+'</code></td></tr>').join('');
document.getElementById('ip-bd').innerHTML =
 '<table><thead><tr><th>Roteador (MR60X)</th><th>IP de gerência</th></tr></thead><tbody>'+ipr+'</tbody></table>'+
 '<div class="eq">Toque num roteador para ir até ele no mapa.<br>'+DATA.rede_nota+'</div>';

// -------- botoes / drawers (um de cada vez; começa fechado) --------
const D = {'b-leg':'d-leg','b-cam':'d-cam','b-portas':'d-portas','b-ip':'d-ip','b-diag':'d-diag','b-info':'d-info'};
function setOpen(bid){
  Object.entries(D).forEach(([b,dd])=>{
    const on = (b===bid);
    document.getElementById(dd).classList.toggle('show', on);
    document.getElementById(b).classList.toggle('on', on);
  });
}
Object.keys(D).forEach(bid=>{
  document.getElementById(bid).addEventListener('click',()=>{
    const open = !document.getElementById(D[bid]).classList.contains('show');
    setOpen(open ? bid : null);
    if(open && bid==='b-diag' && window._diagOpen) setTimeout(window._diagOpen, 60);
  });
});
document.querySelectorAll('.drawer [data-close]').forEach(x=>x.addEventListener('click',()=>setOpen(null)));

// -------- diagrama: pan + zoom (mouse, roda e pinça) --------
(function(){
  const vp=document.getElementById('diag-vp'), st=document.getElementById('diag-stage');
  let sc=1, tx=0, ty=0;
  const apply=()=>{ st.style.transform=`translate(${tx}px,${ty}px) scale(${sc})`; };
  function fit(){ sc=1; tx=0; ty=0; apply(); }   // ⤢ visão geral (cabe na largura)
  function readStart(){                           // abertura: já num zoom legível (canto sup. esq.)
    const w = vp.getBoundingClientRect().width || 400;
    sc = Math.max(1, Math.min(4, 900 / w)); tx = 0; ty = 0; apply();
  }
  window._diagFit=fit; window._diagOpen=readStart;
  function zoomAt(cx,cy,f){
    const r=vp.getBoundingClientRect(), x=cx-r.left, y=cy-r.top;
    const ns=Math.min(14, Math.max(0.9, sc*f));
    f=ns/sc; tx=x-(x-tx)*f; ty=y-(y-ty)*f; sc=ns; apply();
  }
  const zc=f=>{ const r=vp.getBoundingClientRect(); zoomAt(r.left+r.width/2, r.top+r.height/2, f); };
  vp.addEventListener('wheel',e=>{ e.preventDefault(); zoomAt(e.clientX,e.clientY, e.deltaY<0?1.12:1/1.12); },{passive:false});
  let pts=new Map(), pd=0, pcx=0, pcy=0;
  vp.addEventListener('pointerdown',e=>{ vp.setPointerCapture(e.pointerId); pts.set(e.pointerId,[e.clientX,e.clientY]); });
  vp.addEventListener('pointermove',e=>{
    if(!pts.has(e.pointerId)) return;
    const prev=pts.get(e.pointerId); pts.set(e.pointerId,[e.clientX,e.clientY]);
    const a=[...pts.values()];
    if(a.length===1){ tx+=e.clientX-prev[0]; ty+=e.clientY-prev[1]; apply(); }
    else if(a.length===2){
      const nd=Math.hypot(a[0][0]-a[1][0], a[0][1]-a[1][1]);
      const ncx=(a[0][0]+a[1][0])/2, ncy=(a[0][1]+a[1][1])/2;
      if(pd){ zoomAt(ncx,ncy, nd/pd); tx+=ncx-pcx; ty+=ncy-pcy; apply(); }
      pd=nd; pcx=ncx; pcy=ncy;
    }
  });
  const up=e=>{ pts.delete(e.pointerId); if(pts.size<2) pd=0; };
  vp.addEventListener('pointerup',up); vp.addEventListener('pointercancel',up);
  document.getElementById('diag-fit').addEventListener('click',fit);
  document.getElementById('diag-zin').addEventListener('click',()=>zc(1.6));
  document.getElementById('diag-zout').addEventListener('click',()=>zc(1/1.6));
})();
// desktop: abre a legenda; mobile: começa tudo fechado (só o mapa)
if (window.matchMedia('(min-width:900px)').matches) setOpen('b-leg');
setTimeout(()=>{map.invalidateSize(); reflowLines();}, 200);
</script>
</body>
</html>
"""

open(OUT, "w").write(HTML.replace("__DATA__", json.dumps(DATA, ensure_ascii=False)).replace("__DIAG__", DIAG_SVG))
print("salvo:", OUT)
