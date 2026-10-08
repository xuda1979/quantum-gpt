set -euo pipefail
echo __ASI1_NET_PROBE_0604I__
python3 -c "import socket; print(socket.gethostbyname('iner.aihuanxin.cn'))" || true
command -v curl || true
command -v wget || true
python3 -c "import urllib.request; print(urllib.request.urlopen('https://iner.aihuanxin.cn', timeout=5).status)" || true
echo __ASI1_NET_PROBE_DONE__
