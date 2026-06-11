"""
Simulador de Transmisión y Compresión de Señales — Grupo 12
Versión 4: Arquitectura modular (HTML, CSS, JS, Python separados)
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
from flask import Flask, request, jsonify, render_template

PORT = 5050
app = Flask(__name__, template_folder='templates', static_folder='static')

# Estado global: señal de audio cargada en servidor
audio_signal = {'t': None, 'y': None, 'name': None}

# ──────────────────────────────────────────────────────────────────────────
# Lógica de señales
# ──────────────────────────────────────────────────────────────────────────

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

# ──────────────────────────────────────────────────────────────────────────
# Rutas Flask
# ──────────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

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

# ──────────────────────────────────────────────────────────────────────────
# Arranque
# ──────────────────────────────────────────────────────────────────────────

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
