# Rede de Fibra Óptica — Fazenda Sagrada Família

Projeto de infraestrutura da rede de fibra óptica da fazenda: distribuição de internet
a partir de um link **Starlink**, por um backbone de fibra até a **Caixa CTO** (poste P9),
e de lá por 7 ramais de fibra + 1 ramal RJ45 até um roteador **Mercusys MR60X** em cada local.
Inclui também as **17 câmeras de segurança Wi-Fi 360°** (Kapbom de poste + soquete E27), que
não usam a fibra — cada uma conecta no Wi-Fi do roteador MR60X mais próximo.

O site publicado (GitHub Pages) fica em **`docs/`** e tem:

| Página | Arquivo |
|---|---|
| Início (navegável) | `docs/index.html` |
| Mapa interativo | `docs/mapa.html` |
| PDF do projeto (7 páginas — a 7ª é a das câmeras) | `docs/fibra_infra_projeto.pdf` |
| Etiquetas dos cabos (folha A4 p/ imprimir — cor + nome + IP) | `docs/etiquetas_roteadores.pdf` |
| KML (Google Earth) — traçado, roteadores e câmeras | `docs/fibra_infra.kml` |
| Imagens | `docs/img/*.png` |
| Diagrama de ligação vetorial (zoom sem perda) | `docs/img/fibra_ligacao.svg` |
| Fotos reais da vista de cada câmera | `docs/img/camera/<Local>.jpeg` |

---

## Estrutura

```
.
├── build.sh                  # reconstrói tudo em docs/
├── requirements.txt          # Pillow + requests
├── data/
│   └── coordenadas.kml       # KML ORIGINAL exportado do Google Earth (fonte das coordenadas)
├── src/                      # geradores (Python) — é AQUI que se edita
│   ├── fibra_dados.py        # ★ FONTE ÚNICA DE DADOS (coordenadas, ligações, equipamentos, IPs, câmeras)
│   ├── paths.py              # caminhos de saída (docs/, docs/img/)
│   ├── fibra_equipamentos.py # diagrama de ligação do switch  -> img/fibra_equipamentos.png + fibra_ligacao.png
│   ├── fibra_ligacao_svg.py  # mesmo diagrama em SVG vetorial  -> img/fibra_ligacao.svg  (zoom no mobile)
│   ├── fibra_esquema.py      # esquema/topologia da rede      -> img/fibra_esquema.png
│   ├── gen_map.py            # mapa sobre satélite Google      -> img/fibra_infra.png
│   ├── gen_kml.py            # KML com traçado + pontos        -> fibra_infra.kml
│   ├── gen_html.py           # mapa interativo (Leaflet)       -> mapa.html
│   ├── gen_pdf.py            # PDF completo                    -> fibra_infra_projeto.pdf
│   ├── gen_etiquetas.py      # folha A4 de etiquetas dos cabos -> etiquetas_roteadores.pdf
│   └── gen_index.py          # página inicial                  -> index.html
└── docs/                     # SAÍDA — servida pelo GitHub Pages (não editar à mão)
```

---

## Como reconstruir

```bash
pip install -r requirements.txt      # uma vez
./build.sh                           # gera tudo em docs/
```

`gen_map.py` baixa as imagens de satélite do Google (precisa de internet). O resto é offline.

Para rodar um gerador isolado:

```bash
cd src && python3 gen_html.py
```

---

## Onde mudar cada coisa

**Quase tudo está em [`src/fibra_dados.py`](src/fibra_dados.py).** Depois de editar, rode `./build.sh`.

| O que | Onde em `fibra_dados.py` |
|---|---|
| Coordenadas dos postes | `POSTES` (lon, lat) |
| Coordenadas de nós nomeados (starlink, rancho, sede, mãe, lazer) | `NAMED` |
| Traçado de cada ligação de fibra (por quais postes passa) e sua cor | `ROUTES` (lista `nodes`, `rgb`) |
| Quais roteadores existem, em que poste/nó, e status | `ROUTERS` |
| Modelos de equipamento (texto) | `EQUIP` |
| Tipo (A/B) de cada porta SC do switch | `PORT_TYPES` (1–4 = A, 5–8 = B) |
| Ligação porta do switch ↔ roteador confirmado | `LINK_EQUIP` (porta 5 = RANCHO) e `PORTAS` |
| Roteadores ainda sem porta definida | `ROTEADORES_A_DISTRIBUIR` |
| IPs dos roteadores | `IP_ROTEADOR` |
| Texto do caminho da internet | `REDE_NOTA` |
| Câmeras de segurança (ponto, local, modelo, poste, Wi-Fi) | `CAMERAS` |
| Modelos de câmera (texto) | `CAMERA_MODELS` |

> Câmeras: o 5º campo de cada linha de `CAMERAS` é o roteador Wi-Fi. `None` = usa o MR60X
> **mais próximo** (`cam_wifi()`); um nome fixa a associação (usado no cluster Mãe/CTO/Lazer,
> onde a distância pura enganaria). Coordenadas em DMS entram via `dmsll('lat', 'lon')`.
>
> **Fotos das câmeras:** coloque um arquivo `docs/img/camera/<Local>.jpeg` (nome = campo *local*
> da câmera, ex.: `Mãe Lateral.jpeg`). Não é gerado — é asset manual. `gen_html.py` detecta e
> mostra no popup do mapa (clicar na câmera) e como link 📷 no drawer "Câmeras". Aceita `.jpeg/.jpg/.png/.webp`.

### Regras do modelo (importantes)

- **Postes renumerados** `P1…P20` na sequência da fibra (head-end → CTO → ramal mais longo).
  O de-para com o KML original está no cabeçalho de `fibra_dados.py` e na página 6 do PDF.
- **Pareamento BiDi do switch:** o conversor de mídia é sempre do **tipo oposto** ao da porta.
  `porta SC A ↔ conversor tipo B` · `porta SC B ↔ conversor tipo A`. Isso já é calculado
  (`conv_tipo()`); no diagrama só falta o **nome do roteador** de cada porta.
- **Confirmado:** porta 5 (SC B) → conversor tipo A → Roteador RANCHO · RJ45-1 → Roteador CTO.
  As portas 1–4 e 6–8 estão marcadas "a definir".

### Ajustes visuais

- Layout / rótulos do diagrama de ligação (PNG): `src/fibra_equipamentos.py`
- Diagrama de ligação em SVG (o que abre no mapa, com zoom): `src/fibra_ligacao_svg.py`
- Marcadores "alvo", câmeras, legenda e drawers do mapa: `src/gen_html.py`
- Páginas e tabelas do PDF (inclui a pág. 7 das câmeras): `src/gen_pdf.py`
- Cartões e tabelas da página inicial: `src/gen_index.py`
- Ícones e legenda de câmera no mapa estático: `src/gen_map.py` (`ic_cam`)

---

## Publicar no GitHub Pages

O site é a pasta **`docs/`** na branch principal.

```bash
git init
git add .
git commit -m "Projeto da rede de fibra óptica"
git branch -M main
git remote add origin git@github.com:<usuario>/<repo>.git
git push -u origin main
```

No GitHub: **Settings → Pages → Build and deployment → Source: _Deploy from a branch_ →
Branch: `main` / pasta `/docs` → Save.**

Em ~1 min o site fica em `https://<usuario>.github.io/<repo>/`.

Depois de qualquer alteração: `./build.sh && git commit -am "..." && git push`.

> Observação: `docs/mapa.html` usa camadas de satélite do Google e a biblioteca Leaflet via CDN.
> Precisa de internet para carregar o mapa. Para uma versão 100% offline, trocar a URL das
> tiles em `src/gen_html.py` por um provedor com uso livre (ex.: Esri World Imagery).
