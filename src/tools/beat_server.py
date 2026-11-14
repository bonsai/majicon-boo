#!/usr/bin/env python3
"""dq-beat PC receiver (Web Audio version): DS hits -> browser sound.

The DS sends UDP FUDI text to port 7002:
    hit kick 0; / hit snare 0; / hit hat 0; / hit bass 36;
This script listens, re-streams the hits to the browser over SSE, and
the page synthesizes the four voices with the Web Audio API.
Stdlib only — same relay shape as dq-oekaki's server.

Usage: python3 beat_server.py [http_port]   (default 8081)
Then open the printed URL and press SOUND ON (browsers require a
click before audio can start).
"""
import json
import queue
import socket
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

UDP_PORT = 7002
HTTP_PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8081

clients = []
clients_lock = threading.Lock()

PAGE = """<!DOCTYPE html>
<html lang="ja"><meta charset="utf-8"><title>DQ-BEAT WEB</title>
<body style="background:#000;color:#fff;font-family:sans-serif;text-align:center">
<h1 style="letter-spacing:.2em">DQ-BEAT <span style="font-size:.5em">WEB AUDIO</span></h1>
<p id="st">DSからの接続待ち…（UDP 7002）</p>
<button id="on" style="font-size:1.2em;padding:.4em 1.2em">▶ SOUND ON</button>
<div style="margin:1.2em auto;display:flex;gap:10px;justify-content:center">
  <div id="kick" style="width:110px;padding:1.6em 0;background:#000078;border:1px solid #fff">KICK</div>
  <div id="snare" style="width:110px;padding:1.6em 0;background:#000078;border:1px solid #fff">SNARE</div>
  <div id="hat" style="width:110px;padding:1.6em 0;background:#000078;border:1px solid #fff">HAT</div>
  <div id="bass" style="width:110px;padding:1.6em 0;background:#000078;border:1px solid #fff">BASS</div>
</div>
<p id="last" style="color:#ffd800"></p>
<script>
let ac = null, noiseBuf = null;
document.getElementById('on').onclick = () => {
  ac = new (window.AudioContext || window.webkitAudioContext)();
  noiseBuf = ac.createBuffer(1, ac.sampleRate, ac.sampleRate);
  const d = noiseBuf.getChannelData(0);
  for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
  document.getElementById('on').textContent = 'SOUND READY';
};
function env(g, peak, dur) {
  const t = ac.currentTime;
  g.gain.setValueAtTime(peak, t);
  g.gain.exponentialRampToValueAtTime(0.001, t + dur);
}
function kick() {
  if (!ac) return;
  const t = ac.currentTime, o = ac.createOscillator(), g = ac.createGain();
  o.frequency.setValueAtTime(150, t);
  o.frequency.exponentialRampToValueAtTime(45, t + 0.12);
  env(g, 0.9, 0.24);
  o.connect(g).connect(ac.destination); o.start(); o.stop(t + 0.26);
}
function noiseHit(freq, type, peak, dur) {
  if (!ac) return;
  const t = ac.currentTime, src = ac.createBufferSource(), f = ac.createBiquadFilter(), g = ac.createGain();
  src.buffer = noiseBuf; f.type = type; f.frequency.value = freq;
  env(g, peak, dur);
  src.connect(f).connect(g).connect(ac.destination); src.start(); src.stop(t + dur + 0.02);
}
function bass(note) {
  if (!ac) return;
  const t = ac.currentTime, o = ac.createOscillator(), g = ac.createGain();
  o.type = 'triangle';
  o.frequency.value = 440 * Math.pow(2, (note - 69) / 12);
  env(g, 0.8, 0.22);
  o.connect(g).connect(ac.destination); o.start(); o.stop(t + 0.24);
}
const VOICES = { kick, snare: () => noiseHit(1800, 'bandpass', 0.7, 0.13),
                 hat: () => noiseHit(7500, 'highpass', 0.4, 0.05), bass };
const es = new EventSource('/events');
es.onopen = () => document.getElementById('st').textContent = '中継OK。DSで再生してください';
es.onmessage = (e) => {
  const m = JSON.parse(e.data);
  const pad = document.getElementById(m.track);
  if (pad) { pad.style.background = '#ffd800'; pad.style.color = '#000';
    setTimeout(() => { pad.style.background = '#000078'; pad.style.color = '#fff'; }, 90); }
  document.getElementById('last').textContent = m.track.toUpperCase() + (m.track === 'bass' ? ' note ' + m.note : '');
  const v = VOICES[m.track];
  if (v) v(m.note);
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
            if len(parts) == 3 and parts[0] == "hit":
                try:
                    note = int(parts[2])
                except ValueError:
                    continue
                msg = "data: " + json.dumps({"track": parts[1], "note": note}) + "\n\n"
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
