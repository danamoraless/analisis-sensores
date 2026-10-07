"""Análisis de sensores industriales (datos simulados).

Lee data/sensores_industriales.csv, calcula las métricas solicitadas
y exporta las lecturas con alerta (> 85 °C) a resultados/alertas.csv.
Solo usa la biblioteca estándar de Python.
"""

import csv
from collections import defaultdict
from pathlib import Path

UMBRAL_C = 85.0
BASE = Path(__file__).resolve().parent
RUTA_CSV = BASE / "sensores_industriales.csv"
RUTA_ALERTAS = BASE / "resultados" / "alertas.csv"


def empatados_max(conteo):
    """Devuelve (valor máximo, lista de claves empatadas en ese valor)."""
    if not conteo:
        return 0, []
    maximo = max(conteo.values())
    return maximo, sorted(k for k, v in conteo.items() if v == maximo)


def main():
    total = 0
    sensores = set()
    suma_temp = defaultdict(float)
    n_temp = defaultdict(int)
    max_temp = None
    filas_max = []  # todas las filas empatadas en la temperatura máxima
    alertas_por_planta = defaultdict(int)
    n_alertas = 0

    RUTA_ALERTAS.parent.mkdir(parents=True, exist_ok=True)

    with open(RUTA_CSV, newline="", encoding="utf-8") as f_in, open(
        RUTA_ALERTAS, "w", newline="", encoding="utf-8"
    ) as f_out:
        lector = csv.DictReader(f_in)
        escritor = csv.DictWriter(f_out, fieldnames=lector.fieldnames)
        escritor.writeheader()

        for fila in lector:
            total += 1
            sensores.add(fila["id_sensor"])
            planta = fila["planta"]
            temp = float(fila["temperatura_c"])

            suma_temp[planta] += temp
            n_temp[planta] += 1

            if max_temp is None or temp > max_temp:
                max_temp = temp
                filas_max = [fila]
            elif temp == max_temp:
                filas_max.append(fila)

            if temp > UMBRAL_C:
                n_alertas += 1
                alertas_por_planta[planta] += 1
                escritor.writerow(fila)  # conserva columnas originales

    print(f"Registros: {total}")
    print(f"Sensores distintos: {len(sensores)}")

    print("\nTemperatura promedio por planta:")
    for planta in sorted(suma_temp):
        print(f"  {planta}: {suma_temp[planta] / n_temp[planta]:.2f} °C")

    print(f"\nTemperatura máxima: {max_temp} °C")
    for fila in filas_max:
        print(f"  sensor {fila['id_sensor']} | {fila['fecha_hora']} | planta {fila['planta']}")

    print(f"\nLecturas con temperatura > {UMBRAL_C:g} °C: {n_alertas}")

    maximo, plantas = empatados_max(alertas_por_planta)
    if plantas:
        print(f"Planta(s) con más alertas ({maximo}): {', '.join(plantas)}")
    else:
        print("No hubo alertas en ninguna planta.")

    print(f"\nAlertas exportadas a {RUTA_ALERTAS.relative_to(BASE)}")


if __name__ == "__main__":
    main()
