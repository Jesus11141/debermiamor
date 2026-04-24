# ⚡ PRONACA Pifo — Modelo Dinámico de Consumo Eléctrico
## Dashboards Interactivos 2022–2024

---

## 📋 ¿De qué trata el proyecto?

Se simula y visualiza el **consumo eléctrico de la planta PRONACA Pifo** durante los últimos 3 años (2022, 2023, 2024), siguiendo la **Metodología de Simulación** y generando **2 dashboards interactivos**.

---

## 🔬 Metodología Aplicada

| Paso | Descripción | Archivo |
|------|-------------|---------|
| 1. Definición del Sistema | Planta industrial avícola, consumo diario en kWh | `datos_pronaca.py` |
| 2. Formulación del Modelo | Ecuaciones de estacionalidad, tendencia y ruido | `datos_pronaca.py` |
| 3. Colección de Datos | Datos simulados realistas (1095 días) | `datos_pronaca.py` |
| 4. Implementación | Codificación en Python con Dash + Plotly | `dashboard1_python.py` |
| 5. Verificación y Validación | MAPE del modelo IA, detección de anomalías | `dashboard2_ia.py` |
| 6. Experimentación | Filtros interactivos por año y granularidad | Ambos dashboards |

---

## 📁 Archivos del Proyecto

```
deber aly/
├── datos_pronaca.py       → Generación de datos simulados
├── dashboard1_python.py   → Dashboard 1 (Programa Python)
├── dashboard2_ia.py       → Dashboard 2 (Herramienta IA)
├── requirements.txt       → Librerías necesarias
└── ejecutar.bat           → Lanzador rápido (doble clic)
```

---

## ⚙️ Requisitos

- **Python 3.13** instalado
- **Librerías:** dash, plotly, pandas, numpy, scikit-learn, scipy

---

## 🚀 Pasos para Ejecutar

### Paso 1 — Abrir CMD (NO PowerShell)

Presiona `Win + R`, escribe `cmd` y presiona Enter.

---

### Paso 2 — Ir a la carpeta del proyecto

```cmd
cd "C:\Users\Raul\Downloads\deber aly"
```

---

### Paso 3 — Instalar librerías (solo la primera vez)

```cmd
"C:\Users\Raul\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe" -m pip install dash plotly pandas numpy scikit-learn scipy
```

---

### Paso 4 — Ejecutar Dashboard 1 (Python)

```cmd
"C:\Users\Raul\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe" dashboard1_python.py
```

Abrir en el navegador: **http://127.0.0.1:8050**

> Para detenerlo: presiona `Ctrl + C` en el CMD

---

### Paso 5 — Ejecutar Dashboard 2 (IA)

Abre **otra ventana de CMD** y ejecuta:

```cmd
cd "C:\Users\Raul\Downloads\deber aly"
"C:\Users\Raul\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe" dashboard2_ia.py
```

Abrir en el navegador: **http://127.0.0.1:8051**

---

### Alternativa — Doble clic en ejecutar.bat

1. Abrir la carpeta `C:\Users\Raul\Downloads\deber aly` en el Explorador
2. Doble clic en **ejecutar.bat**
3. Escribir `1` para Dashboard 1 o `2` para Dashboard 2

---

## 📊 Dashboard 1 — Programa Python

**URL:** http://127.0.0.1:8050

### ¿Qué muestra?

| Gráfico | Descripción |
|---------|-------------|
| 📈 Serie Temporal | Consumo diario/semanal/mensual por año |
| 📊 Barras Anuales | Total consumido por año en GWh |
| 🟥 Heatmap | Consumo mensual cruzado por año (mapa de calor) |
| 📅 Patrón Semanal | Consumo promedio por día de la semana |
| 💰 Costo Mensual | Costo estimado en USD por mes |

### Controles interactivos

- **Filtro de Año:** seleccionar 2022, 2023, 2024 (o combinaciones)
- **Granularidad:** cambiar entre vista Diaria, Semanal o Mensual

### KPIs en tiempo real

- Total consumo 3 años (GWh)
- Costo total estimado (USD)
- Promedio diario (kWh)
- Demanda pico máxima (kW)

---

## 🤖 Dashboard 2 — Herramienta de IA

**URL:** http://127.0.0.1:8051

### ¿Qué hace la IA?

| Técnica | Descripción |
|---------|-------------|
| Regresión Polinomial (grado 3) | Aprende el patrón histórico y predice el consumo de 2025 |
| Z-Score (scipy) | Detecta días con consumo anormalmente alto o bajo |
| Descomposición de serie | Separa tendencia y componente estacional |
| Recomendaciones automáticas | Genera sugerencias basadas en los datos analizados |

### Vistas disponibles (botones de radio)

1. **Predicción 2025** — Línea histórica + predicción IA con banda de confianza del 95%
2. **Anomalías** — Serie completa con puntos rojos marcando días anómalos
3. **Descomposición** — Tendencia (línea naranja) + componente estacional (barras verdes)

### KPIs de IA

- Precisión del modelo (100% - MAPE)
- Cantidad de días anómalos detectados
- Predicción promedio diaria para 2025
- Costo proyectado para 2025

### Recomendaciones automáticas generadas

El sistema analiza los datos y genera automáticamente sugerencias como:
- Tendencia de crecimiento → evaluar paneles solares
- Consumo en fin de semana → revisar equipos en stand-by
- Días anómalos → mantenimiento preventivo
- Fecha del pico histórico → planificación de mantenimiento

---

## 📐 Modelo de Simulación (datos_pronaca.py)

Los datos se generan con la siguiente lógica:

```
consumo_diario = (base + estacionalidad + tendencia) × factor_semanal + ruido

Donde:
  base          = 8,000 kWh/día  (planta industrial avícola)
  estacionalidad = 1,200 × sin(2π × mes / 12)  (más consumo en verano)
  tendencia     = 150 kWh × años transcurridos  (crecimiento ~3% anual)
  factor_semanal = 1.0 (lunes-viernes), 0.80 (sábado), 0.55 (domingo)
  ruido         = distribución normal(0, 300)
  costo         = consumo × $0.09/kWh  (tarifa industrial Ecuador)
```

---

## 🛠️ Librerías Utilizadas

| Librería | Uso |
|----------|-----|
| `dash` | Framework para dashboards web interactivos |
| `plotly` | Gráficos interactivos (líneas, barras, heatmap, histogramas) |
| `pandas` | Manejo y procesamiento de datos |
| `numpy` | Cálculos numéricos y generación de datos |
| `scikit-learn` | Regresión polinomial (modelo IA de predicción) |
| `scipy` | Detección de anomalías con Z-Score |

---

## ❓ Preguntas frecuentes

**¿Los datos son reales?**
No, son simulados con parámetros realistas de una planta industrial avícola ecuatoriana. El modelo replica patrones reales: estacionalidad, tendencia de crecimiento y variación semanal.

**¿Por qué dos dashboards?**
El trabajo pide uno con programa Python y otro con herramienta de IA. El Dashboard 1 es visualización pura; el Dashboard 2 incorpora Machine Learning (predicción y detección de anomalías).

**¿Qué es el MAPE?**
Mean Absolute Percentage Error — mide qué tan preciso es el modelo IA. Un MAPE bajo significa que el modelo predice bien el consumo histórico.

**¿Se pueden usar datos reales?**
Sí. En `datos_pronaca.py` se puede reemplazar la función `generar_datos_pronaca()` con la lectura de un archivo Excel o CSV con datos reales de PRONACA.
