"""
Simulador de Transmisión y Compresión de Señales — Grupo 12
Versión 3: upload real de WAV via FormData
"""

import sys, subprocess, threading, time, math, random, webbrowser, struct, io, os

# ── Instalar Flask si falta ───────────────────────────────────────────────────
def ensure_flask():
    try:
        import flask; return
    except ImportError:
        pass
    try:
        import tkinter as tk
        from tkinter import ttk
        root = tk.Tk()
        root.title("Instalando dependencias...")
        root.geometry("380x120")
        root.resizable(False, False)
        tk.Label(root, text="Instalando Flask por primera vez...\n(requiere conexión a internet)", pady=12).pack()
        bar = ttk.Progressbar(root, mode='indeterminate', length=320)
        bar.pack(pady=4); bar.start(10); root.update()
        ok = [False]
        def do_install():
            r = subprocess.run([sys.executable,"-m","pip","install","flask","--quiet"], capture_output=True)
            ok[0] = (r.returncode == 0)
            root.after(0, root.destroy)
        threading.Thread(target=do_install, daemon=True).start()
        root.mainloop()
        if not ok[0]:
            import tkinter.messagebox as mb
            mb.showerror("Error","No se pudo instalar Flask.\nVerificá tu conexión a internet.")
            sys.exit(1)
    except Exception:
        subprocess.run([sys.executable,"-m","pip","install","flask","--quiet"])

ensure_flask()
from flask import Flask, request, jsonify, Response

PORT = 5050
app  = Flask(__name__)

# Estado global: señal de audio cargada en servidor
audio_signal = {'t': None, 'y': None, 'name': None}

# ─────────────────────────────────────────────────────────────────────────────
#  HTML embebido
# ─────────────────────────────────────────────────────────────────────────────
HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Simulador — Transmisión y Compresión de Señales</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
:root{--bg:#0f172a;--card:#1e293b;--border:#334155;--text:#f8fafc;--muted:#94a3b8;--primary:#38bdf8;--primary2:#0ea5e9;--orange:#fb923c;--red:#f43f5e;--green:#4ade80;--yellow:#facc15}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--text);padding:28px 20px 60px;min-height:100vh}
.container{max-width:1150px;margin:0 auto}
header{text-align:center;margin-bottom:30px}
header h1{font-size:1.75rem;font-weight:700;letter-spacing:-.02em}
header p{color:var(--muted);margin-top:5px;font-size:.9rem}
.badge{display:inline-block;margin-top:8px;background:#1e3a5f;color:var(--primary);border:1px solid #2563a8;border-radius:20px;padding:3px 14px;font-size:.75rem;font-weight:600;letter-spacing:.04em}
.panel{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:24px;margin-bottom:24px}
.panel-title{font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:var(--muted);margin-bottom:16px;display:flex;align-items:center;gap:8px}
.panel-title::after{content:'';flex:1;height:1px;background:var(--border)}
.source-tabs{display:flex;gap:8px;margin-bottom:18px}
.tab-btn{padding:7px 18px;border-radius:6px;border:1px solid var(--border);background:transparent;color:var(--muted);font-size:.85rem;font-weight:600;cursor:pointer;transition:all .15s}
.tab-btn.active{background:var(--primary);color:#0f172a;border-color:var(--primary)}
.controls{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;align-items:end}
@media(max-width:750px){.controls{grid-template-columns:1fr}}
.field label{display:block;font-size:.78rem;font-weight:600;color:var(--primary);margin-bottom:7px;text-transform:uppercase;letter-spacing:.05em}
select{width:100%;padding:10px 13px;background:var(--bg);border:1px solid var(--border);border-radius:7px;color:var(--text);font-size:.88rem;outline:none;cursor:pointer}
select:focus{border-color:var(--primary)}
.range-row{display:flex;align-items:center;gap:10px}
input[type=range]{flex:1;cursor:pointer;accent-color:var(--primary)}
.range-val{font-weight:700;font-size:.9rem;min-width:38px;text-align:right}
.btn{padding:11px 24px;background:var(--primary);color:#0f172a;border:none;border-radius:7px;font-weight:700;font-size:.9rem;cursor:pointer;width:100%;transition:background .15s,transform .1s;display:flex;align-items:center;justify-content:center;gap:8px}
.btn:hover{background:var(--primary2)}.btn:active{transform:scale(.97)}.btn:disabled{opacity:.5;cursor:not-allowed}
.btn-upload{background:var(--card);color:var(--primary);border:1px solid var(--primary);border-radius:7px;padding:10px 18px;font-weight:600;font-size:.88rem;cursor:pointer;transition:all .15s;display:inline-flex;align-items:center;gap:8px}
.btn-upload:hover{background:#1e3a5f}
.audio-zone{border:2px dashed var(--border);border-radius:10px;padding:24px;text-align:center;transition:border-color .2s}
.audio-zone:hover{border-color:var(--primary)}
.audio-zone input[type=file]{display:none}
#audioStatus{margin-top:12px;font-size:.83rem;min-height:20px}
.status-ok{color:var(--green)}.status-err{color:var(--red)}.status-loading{color:var(--yellow)}
.metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));gap:12px;margin-bottom:24px}
.metric{background:var(--card);border:1px solid var(--border);border-radius:9px;padding:14px 16px;text-align:center}
.metric p{font-size:.68rem;text-transform:uppercase;letter-spacing:.07em;color:var(--muted);margin-bottom:7px}
.metric span{font-size:1.2rem;font-weight:700}
.pipeline{display:flex;align-items:center;justify-content:center;gap:0;margin-bottom:24px;flex-wrap:wrap}
.pipe-step{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:10px 16px;text-align:center;min-width:110px}
.pipe-step .icon{font-size:1.2rem;margin-bottom:3px}
.pipe-step .name{font-size:.7rem;font-weight:700;text-transform:uppercase;color:var(--muted)}
.pipe-step .val{font-size:.78rem;color:var(--text);margin-top:2px;font-weight:600}
.pipe-arrow{color:var(--border);font-size:1.4rem;margin:0 4px}
.chart-grid{display:grid;gap:18px}
.chart-row{display:grid;grid-template-columns:1fr 1fr;gap:18px}
@media(max-width:680px){.chart-row{grid-template-columns:1fr}}
.chart-box{background:var(--card);border:1px solid var(--border);border-radius:11px;padding:18px}
.chart-box h4{font-size:.75rem;font-weight:700;color:var(--muted);margin-bottom:12px;text-transform:uppercase;letter-spacing:.05em;display:flex;align-items:center;gap:6px}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block;flex-shrink:0}
.chart-wrap{position:relative;height:200px}
.chart-overlap-wrap{position:relative;height:220px}
.section-header{font-size:.95rem;font-weight:600;border-left:3px solid var(--primary);padding-left:11px;margin-bottom:16px}
#results{display:none;animation:fadeUp .3s ease}
footer{text-align:center;color:var(--muted);font-size:.75rem;margin-top:40px}
.spinner{width:16px;height:16px;border:3px solid #0f172a55;border-top-color:#0f172a;border-radius:50%;animation:spin .7s linear infinite}
.tag{display:inline-block;background:#1e3a5f;color:var(--primary);border-radius:4px;padding:1px 6px;font-size:.66rem;font-weight:700;margin-right:5px}
@keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
@keyframes spin{to{transform:rotate(360deg)}}
</style>
</head>
<body>
<div class="container">

<header>
  <h1>Transmisión Digital y Compresión de Señales</h1>
  <p>Simulador de procesamiento en entornos Cliente–Servidor</p>
  <span class="badge">Grupo 12 · Etapa 2</span>
</header>

<!-- FUENTE -->
<div class="panel">
  <div class="panel-title">Fuente de señal</div>
  <div class="source-tabs">
    <button class="tab-btn active" onclick="setSource('sine')">📈 Seno sintético</button>
    <button class="tab-btn" onclick="setSource('audio')">🎵 Audio WAV</button>
  </div>

  <div id="srcSine">
    <p style="color:var(--muted);font-size:.85rem">Se genera un seno puro de 300 muestras (2 ciclos completos, 0 → 4π).</p>
  </div>

  <div id="srcAudio" style="display:none">
    <div class="field" style="margin-bottom:12px">
      <label style="margin-bottom:10px;display:block">Cargar archivo WAV</label>
      <input type="file" id="audioFile" accept=".wav,audio/wav,audio/x-wav"
             style="width:100%;padding:8px;background:var(--bg);border:1px solid var(--border);border-radius:7px;color:var(--text);cursor:pointer"
             onchange="onAudioFileSelected(this)">
      <p style="color:var(--muted);font-size:.8rem;margin-top:8px">
        Al seleccionar el archivo se lee automáticamente y aparece la vista previa abajo.
      </p>
    </div>
    <div id="audioStatus"></div>
  </div>
</div>

<!-- PREVIEW -->
<div id="previewPanel" class="panel" style="display:none">
  <div class="panel-title">Vista previa — señal leída</div>
  <p id="previewMeta" style="color:var(--muted);font-size:.84rem;margin-bottom:14px"></p>
  <div class="chart-box">
    <h4><span class="dot" style="background:#38bdf8"></span><span id="previewTitle">Señal cargada</span></h4>
    <div class="chart-wrap" style="height:240px"><canvas id="cPreview"></canvas></div>
  </div>
</div>

<!-- PARÁMETROS -->
<div class="panel">
  <div class="panel-title">Parámetros de transmisión</div>
  <div class="controls">
    <div class="field">
      <label><span class="tag">Paso 2</span>Compresión</label>
      <select id="compression">
        <option value="none">Sin compresión</option>
        <option value="samples">Submuestreo (1 de cada 6)</option>
        <option value="quantization">Cuantización (8 niveles)</option>
      </select>
    </div>
    <div class="field">
      <label><span class="tag">Paso 3a</span>Ruido gaussiano</label>
      <div class="range-row">
        <input type="range" id="noise" min="0" max="100" value="0"
               oninput="document.getElementById('noiseVal').textContent=this.value+'%'">
        <span class="range-val" id="noiseVal">0%</span>
      </div>
    </div>
    <div class="field">
      <label><span class="tag">Paso 3b</span>Pérdida de paquetes</label>
      <div class="range-row">
        <input type="range" id="packetloss" min="0" max="50" value="0"
               oninput="document.getElementById('plVal').textContent=this.value+'%'">
        <span class="range-val" id="plVal">0%</span>
      </div>
    </div>
  </div>
  <div style="margin-top:16px;max-width:220px">
    <button class="btn" id="btnTx" onclick="transmit()">
      <span id="btnText">▶ Generar y Transmitir</span>
      <div class="spinner" id="spinner" style="display:none"></div>
    </button>
  </div>
</div>

<!-- RESULTADOS -->
<div id="results">
  <div class="section-header">Paso 5 — Monitoreo y métricas de recepción</div>

  <div class="pipeline">
    <div class="pipe-step"><div class="icon">📡</div><div class="name">Original</div><div class="val" id="pp_orig">—</div></div>
    <div class="pipe-arrow">→</div>
    <div class="pipe-step"><div class="icon">🗜️</div><div class="name">Comprimido</div><div class="val" id="pp_comp">—</div></div>
    <div class="pipe-arrow">→</div>
    <div class="pipe-step"><div class="icon">📶</div><div class="name">Canal</div><div class="val" id="pp_canal">—</div></div>
    <div class="pipe-arrow">→</div>
    <div class="pipe-step"><div class="icon">🖥️</div><div class="name">Reconstruido</div><div class="val" id="pp_recon">—</div></div>
  </div>

  <div class="metrics">
    <div class="metric"><p>Tamaño original</p><span id="m_orig">—</span></div>
    <div class="metric"><p>Tamaño comprimido</p><span id="m_comp" style="color:var(--orange)">—</span></div>
    <div class="metric"><p>Tasa de compresión</p><span id="m_pct" style="color:var(--primary)">—</span></div>
    <div class="metric"><p>Ruido aplicado</p><span id="m_noise" style="color:var(--yellow)">—</span></div>
    <div class="metric"><p>Pérdida de paquetes</p><span id="m_pl" style="color:var(--orange)">—</span></div>
    <div class="metric"><p>Error MSE</p><span id="m_err" style="color:var(--red)">—</span></div>
  </div>

  <div class="chart-grid">
    <div class="chart-box">
      <h4><span class="dot" style="background:#38bdf8"></span>Señal Original</h4>
      <div class="chart-wrap"><canvas id="cOrig"></canvas></div>
    </div>
    <div class="chart-row">
      <div class="chart-box">
        <h4><span class="dot" style="background:#fb923c"></span>Comprimida <span style="color:var(--muted);font-weight:400;text-transform:none">(antes de Tx)</span></h4>
        <div class="chart-wrap"><canvas id="cComp"></canvas></div>
      </div>
      <div class="chart-box">
        <h4><span class="dot" style="background:#facc15"></span>En canal <span style="color:var(--muted);font-weight:400;text-transform:none">(ruido + pérdidas)</span></h4>
        <div class="chart-wrap"><canvas id="cChan"></canvas></div>
      </div>
    </div>
    <div class="chart-box">
      <h4>
        <span class="dot" style="background:#38bdf8"></span>Original &nbsp;vs&nbsp;
        <span class="dot" style="background:#f43f5e"></span>Reconstruida
        <span style="color:var(--muted);font-weight:400;text-transform:none;margin-left:4px">(comparación directa)</span>
      </h4>
      <div class="chart-overlap-wrap"><canvas id="cOver"></canvas></div>
    </div>
  </div>
</div>

<footer>Simulador local · 100% offline tras primera ejecución · Grupo 12</footer>
</div>

<script>
let charts = {};
let currentSource = 'sine';
let audioReady = false;
let previewCache = null;

// ── Fuente ───────────────────────────────────────────────────────────────────
async function setSource(src) {
  currentSource = src;
  document.querySelectorAll('.tab-btn').forEach((b,i) =>
    b.classList.toggle('active', (i===0&&src==='sine')||(i===1&&src==='audio')));
  document.getElementById('srcSine').style.display  = src==='sine'  ? '' : 'none';
  document.getElementById('srcAudio').style.display = src==='audio' ? '' : 'none';
  if (src === 'sine') {
    await loadSinePreview();
  } else {
    const fileInput = document.getElementById('audioFile');
    const pending = fileInput && fileInput.files && fileInput.files[0];
    if (pending && !audioReady) await uploadAudio(pending);
    else if (audioReady && previewCache) renderPreview(previewCache);
    else hidePreview();
  }
}

// ── Drag & drop (toda la zona de audio) ─────────────────────────────────────
function onAudioFileSelected(input) {
  const file = input.files && input.files[0];
  if (file) uploadAudio(file);
}

document.addEventListener('DOMContentLoaded', () => {
  const zone = document.getElementById('srcAudio');
  if (!zone) return;
  zone.addEventListener('dragover', ev => ev.preventDefault());
  zone.addEventListener('drop', ev => {
    ev.preventDefault();
    const file = ev.dataTransfer.files[0];
    if (file && file.name.toLowerCase().endsWith('.wav')) {
      uploadAudio(file);
    } else {
      setAudioStatus('error', '❌ Solo se aceptan archivos .wav');
    }
  });
});

// ── Upload real al servidor ──────────────────────────────────────────────────
function setAudioStatus(type, msg) {
  const el = document.getElementById('audioStatus');
  el.className = type === 'ok' ? 'status-ok' : type === 'error' ? 'status-err' : 'status-loading';
  el.textContent = msg;
}

async function uploadAudio(file) {
  if (!file) return false;
  if (!file.name.toLowerCase().endsWith('.wav')) {
    setAudioStatus('error', '❌ Solo se aceptan archivos .wav');
    audioReady = false;
    return false;
  }

  setAudioStatus('loading', '⏳ Leyendo y analizando WAV...');
  audioReady = false;
  hidePreview();
  document.getElementById('results').style.display = 'none';

  const fd = new FormData();
  fd.append('file', file);

  try {
    const res = await fetch('/upload_audio', { method: 'POST', body: fd });
    if (!res.ok) throw new Error('El servidor no pudo leer el archivo (HTTP ' + res.status + ')');
    const d = await res.json();
    if (d.error) {
      setAudioStatus('error', '❌ ' + d.error);
      return false;
    }

    audioReady = true;
    previewCache = {
      t: d.t, y: d.y,
      title: d.name,
      meta: `${d.duration_ms} ms · ${d.sample_rate} Hz · ${d.channels} ch · ${d.samples} muestras`,
      xLabel: 'Tiempo (s)'
    };
    if (charts.preview) renderPreview(previewCache);
    setAudioStatus('ok', `✅ ${d.name} leído — ya podés transmitir con ruido y compresión`);
    return true;
  } catch(e) {
    setAudioStatus('error', '❌ Error: ' + e.message);
    return false;
  }
}

async function loadSinePreview() {
  try {
    const res = await fetch('/preview/sine');
    const d = await res.json();
    previewCache = {
      t: d.t, y: d.y,
      title: 'Seno sintético',
      meta: '300 muestras · 2 ciclos completos (0 → 4π rad)',
      xLabel: 'Fase (rad)'
    };
    renderPreview(previewCache);
  } catch(e) { /* silencioso */ }
}

function hidePreview() {
  document.getElementById('previewPanel').style.display = 'none';
}

function renderPreview(data) {
  document.getElementById('previewPanel').style.display = 'block';
  document.getElementById('previewTitle').textContent = data.title;
  document.getElementById('previewMeta').textContent = data.meta;
  setChart(charts.preview, data.t, data.y, data.xLabel);
}

// ── Charts ───────────────────────────────────────────────────────────────────
function yBounds(...arrays) {
  let mn = Infinity, mx = -Infinity;
  arrays.flat().forEach(v => { if (v < mn) mn = v; if (v > mx) mx = v; });
  const pad = Math.max((mx - mn) * 0.12, 0.05);
  return { min: mn - pad, max: mx + pad };
}

function makeChart(id, datasets, showX = false) {
  const ctx = document.getElementById(id).getContext('2d');
  return new Chart(ctx, {
    type: 'line',
    data: { labels: [], datasets },
    options: {
      animation: { duration: 350 },
      plugins: { legend: { display: datasets.length > 1,
        labels: { color: '#94a3b8', boxWidth: 10, font: { size: 11 } } } },
      responsive: true, maintainAspectRatio: false,
      scales: {
        y: { grid: { color: '#334155' }, ticks: { color: '#94a3b8', maxTicksLimit: 5 } },
        x: {
          grid: { display: false },
          ticks: {
            display: showX,
            color: '#94a3b8',
            maxTicksLimit: 6,
            callback: (_, i, arr) => arr[i]?.label ?? ''
          }
        }
      }
    }
  });
}

window.onload = async () => {
  charts.preview = makeChart('cPreview', [{label:'Señal', data:[], borderColor:'#38bdf8', borderWidth:2, pointRadius:0, backgroundColor:'#38bdf820', fill:true, tension:.25}], true);
  charts.orig = makeChart('cOrig', [{label:'Original',   data:[], borderColor:'#38bdf8', borderWidth:2, pointRadius:0, backgroundColor:'#38bdf815', fill:true, tension:.3}]);
  charts.comp = makeChart('cComp', [{label:'Comprimida', data:[], borderColor:'#fb923c', borderWidth:2, pointRadius:3, backgroundColor:'#fb923c15', fill:true, tension:.2}]);
  charts.chan  = makeChart('cChan', [{label:'Canal',      data:[], borderColor:'#facc15', borderWidth:1.5,pointRadius:0, backgroundColor:'#facc1510', fill:true, tension:.1}]);
  charts.over  = makeChart('cOver', [
    {label:'Original',     data:[], borderColor:'#38bdf8', borderWidth:2, pointRadius:0, backgroundColor:'transparent', fill:false, tension:.3},
    {label:'Reconstruida', data:[], borderColor:'#f43f5e', borderWidth:2, pointRadius:0, backgroundColor:'transparent', fill:false, tension:.3}
  ]);
  await loadSinePreview();
};

function setChart(chart, t, ...ys) {
  const xLabel = typeof ys[ys.length - 1] === 'string' ? ys.pop() : null;
  chart.data.labels = t.map(v => Number(v).toFixed(3));
  ys.forEach((y, i) => { chart.data.datasets[i].data = y; });
  const b = yBounds(...ys);
  chart.options.scales.y.min = b.min;
  chart.options.scales.y.max = b.max;
  if (xLabel) chart.options.scales.x.title = { display: true, text: xLabel, color: '#64748b', font: { size: 11 } };
  chart.update();
}

// ── Transmitir ───────────────────────────────────────────────────────────────
async function transmit() {
  if (currentSource === 'audio') {
    const fileInput = document.getElementById('audioFile');
    const pending = fileInput && fileInput.files && fileInput.files[0];

    // Si hay archivo seleccionado pero aún no se procesó, lo leemos ahora
    if (!audioReady && pending) {
      const ok = await uploadAudio(pending);
      if (!ok) return;
    }

    if (!audioReady) {
      alert('Por favor cargá un archivo WAV primero.\n\nElegí un .wav y esperá el mensaje verde de confirmación con la vista previa.');
      return;
    }
  }
  const btn = document.getElementById('btnTx');
  const txt = document.getElementById('btnText');
  const sp  = document.getElementById('spinner');
  btn.disabled = true; txt.style.display = 'none'; sp.style.display = 'block';

  try {
    const res = await fetch('/transmit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        source:      currentSource,
        compression: document.getElementById('compression').value,
        noise_level: +document.getElementById('noise').value,
        packet_loss: +document.getElementById('packetloss').value,
      })
    });
    const d = await res.json();
    if (d.error) { alert('Error: ' + d.error); return; }

    setChart(charts.orig, d.t_orig, d.y_orig);
    setChart(charts.comp, d.t_comp, d.y_comp);
    setChart(charts.chan,  d.t_orig, d.y_chan);
    setChart(charts.over,  d.t_orig, d.y_orig, d.y_recon);

    document.getElementById('m_orig').textContent  = d.metrics.size_orig;
    document.getElementById('m_comp').textContent  = d.metrics.size_comp;
    document.getElementById('m_pct').textContent   = d.metrics.comp_percent;
    document.getElementById('m_noise').textContent = d.metrics.noise;
    document.getElementById('m_pl').textContent    = d.metrics.packet_loss;
    document.getElementById('m_err').textContent   = d.metrics.mse;

    document.getElementById('pp_orig').textContent  = d.metrics.size_orig;
    document.getElementById('pp_comp').textContent  = d.metrics.size_comp;
    document.getElementById('pp_canal').textContent = `R:${d.metrics.noise} PL:${d.metrics.packet_loss}`;
    document.getElementById('pp_recon').textContent = d.metrics.size_orig;

    document.getElementById('results').style.display = 'block';
  } catch(e) {
    alert('Error: ' + e.message);
  } finally {
    btn.disabled = false; txt.style.display = 'block'; sp.style.display = 'none';
  }
}
</script>
</body>
</html>"""

# ─────────────────────────────────────────────────────────────────────────────
#  Lógica de señales
# ─────────────────────────────────────────────────────────────────────────────
N  = 300
TM = 4 * math.pi

def gen_sine(n=N):
    t = [i * TM / (n-1) for i in range(n)]
    y = [math.sin(x) for x in t]
    return t, y

def parse_wav(file_bytes, target_n=N):
    """Lee un WAV, normaliza amplitud y remuestrea a target_n puntos con eje temporal real."""
    import wave as wv
    buf = io.BytesIO(file_bytes)
    try:
        with wv.open(buf) as w:
            n_ch   = w.getnchannels()
            sw     = w.getsampwidth()
            rate   = w.getframerate()
            n_fr   = w.getnframes()
            frames = w.readframes(n_fr)
    except Exception as e:
        raise ValueError(f"No se pudo leer el WAV: {e}")

    fmt = {1: 'b', 2: 'h', 4: 'i'}.get(sw)
    if fmt is None:
        raise ValueError(f"Profundidad no soportada: {sw * 8} bits")
    total   = n_fr * n_ch
    samples = list(struct.unpack(f'<{total}{fmt}', frames))
    if n_ch > 1:
        samples = samples[::n_ch]

    max_val = 2 ** (sw * 8 - 1)
    samples = [s / max_val for s in samples]
    if not samples:
        raise ValueError("El WAV está vacío.")

    orig_n = len(samples)
    duration_ms = round(n_fr / rate * 1000)

    if orig_n == 1:
        return [0.0], samples[:], rate, n_ch, n_fr, duration_ms

    t_out, out = [], []
    for i in range(target_n):
        pos  = i * (orig_n - 1) / (target_n - 1)
        lo   = int(pos)
        hi   = min(lo + 1, orig_n - 1)
        frac = pos - lo
        out.append(samples[lo] + frac * (samples[hi] - samples[lo]))
        t_out.append(pos / rate)

    return t_out, out, rate, n_ch, n_fr, duration_ms

def compress_samples(t, y, factor=6):
    return t[::factor], y[::factor]

def compress_quant(t, y, levels=8):
    mn, mx = min(y), max(y)
    rng = mx - mn
    if rng == 0: return t, y[:]
    step = rng / levels
    yq = [round((v - mn) / step) * step + mn for v in y]
    return t, yq

def add_noise(y, pct):
    if pct == 0: return y[:]
    amp = 0.015 * pct
    return [v + random.gauss(0, amp) for v in y]

def apply_packet_loss(y, loss_pct):
    if loss_pct == 0: return y[:]
    out  = y[:]
    last = y[0]
    for i in range(len(out)):
        if random.random() < loss_pct / 100:
            out[i] = last
        else:
            last = out[i]
    return out

def reconstruct(tc, yc, to):
    out = []
    for tv in to:
        if tv <= tc[0]:  out.append(yc[0]);  continue
        if tv >= tc[-1]: out.append(yc[-1]); continue
        for i in range(len(tc)-1):
            if tc[i] <= tv <= tc[i+1]:
                r = (tv - tc[i]) / (tc[i+1] - tc[i])
                out.append(yc[i] + r * (yc[i+1] - yc[i]))
                break
    return out

def mse(a, b):
    n = min(len(a), len(b))
    if n == 0: return 0
    return sum((x-y)**2 for x,y in zip(a[:n], b[:n])) / n

# ─────────────────────────────────────────────────────────────────────────────
#  Rutas Flask
# ─────────────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return Response(HTML, mimetype='text/html')

@app.route('/preview/sine')
def preview_sine():
    t, y = gen_sine()
    return jsonify({'t': t, 'y': y})

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    """Recibe el WAV, lo parsea, guarda la señal y devuelve datos para visualizar."""
    if 'file' not in request.files:
        return jsonify({'error': 'No se recibió archivo.'})
    f = request.files['file']
    if not f.filename.lower().endswith('.wav'):
        return jsonify({'error': 'Solo se aceptan archivos .wav'})
    try:
        file_bytes = f.read()
        t, y, rate, n_ch, n_fr, dur_ms = parse_wav(file_bytes)
        audio_signal['t']    = t
        audio_signal['y']    = y
        audio_signal['name'] = f.filename
        return jsonify({
            'name':        f.filename,
            'sample_rate': rate,
            'channels':    n_ch,
            'samples':     len(y),
            'duration_ms': dur_ms,
            't':           t,
            'y':           y,
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/transmit', methods=['POST'])
def transmit():
    try:
        body      = request.get_json()
        source    = body.get('source', 'sine')
        comp      = body.get('compression', 'none')
        noise_pct = int(body.get('noise_level', 0))
        pl_pct    = int(body.get('packet_loss', 0))

        # 1. Señal original
        if source == 'audio':
            if audio_signal['t'] is None:
                return jsonify({'error': 'No hay audio cargado en el servidor.'})
            t_orig = audio_signal['t']
            y_orig = audio_signal['y']
        else:
            t_orig, y_orig = gen_sine()

        # 2. Comprimir
        if comp == 'samples':
            tc, yc = compress_samples(t_orig, y_orig)
        elif comp == 'quantization':
            tc, yc = compress_quant(t_orig, y_orig)
        else:
            tc, yc = t_orig[:], y_orig[:]

        # 3a. Ruido
        yc_noisy = add_noise(yc, noise_pct)
        # 3b. Pérdida de paquetes
        yc_channel = apply_packet_loss(yc_noisy, pl_pct)

        # 4. Reconstruir
        y_recon = reconstruct(tc, yc_channel, t_orig)
        y_chan  = reconstruct(tc, yc_channel, t_orig)

        pct   = 100 * (1 - len(yc) / len(y_orig))
        error = mse(y_orig, y_recon)

        return jsonify({
            't_orig':  t_orig, 'y_orig':  y_orig,
            't_comp':  tc,     'y_comp':  yc,
            'y_chan':  y_chan,
            't_recon': t_orig, 'y_recon': y_recon,
            'metrics': {
                'size_orig':    f'{len(y_orig)} muestras',
                'size_comp':    f'{len(yc)} muestras',
                'comp_percent': f'{pct:.1f}%',
                'noise':        f'{noise_pct}%',
                'packet_loss':  f'{pl_pct}%',
                'mse':          f'{error:.6f}'
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)})

# ─────────────────────────────────────────────────────────────────────────────
#  Arranque
# ─────────────────────────────────────────────────────────────────────────────
def run_flask():
    import logging
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    app.run(host='127.0.0.1', port=PORT, debug=False, use_reloader=False)

def main():
    threading.Thread(target=run_flask, daemon=True).start()

    import socket
    for _ in range(30):
        try:
            with socket.create_connection(('127.0.0.1', PORT), timeout=0.3): break
        except OSError:
            time.sleep(0.15)

    webbrowser.open(f'http://127.0.0.1:{PORT}')

    try:
        import tkinter as tk
        root = tk.Tk()
        root.title("Simulador — Grupo 12")
        root.geometry("320x115")
        root.resizable(False, False)
        root.configure(bg="#0f172a")
        tk.Label(root, text="✅  Simulador en ejecución",
                 bg="#0f172a", fg="#38bdf8", font=("Segoe UI", 12, "bold")).pack(pady=(18,4))
        tk.Label(root, text=f"http://127.0.0.1:{PORT}",
                 bg="#0f172a", fg="#94a3b8", font=("Segoe UI", 9)).pack()
        tk.Label(root, text="Cerrá esta ventana para detener la app.",
                 bg="#0f172a", fg="#64748b", font=("Segoe UI", 8)).pack(pady=(8,0))
        root.mainloop()
    except Exception:
        print("Simulador en http://127.0.0.1:{PORT} — Ctrl+C para cerrar".format(PORT=PORT))
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            pass

if __name__ == '__main__':
    main()
