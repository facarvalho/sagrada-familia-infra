#!/usr/bin/env bash
# Reconstrói todos os artefatos em docs/ a partir de src/.
# Uso:  ./build.sh
set -euo pipefail
cd "$(dirname "$0")/src"

python3 fibra_equipamentos.py   # docs/img/fibra_equipamentos.png + fibra_ligacao.png
python3 fibra_ligacao_svg.py    # docs/img/fibra_ligacao.svg (diagrama vetorial p/ zoom)
python3 fibra_esquema.py        # docs/img/fibra_esquema.png
python3 gen_map.py              # docs/img/fibra_infra.png   (baixa tiles do Google)
python3 gen_kml.py              # docs/fibra_infra.kml
python3 gen_html.py             # docs/mapa.html
python3 gen_pdf.py              # docs/fibra_infra_projeto.pdf
python3 gen_etiquetas.py        # docs/etiquetas_roteadores.pdf (folha A4 p/ imprimir)
python3 gen_index.py            # docs/index.html

rm -rf __pycache__
echo
echo "OK — abra docs/index.html"
