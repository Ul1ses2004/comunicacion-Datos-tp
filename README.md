# Simulador de Transmisión y Compresión de Señales
**Grupo 12 — Propuesta 4 · Etapa 2**

## Cómo ejecutar (Windows)

1. Descargar y hacer doble click al archivo "Simulador de Transmision.exe" que se encuentra en la carpeta root de este repositorio.
2. Se iniciará automáticamente una aplicación en una pequeña ventana (el servidor), al mismo tiempo que se abrirá una pestaña en internet con la webapp (el cliente).
3. Minimizar la pequeña ventana servidor, y utilizar la aplicación en la página que se ha abierto.
4. Para salir del programa, simplemente cerrar la ventana servidor y cerrar la página que se abrió.

### Requisito
Python 3 con PATH configurado → [python.org/downloads](https://www.python.org/downloads/)

## Uso de la aplicación

| Paso | Explicación |
|------|----------|
| **1. Fuente** | Elegir la señal seno o cargar un archivo `.wav`. Se mostrará una vista previa con gráfica de la señal en cuestión.|
| **2. Compresión** | Elegir el tipo de compresión a aplicar a la señal fuente: **[Sin compresión]:** no aplicar compresión a la señal. <br> **[Reducir muestras]:** utilizar menos puntos (o componentes) para reducir la señal. <br> **[Reducir niveles de cuantización]:** limitar las amplitudes utilizables a 9 valores distintos.
| **3. Canal** | Agregar un porcentaje de ruido al canal (0–100%) que aleatoriamente distorsiona la señal, <br> Agregar un porcentaje de pérdida de paquetes (0–50%) de la señal que genera que se pierdan tramos de la misma. |
| **4. Transmitir** | Aplica todas las configuraciones seleccionadas a la señal y las "transmite", mostrando la gráfica de cómo se veía originalmente, cómo es comprimida, cómo es en canal (es decir, mientra se transmite) y finalmente, una comparación de la original vs la transmitida. |
| **5. Métricas** | Muestra tamaños, tasa de compresión, ruido y pérdida de paquetes y MSE |

## Funcionalidades vs consigna (Propuesta 4)

- Conversión de señal analógica/simulada a datos digitales (seno + WAV)
- Compresión por submuestreo y cuantización
- Simulación de errores en transmisión (ruido + pérdida de paquetes)
- Visualización de reconstrucción en el receptor con MSE
- **Extra:** carga de audio WAV con lectura y vista previa inmediata
