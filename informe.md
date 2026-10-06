# Informe: Big Data aplicado al monitoreo de sensores industriales

> Los datos del CSV son **simulados**. Los valores provienen de la salida de `analisis.py`.

## 5. Las 5 V aplicadas al proyecto

| V | Relación con el sistema de sensores | Ejemplo concreto | ¿CSV actual o ampliación? |
|---|---|---|---|
| **Volumen** | Cantidad de datos generados por los sensores. | El CSV tiene 100,000 mediciones (40 sensores distintos). Con miles de sensores a 1 lectura/s se generarían cientos de millones de filas por día (p. ej. 5,000 sensores × 86,400 s ≈ 432 millones). | **CSV actual:** 100,000 filas. **Ampliación:** el volumen masivo. |
| **Velocidad** | Rapidez con que llegan los datos y con que deben procesarse. | Hoy: 1 lectura por minuto por sensor, analizada después. Futuro: 1 lectura por segundo, con alertas en pocos segundos. | **CSV actual:** frecuencia de 1/min (y se procesa en diferido). **Ampliación:** 1/s y respuesta casi en tiempo real. |
| **Variedad** | Diversidad de formatos y fuentes. | Hoy: tabla CSV. Futuro: mensajes JSON, fotografías de máquinas y texto libre de reportes de mantenimiento. | **CSV actual:** solo un formato tabular. **Ampliación:** JSON, imágenes y texto. |
| **Veracidad** | Calidad y confiabilidad de los datos. | Un sensor descalibrado podría registrar temperaturas erróneas; hay que revisar nulos, duplicados y valores imposibles; en este CSV no se encontraron valores vacíos ni `id_registro` repetidos. El umbral de 85 °C es una regla didáctica y los datos son simulados. | **CSV actual:** se pueden revisar nulos/duplicados/rangos en las columnas existentes. **Ampliación:** fallas de sensores y de red a gran escala. |
| **Valor** | Utilidad de los datos para decidir. | Identificar la planta con más alertas (Planta_3) para priorizar revisión de mantenimiento. | **CSV actual:** hallazgos descriptivos. **Ampliación:** mantenimiento predictivo al combinar fuentes. |

## 6. Tipos de datos y procesamiento tradicional

| Elemento | Tipo | Justificación |
|---|---|---|
| CSV de sensores | **Estructurado** | Filas y columnas con esquema fijo. |
| Mensaje JSON de un sensor | **Semiestructurado** | Tiene etiquetas y jerarquía, pero el esquema puede variar. |
| Fotografía de una máquina | **No estructurado** | Píxeles sin esquema tabular; requiere visión por computadora. |
| Texto libre de un reporte de mantenimiento | **No estructurado** | Lenguaje natural sin campos definidos; requiere procesamiento de texto. |

**¿Por qué 100,000 registros no son Big Data automáticamente?** Big Data no se define solo por el número de filas, sino por si los datos superan lo que se puede almacenar y procesar con herramientas tradicionales (una sola máquina) y por las otras V. Este archivo es pequeño (unos pocos MB), se lee completo en segundos con una sola computadora y es de un único formato, así que el procesamiento tradicional basta.

**Limitaciones al crecer la escala:** el archivo ya no cabría en la memoria de una sola máquina; leer un CSV completo cada vez sería lento; un solo equipo sería punto único de falla; no se podrían responder alertas en segundos con ejecución por lotes; y el código actual no maneja imágenes ni texto libre. Se necesitaría almacenamiento y cómputo distribuidos.

## 7. Batch y Streaming

**Lo que hice:** procesamiento **por lotes (batch)**. El programa lee un archivo ya guardado completo, lo procesa de una vez y termina; el resultado no es urgente, y los datos están acotados (un conjunto finito).

**Alerta pocos segundos después de una lectura > 85 °C:** **streaming**. Cada lectura se evalúa al llegar (por ejemplo, un broker de mensajes como Kafka y un motor de flujo como Flink o Spark Structured Streaming), y si supera el umbral se notifica de inmediato. La latencia requerida es de segundos, lo cual un lote no puede dar.

**Resumen al terminar el día:** **batch**. Se necesita todo el día de datos y el resultado puede esperar horas; un trabajo programado nocturno es más simple y barato.

**Relación con el tiempo:** la elección depende de cuándo se necesita el resultado: segundos → streaming; horas → batch.

## 8. Lambda y Kappa

**Escenario A → Arquitectura Lambda.** Combina explícitamente una ruta por lotes (recalcula el historial completo, con precisión) y una ruta rápida (procesa lo reciente con baja latencia); una capa de servicio une ambos resultados. Costo: mantener dos lógicas de procesamiento.

```
                 +--> [Capa batch: recalcula historial] --+
[Sensores] --> [Ingesta] --+                                +--> [Capa de servicio] --> [Consultas / Alertas]
                 +--> [Capa rápida: mediciones recientes] -+
```

**Escenario B → Arquitectura Kappa.** Una sola lógica de procesamiento de eventos sobre un registro de eventos inmutable y reproducible; para reprocesar, se vuelve a leer el registro con la nueva versión del código. Evita duplicar lógica.

```
[Sensores] --> [Registro de eventos (log) conservado] --> [Procesamiento de flujo único] --> [Almacén de resultados] --> [Consultas / Alertas]
                           ^                                         |
                           +----------- reprocesar desde el log -----+
```

## 9. Analítica descriptiva, predictiva y prescriptiva

**Descriptiva (hallazgos reales del análisis):**
1. La planta con más alertas de temperatura es Planta_3, con 1,777 alertas de un total de 6,954 lecturas > 85 °C (6.95 % de las 100,000 lecturas). Las otras plantas tienen 1,737 (Planta_1), 1,732 (Planta_4) y 1,708 (Planta_2), así que la diferencia entre plantas es pequeña.
2. La temperatura máxima registrada fue 104.99 °C y hay un empate de cuatro lecturas: S023 (01/09/26 22:23, Planta_3), S019 (02/09/26 13:11, Planta_2), S014 (02/09/26 15:23, Planta_2) y S030 (02/09/26 16:02, Planta_3).

**Predictiva:** ¿Qué máquinas tienen mayor probabilidad de presentar una falla en los próximos 7 días? Datos adicionales necesarios: historial de fallas y paros, registros y tipos de mantenimiento, edad y modelo de cada máquina, carga de trabajo, condiciones ambientales y lecturas históricas más largas, con etiquetas de falla confirmada.

**Prescriptiva:** si el modelo anticipa riesgo alto en una máquina, programar una inspección preventiva antes del siguiente turno. Antes de decidir revisaría: si el patrón de alertas es persistente o aislado, la vibración conjunta, el historial de mantenimiento, si el sensor está calibrado (veracidad), el costo de parar la máquina frente al de una falla y la disponibilidad del equipo de mantenimiento.

*Nota:* una lectura por encima del umbral es una alerta del ejercicio; por sí sola no demuestra que una máquina vaya a fallar.
