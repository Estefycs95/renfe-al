import csv
import json
import re

# ---------------------------------
# trips.txt
# trip_id -> linea
# ---------------------------------

trip_linea = {}

with open("trips.txt", encoding="utf-8") as f:

    reader = csv.DictReader(f)

    for row in reader:

        trip_id = row["trip_id"]

        m = re.search(r"(C\d+[abAB]?)$", trip_id)

        if m:

            trip_linea[trip_id] = m.group(1).upper()


# ---------------------------------
# stop_times.txt
# ---------------------------------

trayectos = {}

trip_actual = None
stops_actual = []

with open("stop_times.txt", encoding="utf-8") as f:

    reader = csv.DictReader(f)

    for row in reader:

        trip_id = row["trip_id"]
        stop_id = row["stop_id"]

        if trip_actual is None:
            trip_actual = trip_id

        if trip_id != trip_actual:

            linea = trip_linea.get(trip_actual)

            if linea and stops_actual:

                trayectos.setdefault(
                    linea,
                    []
                ).append(stops_actual)

            stops_actual = []
            trip_actual = trip_id

        stops_actual.append(stop_id)

    if stops_actual:

        linea = trip_linea.get(trip_actual)

        if linea:

            trayectos.setdefault(
                linea,
                []
            ).append(stops_actual)

# ---------------------------------
# Elegimos el trayecto más largo
# por línea
# ---------------------------------

resultado = {}

for linea, viajes in trayectos.items():

    mejor = max(
        viajes,
        key=len
    )

    resultado[linea] = mejor

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
    "Generado rutas-madrid.json"
)
