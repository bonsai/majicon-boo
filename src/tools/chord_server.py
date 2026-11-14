#!/usr/bin/env python3
"""dq-chord-drive PC receiver: DS chord events -> browser Web Audio.

The DS sends, on every bar, UDP FUDI text to port 7003:
    chord C#m7 61 64 68 71;      (chord name + MIDI notes)
    chord OFF;
This script re-streams them to the browser over SSE, and the page
strums the chord with the Web Audio API. Stdlib only — same relay
shape as the dq-oekaki / dq-beat servers.

Usage: python3 chord_server.py [http_port]   (default 8082)
Open the printed URL and press SOUND ON first (browser audio policy).
"""
import json
import queue
import socket
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

UDP_PORT = 7003
HTTP_PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8082

clients = []
clients_lock = threading.Lock()

PAGE = """<!DOCTYPE html>
<html lang="ja"><meta charset="utf-8"><title>DQ-CHORD-DRIVE</title>
<body style="background:#000;color:#fff;font-family:sans-serif;text-align:center">
<h1 style="letter-spacing:.2em">DQ-CHORD-DRIVE <span style="font-size:.5em">WEB AUDIO</span></h1>
<p id="st">DSからの接続待ち…（UDP 7003）</p>
<button id="on" style="font-size:1.2em;padding:.4em 1.2em">▶ SOUND ON</button>
<div style="margin:1em auto;width:480px;padding:1.2em 0;background:#000078;border:1px solid #fff">
  <div id="chord" style="font-size:3em;color:#ffd800">—</div>
  <div id="notes" style="color:#ccc;margin-top:.4em"></div>
</div>
<script>
let ac = null;
document.getElementById('on').onclick = () => {
  ac = new (window.AudioContext || window.webkitAudioContext)();
  document.getElementById('on').textContent = 'SOUND READY';
};
const NAMES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'];
function tone(freq, at, peak, dur, type) {
  const o = ac.createOscillator(), g = ac.createGain();
  o.type = type; o.frequency.value = freq;
  g.gain.setValueAtTime(0.0001, at);
  g.gain.exponentialRampToValueAtTime(peak, at + 0.02);
  g.gain.exponentialRampToValueAtTime(0.001, at + dur);
  o.connect(g).connect(ac.destination);
  o.start(at); o.stop(at + dur + 0.05);
}
function strum(notes) {
  if (!ac) return;
  const t = ac.currentTime;
  notes.forEach((n, i) => {
    const f = 440 * Math.pow(2, (n - 69) / 12);
    tone(f, t + i * 0.045, 0.28, 0.9, 'triangle');
  });
  const root = notes[0] - 24;
  tone(440 * Math.pow(2, (root - 69) / 12), t, 0.3, 1.1, 'sine');
}
const es = new EventSource('/events');
es.onopen = () => document.getElementById('st').textContent = '中継OK。DSで再生してください';
es.onmessage = (e) => {
  const m = JSON.parse(e.data);
  document.getElementById('chord').textContent = m.name;
  document.getElementById('notes').textContent =
    m.notes.map(n => NAMES[n % 12] + (Math.floor(n / 12) - 1)).join('  ');
  if (m.notes.length) strum(m.notes);
};
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
            parts = line.strip().rstrip(";").split()
            if len(parts) >= 2 and parts[0] == "chord":
                try:
                    notes = [int(p) for p in parts[2:]]
                except ValueError:
                    continue
                msg = "data: " + json.dumps({"name": parts[1], "notes": notes}) + "\n\n"
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
