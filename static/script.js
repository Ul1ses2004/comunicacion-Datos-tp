let charts = {};
let currentSource = 'sine';
let audioReady = false;
let previewCache = null;

// ── Fuente ─────────────────────────────────────────────────────────────
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

// ── Drag & drop ─────────────────────────────────────────────────────────────
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

// ── Charts ─────────────────────────────────────────────────────────────
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

// ── Transmitir ──────────────────────────────────────────────────────────
async function transmit() {
  if (currentSource === 'audio') {
    const fileInput = document.getElementById('audioFile');
    const pending = fileInput && fileInput.files && fileInput.files[0];

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