import csv
import json
import re

# ----------------------------
# Cargar estaciones Madrid
# ----------------------------

with open(
    "estaciones-madrid.json",
    encoding="utf-8"
) as f:

    estaciones_madrid = set(
        json.load(f).keys()
    )

# ----------------------------
# trips.txt
# trip_id -> línea
# ----------------------------

trip_linea = {}

with open(
    "trips.txt",
    encoding="utf-8"
) as f:

    reader = csv.DictReader(f)

    for row in reader:

        trip_id = row["trip_id"]

        match = re.search(
            r"(C\d+[ABab]?)$",
            trip_id
        )

        if match:

            trip_linea[trip_id] = (
                match.group(1).upper()
            )

# ----------------------------
# stop_times.txt
# ----------------------------

trayectos = {}

trip_actual = None
stops_actual = []

with open(
    "stop_times.txt",
    encoding="utf-8"
) as f:

    reader = csv.DictReader(f)

    for row in reader:

        trip_id = row["trip_id"]
        stop_id = row["stop_id"]

        if trip_actual is None:
            trip_actual = trip_id

        if trip_id != trip_actual:

            linea = trip_linea.get(
                trip_actual
            )

            if linea and stops_actual:

                trayectos.setdefault(
                    linea,
                    []
                ).append(
                    stops_actual
                )

            stops_actual = []
            trip_actual = trip_id

        stops_actual.append(
            stop_id
        )

    # último viaje

    if stops_actual:

        linea = trip_linea.get(
            trip_actual
        )

        if linea:

            trayectos.setdefault(
                linea,
                []
            ).append(
                stops_actual
            )

# ----------------------------
# Unir todas las estaciones
# ----------------------------

resultado = {}

for linea, viajes in trayectos.items():

    estaciones_linea = []

    for viaje in viajes:

        for parada in viaje:

            if (
                parada in estaciones_madrid
                and
                parada not in estaciones_linea
            ):

                estaciones_linea.append(
                    parada
                )

    if len(estaciones_linea) > 1:

        resultado[linea] = (
            estaciones_linea
        )

# ----------------------------
# Guardar JSON
# ----------------------------

with open(
    "rutas-madrid.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        resultado,
        f,
        ensure_ascii=False,
        indent=2
    )

print(
    f"Generadas {len(resultado)} líneas"
)
