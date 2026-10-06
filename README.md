# Análisis de sensores industriales

## Objetivo
Analizar con Python las mediciones de temperatura y vibración de sensores instalados en cuatro plantas industriales: conteo de registros y sensores, temperatura promedio por planta, temperatura máxima, alertas (> 85 °C) y exportación de las lecturas con alerta.

## Datos
> **Los datos son simulados.** No provienen de máquinas reales.

Archivo: `data/sensores_industriales.csv` (100,000 mediciones de 40 sensores en 4 plantas).

| Columna | Significado |
|---|---|
| `id_registro` | Identificador de la medición |
| `fecha_hora` | Fecha y hora de la lectura |
| `id_sensor` | Identificador del sensor |
| `planta` | Planta donde está instalado |
| `temperatura_c` | Temperatura en °C |
| `vibracion_mm_s` | Vibración en mm/s |

Regla de alerta (didáctica): temperatura mayor que 85 °C.

## Dependencias
El programa usa **exclusivamente la biblioteca estándar de Python** (`csv`, `pathlib`, `collections`), por lo que **no necesita dependencias externas**. `requirements.txt` existe solo para documentarlo.

Requiere Python 3.8 o superior.

## Instalación y ejecución

```bash
git clone <URL_DEL_REPOSITORIO>
cd <carpeta-del-repositorio>

# Crear y activar el entorno virtual
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Instalar dependencias (ninguna externa)
pip install -r requirements.txt

# Ejecutar
python analisis.py
```

## Resultados
- Salida por consola con todas las métricas.
- `resultados/alertas.csv`: lecturas con temperatura > 85 °C, con las columnas originales.
- `informe.md`: respuestas de la parte de Big Data.
- `evidencias/`: captura de la ejecución en una copia clonada.

## Estructura
```
data/  resultados/  evidencias/  analisis.py  informe.md  requirements.txt  .gitignore
```
