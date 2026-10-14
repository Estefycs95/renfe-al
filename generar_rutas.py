import csv
import json
import re

# ----------------------------
# Cargar todas las estaciones
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
# trip_id -> linea
# ----------------------------

trip_linea = {}

with open(
    "trips.txt",
    encoding="utf-8"
) as f:

    reader = csv.DictReader(f)

    for row in reader:

        trip_id = row["trip_id"]

        m = re.search(
            r"(C\d+[abAB]?)$",
            trip_id
        )

        if m:

            trip_linea[trip_id] = (
                m.group(1).upper()
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

                trayectos\
                    .setdefault(
                        linea,
                        []
                    )\
                    .append(
                        stops_actual
                    )

            stops_actual = []
            trip_actual = trip_id

        stops_actual.append(
            stop_id
        )

    if stops_actual:

        linea = trip_linea.get(
            trip_actual
        )

        if linea:

            trayectos\
                .setdefault(
                    linea,
                    []
                )\
                .append(
                    stops_actual
                )

# ----------------------------
# Trayecto más largo
# ----------------------------

resultado = {}

for linea, viajes in trayectos.items():

    mejor = []

    for viaje in viajes:

        estaciones = [

            parada

            for parada in viaje

            if parada in estaciones_madrid

        ]

        if len(estaciones) > len(mejor):

            mejor = estaciones

    if len(mejor) > 1:

        resultado[linea] = mejor

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
