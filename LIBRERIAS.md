# 📚 Librerías utilizadas en el Simulador

## **Python**

### 1. **sys**
```python
import sys
```
- **Propósito:** Acceso a variables y funciones específicas del sistema
- **Uso en el código:** 
  - `sys.executable` → obtiene la ruta del intérprete Python para instalar paquetes
  - `sys.exit(1)` → sale del programa si falla la instalación

---

### 2. **subprocess**
```python
import subprocess
```
- **Propósito:** Ejecutar procesos externos desde Python
- **Uso en el código:**
  - `subprocess.run([sys.executable, "-m", "pip", "install", "flask", "--quiet"])` 
  - → ejecuta `pip install` automáticamente para instalar Flask

---

### 3. **threading**
```python
import threading
```
- **Propósito:** Ejecutar código en paralelo (múltiples threads)
- **Uso en el código:**
  - `threading.Thread(target=run_flask, daemon=True).start()` 
  - → levanta el servidor Flask en un thread separado
  - → el programa principal no se bloquea
  - `daemon=True` → el thread se cierra cuando cierra el programa principal

**Ventaja:** El usuario puede interactuar con la ventana Tkinter mientras Flask procesa en background

---

### 4. **time**
```python
import time
```
- **Propósito:** Operaciones relacionadas con tiempo
- **Uso en el código:**
  - `time.sleep(0.15)` → pausa de 150ms mientras espera que Flask esté listo
  - Usado en el loop de espera antes de abrir el navegador

---

### 5. **math**
```python
import math
```
- **Propósito:** Funciones matemáticas
- **Uso en el código:**
  - `math.sin(x)` → calcula seno para la onda sintética
  - `math.pi` → constante π para los ciclos (4π = 2 ciclos)

---

### 6. **random**
```python
import random
```
- **Propósito:** Generar números aleatorios
- **Uso en el código:**
  - `random.gauss(0, amp)` → ruido gaussiano (distribución normal)
  - `random.random()` → número aleatorio para pérdida de paquetes

---

### 7. **webbrowser**
```python
import webbrowser
```
- **Propósito:** Controlar el navegador del sistema
- **Uso en el código:**
  - `webbrowser.open(f'http://127.0.0.1:{PORT}')` 
  - → abre automáticamente el navegador en la URL del simulador

---

### 8. **struct**
```python
import struct
```
- **Propósito:** Convertir bytes a datos estructurados
- **Uso en el código:**
  - `struct.unpack(f'<{total}{fmt}', frames)` 
  - → lee bytes del archivo WAV y los convierte en números
  - `<` → little-endian (orden de bytes)
  - `{fmt}` → formato (b=byte, h=short, i=int)

**Ejemplo:** Un archivo WAV tiene 16 bits por muestra, struct los convierte en integers

---

### 9. **io**
```python
import io
```
- **Propósito:** Trabajar con streams (flujos) de datos en memoria
- **Uso en el código:**
  - `io.BytesIO(file_bytes)` 
  - → convierte los bytes del WAV en un objeto "file-like" que `wave.open()` puede leer
  - No necesita guardar el archivo en disco

---

### 10. **os**
```python
import os
```
- **Propósito:** Operaciones del sistema operativo
- **Uso en el código:** Actualmente no se usa, pero está disponible para futuras extensiones

---

### 11. **wave** (módulo estándar)
```python
import wave as wv  # (dentro de parse_wav)
```
- **Propósito:** Leer y escribir archivos WAV
- **Uso en el código:**
  ```python
  with wv.open(buf) as w:
      n_ch = w.getnchannels()      # número de canales
      sw = w.getsampwidth()         # bytes por muestra (1, 2, o 4)
      rate = w.getframerate()       # frecuencia (Hz)
      n_fr = w.getnframes()         # número de frames
      frames = w.readframes(n_fr)   # lee todos los datos
  ```

---

## **Flask (Backend Web)**

### 12. **Flask**
```python
from flask import Flask, request, jsonify, Response
```

**Flask** es un microframework web para Python. Es la columna vertebral del servidor.

#### Componentes utilizados:

| Componente | Uso |
|-----------|-----|
| `Flask(__name__)` | Crea la aplicación web |
| `@app.route('/')` | Decorador para definir rutas |
| `request.files` | Accede a archivos subidos por el cliente |
| `request.get_json()` | Lee JSON del cuerpo de la solicitud |
| `jsonify({...})` | Convierte diccionarios a JSON y lo retorna |
| `Response(HTML, mimetype='text/html')` | Retorna HTML como respuesta |

**Rutas del servidor:**
- `GET /` → Devuelve la página HTML
- `GET /preview/sine` → Devuelve coordenadas del seno
- `POST /upload_audio` → Recibe WAV, lo procesa, lo guarda
- `POST /transmit` → Realiza la simulación de transmisión

---

## **JavaScript (Frontend)**

### 13. **Chart.js**
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

**Chart.js** es una librería para crear gráficos interactivos.

#### Uso en el código:
```javascript
new Chart(ctx, {
  type: 'line',                    // gráfico de línea
  data: { labels: [], datasets },  // datos
  options: { ... }                 // configuración visual
})
```

**Gráficos creados:**
1. `charts.preview` → Vista previa del audio/seno
2. `charts.orig` → Señal original
3. `charts.comp` → Señal comprimida
4. `charts.chan` → Señal en canal (con ruido)
5. `charts.over` → Superposición: Original vs Reconstruida

**Ventajas:**
- ✅ Gráficos suaves y responsive
- ✅ Leyendas automáticas
- ✅ Animaciones
- ✅ Se adapta a diferentes tamaños de pantalla

---

## **tkinter (GUI local)**

### 14. **tkinter**
```python
import tkinter as tk
from tkinter import ttk, messagebox
```

**tkinter** es la librería estándar de Python para interfaces gráficas de escritorio.

#### Uso en el código:

| Componente | Uso |
|-----------|-----|
| `tk.Tk()` | Ventana principal |
| `tk.Label()` | Etiquetas de texto |
| `ttk.Progressbar()` | Barra de progreso (instalación Flask) |
| `tk.messagebox.showerror()` | Cuadro de diálogo de error |
| `root.geometry()` | Define tamaño de ventana |
| `root.mainloop()` | Loop de eventos |

**Ventana de instalación:**
- Muestra barra de progreso mientras se instala Flask
- Bloquea el programa hasta completar

**Ventana de ejecución:**
- Muestra URL del simulador
- Usuario cierra esta ventana para detener la app

---

## **Resumen visual**

```
┌─────────────────────────────────────────────────────────┐
│                   NAVEGADOR WEB                         │
│  ┌────────────────────────────────────────────────────┐ │
│  │         HTML + CSS + JavaScript (Chart.js)       │ │
│  └────────────────┬─────────────────────────────────┘ │
└───────────────────┼──────────────────────────────────────┘
                    │ HTTP/JSON
        ┌───────────▼───────────────┐
        │      FLASK SERVER         │
        │   (threading.Thread)      │
        ├───────────────────────────┤
        │  • /upload_audio (POST)   │
        │  • /transmit (POST)       │
        │  • /preview/sine (GET)    │
        └───────┬─────────┬─────────┘
                │         │
        ┌───────▼──┐  ┌──▼────────┐
        │   wave   │  │   struct  │
        │   math   │  │  random   │
        │   io     │  │  sys      │
        └──────────┘  └───────────┘

┌──────────────────────────────────────────────┐
│        VENTANA TKINTER (Control)             │
│  • Instalación Flask (Progressbar)           │
│  • Info de ejecución (Label)                 │
│  • Cierre de app (mainloop)                  │
└──────────────────────────────────────────────┘
```

---

## **Dependencias externas (necesarias de instalar)**

- **Flask** → web framework (instalación automática)
- **Chart.js** → CDN (no requiere instalación, se carga del navegador)

## **Librerías estándar (incluidas con Python)**

- sys, subprocess, threading, time, math, random, webbrowser, struct, io, os, wave, tkinter

---

## 🎯 **Conclusión**

Este proyecto integra:
- **Backend:** Flask + Python (matemáticas y procesamiento)
- **Frontend:** HTML/CSS/JavaScript + Chart.js (visualización)
- **Desktop:** tkinter (interfaz nativa)
- **Procesamiento:** wave, struct, math, random (lógica de señales)
- **Concurrencia:** threading (responsividad)

Todo orquestado en un único archivo `.pyw` que es completamente standalone ✨
