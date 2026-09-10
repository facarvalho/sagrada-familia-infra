# Câmeras ao vivo — opções

Como transmitir a imagem **ao vivo** das câmeras (hoje o mapa mostra só a foto fixa da vista
de cada câmera, no popup do marcador).

Cenário: 17 câmeras Wi-Fi 360° baratas (Yoosee / iCSee — Kapbom de poste + soquete E27),
espalhadas em 9 redes de roteador MR60X diferentes, atrás de um link **Starlink**.

---

## Resumo

Dá para fazer, mas há **3 obstáculos** nesse cenário antes de sair "ao vivo no mapa":

| Obstáculo | Por quê | Saída |
|---|---|---|
| **CGNAT do Starlink** | O plano residencial não dá IP público — não dá para "abrir porta" para a internet | Túnel de saída (Cloudflare Tunnel / Tailscale) ou IP público Starlink (plano Priority, mais caro) |
| **9 LANs isoladas** | Cada MR60X faz NAT próprio (é o desenho atual do projeto) — um servidor numa rede não enxerga câmera de outra | Pôr as câmeras numa **VLAN / SSID único**, ou usar os MR60X em modo AP (uma LAN plana só) |
| **RTSP na câmera** | Yoosee / iCSee às vezes tem RTSP escondido nas configurações, às vezes o firmware não tem | Testar 1 câmera: `rtsp://admin:SENHA@IP:554/onvif1` (principal) e `/onvif2` (sub-stream) |

---

## Caminhos, do mais simples ao mais completo

### Nível 0 — nada de obra (funciona hoje)

O app **Yoosee / CloudEdge** já faz ao vivo + gravação em nuvem, multi-câmera, e passa pelo
CGNAT (é P2P via nuvem do fabricante).

- No mapa dá para acrescentar um botão no popup: **"📹 Ver ao vivo (app Yoosee)"**.
- Custo zero, mas não é embutido e depende da nuvem do fabricante.

### Nível 1 — ver de fora, sem site

Um mini-PC ou Raspberry Pi na fazenda + **Tailscale** (VPN grátis).

- Você acessa as câmeras / o gravador de qualquer lugar pelo VPN.
- Bom para uso pessoal / família; **não** serve para link público no mapa.

### Nível 2 — ao vivo embutido no mapa (objetivo)

1. **Uma rede só para as câmeras** — as 17 no mesmo SSID / sub-rede (ou MR60X como AP).
2. **Hub na fazenda** — Pi 5 / mini-PC rodando:
   - **go2rtc** (leve, converte RTSP → WebRTC para o navegador), ou
   - **Frigate** (go2rtc + gravação local + detecção de movimento).
3. **Cloudflare Tunnel** (grátis) do hub → gera um `https://cameras.seudominio.com`
   com login (Cloudflare Access).
4. No popup de cada câmera do mapa, um player WebRTC apontando para esse endereço.
5. **Banda:** subir 17 streams juntos não cabe no Starlink — carregar **só ao clicar**,
   usando o sub-stream (~0,3–0,5 Mbps cada).

---

## Recomendação

- **Agora:** Nível 0 — colocar o link do app no popup; já dá "ao vivo" sem gastar nada.
- **Quando quiser de verdade no mapa:** Nível 2 com **Frigate + Cloudflare Tunnel**.
  Ganha também gravação local (não depende da nuvem) e alerta de movimento.
  Investimento: ~1 mini-PC / Pi + reorganizar a rede das câmeras.

---

## O que já pode ser deixado pronto no projeto

Adicionar um campo `stream` em `CAMERAS` (`src/fibra_dados.py`), hoje vazio:

- Quando a URL existir → o popup do mapa mostra o **player ao vivo**.
- Quando não existir → cai na **foto fixa** que já está em `docs/img/camera/<Local>.jpeg`.

Assim, no dia que o hub estiver no ar, basta preencher a URL e rodar `./build.sh` —
sem mexer em código.

---

## Passo a passo do Nível 2 (quando for fazer)

1. **Testar RTSP** numa câmera pelo app Yoosee/iCSee: procurar em *Configurações → Avançado*
   algo como "ONVIF" / "RTSP" e ativar. Testar no VLC: `rtsp://admin:SENHA@IP_DA_CAMERA:554/onvif1`.
   Se nenhuma variação funcionar, o firmware não expõe RTSP (só resta o app, ou trocar a câmera).
2. **Rede das câmeras:** decidir entre (a) um SSID único de câmeras em todos os MR60X na mesma
   faixa de IP, ou (b) MR60X em modo AP / bridge (uma LAN plana). Fixar IP de cada câmera por MAC.
3. **Hub:** instalar Frigate (Docker) no mini-PC/Pi; adicionar cada câmera com `rtsp` (sub-stream
   para visualização, principal para gravação). Disco: HD dedicado para as gravações.
4. **Acesso externo:** `cloudflared tunnel` no hub → rota para a porta do Frigate/go2rtc;
   proteger com Cloudflare Access (e-mail autorizado ou senha).
5. **Mapa:** preencher `stream` em `CAMERAS` com a URL WebRTC/HLS de cada câmera e `./build.sh`.

## Segurança

- Senha forte e única em cada câmera (trocar a padrão).
- Isolar a VLAN das câmeras da rede dos computadores da fazenda.
- Não expor a interface da câmera direto na internet — só o proxy (Frigate/go2rtc) através do
  túnel, com autenticação.
