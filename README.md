# Simulador de Transmisión y Compresión de Señales
**Grupo 12 — Propuesta 4 · Etapa 2**

---

## Cómo ejecutar (Windows)

1. Hacer **doble clic** en `EJECUTAR_WINDOWS.bat`  
   *(alternativa: doble clic directo en `simulador_grupo12.pyw`)*
2. La primera vez instalará Flask automáticamente (requiere internet)
3. Se abre el navegador en `http://127.0.0.1:5050`
4. Para cerrar: cerrar la ventana pequeña del simulador

### Requisito
Python 3 con PATH configurado → [python.org/downloads](https://www.python.org/downloads/)

---

## Uso de la aplicación

| Paso | Qué hace |
|------|----------|
| **1. Fuente** | Elegir señal seno sintética o cargar un archivo `.wav` |
| **Vista previa** | Al cargar el WAV (o al elegir seno) se **lee y grafica la señal al instante** |
| **2. Compresión** | Sin compresión / Submuestreo / Cuantización (8 niveles) |
| **3. Canal** | Ruido gaussiano (0–100 %) y pérdida de paquetes (0–50 %) |
| **4. Transmitir** | Procesa la señal cargada y muestra compresión, canal y reconstrucción |
| **5. Métricas** | Tamaños, tasa de compresión, MSE y gráficos comparativos |

---

## Estructura del proyecto

```
simulador_señales/
├── simulador_grupo12.pyw   ← Aplicación principal (doble clic)
├── EJECUTAR_WINDOWS.bat    ← Lanzador Windows
├── app.py                  ← Versión anterior (solo referencia)
├── templates/index.html    ← Versión anterior del frontend
└── README.md
```

> **Archivo principal:** `simulador_grupo12.pyw` — incluye servidor, lógica de señales e interfaz.

---

## Funcionalidades vs consigna (Propuesta 4)

- Conversión de señal analógica/simulada a datos digitales (seno + WAV)
- Compresión por submuestreo y cuantización
- Simulación de errores en transmisión (ruido + pérdida de paquetes)
- Visualización de reconstrucción en el receptor con MSE
- **Extra:** carga de audio WAV con lectura y vista previa inmediata
