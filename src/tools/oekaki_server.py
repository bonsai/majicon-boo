#!/usr/bin/env python3
"""dq-oekaki PC receiver: DS strokes -> browser canvas, stdlib only.

The DS sends UDP text events to port 7001 (broadcast):
    D x y / M x y / U / COL RRGGBB / CLR      (canvas coords: 240x152)
This script listens for them and re-streams them to the browser page
over Server-Sent Events. Open the printed URL in a browser on the
same LAN as the DS, then draw on the DS.

Usage: python3 oekaki_server.py [http_port]   (default 8080)
"""
import json
import queue
import socket
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

UDP_PORT = 7001
HTTP_PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080

clients = []
clients_lock = threading.Lock()

PAGE = """<!DOCTYPE html>
<html lang="ja"><meta charset="utf-8"><title>DQ-OEKAKI</title>
<body style="background:#000;color:#fff;font-family:sans-serif;text-align:center">
<h1 style="letter-spacing:.2em">DQ-OEKAKI</h1>
<p id="st">DSからの接続待ち…（UDP 7001）</p>
<canvas id="cv" width="240" height="152" style="width:720px;height:456px;image-rendering:pixelated;background:#000078;border:1px solid #fff"></canvas>
<p><button id="save">PNGで保存</button> <button id="clear">画面クリア（表示のみ）</button></p>
<script>
const cv = document.getElementById('cv'), ctx = cv.getContext('2d');
ctx.fillStyle = '#000078'; ctx.fillRect(0, 0, 240, 152);
ctx.strokeStyle = '#fff'; ctx.fillStyle = '#fff'; ctx.lineWidth = 1.6; ctx.lineCap = 'round';
let pen = false, x = 0, y = 0;
const es = new EventSource('/events');
es.onopen = () => document.getElementById('st').textContent = '中継OK。DSで描いてください';
es.onmessage = (e) => {
  const t = JSON.parse(e.data).line.split(' ');
  if (t[0] === 'D') { pen = true; x = +t[1]; y = +t[2]; ctx.fillRect(x, y, 1.6, 1.6); }
  else if (t[0] === 'M' && pen) { ctx.beginPath(); ctx.moveTo(x, y); x = +t[1]; y = +t[2]; ctx.lineTo(x, y); ctx.stroke(); }
  else if (t[0] === 'U') pen = false;
  else if (t[0] === 'COL') { ctx.strokeStyle = '#' + t[1]; ctx.fillStyle = '#' + t[1]; }
  else if (t[0] === 'CLR') { ctx.fillStyle = '#000078'; ctx.fillRect(0, 0, 240, 152); ctx.fillStyle = ctx.strokeStyle; }
};
document.getElementById('save').onclick = () => {
  const a = document.createElement('a');
  a.download = 'dq-oekaki.png'; a.href = cv.toDataURL('image/png'); a.click();
};
document.getElementById('clear').onclick = () => { ctx.fillStyle = '#000078'; ctx.fillRect(0, 0, 240, 152); };
</script></body></html>
"""


def udp_loop():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", UDP_PORT))
    print(f"UDP listening on {UDP_PORT}")
    while True:
        data, _ = sock.recvfrom(4096)
        for line in data.decode("ascii", "replace").splitlines():
            line = line.strip()
            if not line:
                continue
            msg = "data: " + json.dumps({"line": line}) + "\n\n"
            with clients_lock:
                dead = []
                for q in clients:
                    try:
                        q.put_nowait(msg)
                    except queue.Full:
                        dead.append(q)
                for q in dead:
                    clients.remove(q)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.path == "/":
            body = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            q = queue.Queue(maxsize=512)
            with clients_lock:
                clients.append(q)
            try:
                while True:
                    self.wfile.write(q.get(timeout=15).encode("utf-8"))
                    self.wfile.flush()
            except Exception:
                pass
            finally:
                with clients_lock:
                    if q in clients:
                        clients.remove(q)
        else:
            self.send_error(404)


if __name__ == "__main__":
    threading.Thread(target=udp_loop, daemon=True).start()
    try:
        host_ip = socket.gethostbyname(socket.gethostname())
    except Exception:
        host_ip = "127.0.0.1"
    print(f"Open in a browser:  http://{host_ip}:{HTTP_PORT}/   (or http://127.0.0.1:{HTTP_PORT}/)")
    ThreadingHTTPServer(("0.0.0.0", HTTP_PORT), Handler).serve_forever()
