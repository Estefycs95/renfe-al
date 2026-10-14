import csv
import json
import re
import requests

from google.transit import gtfs_realtime_pb2

URL = "https://gtfsrt.renfe.com/vehicle_positions.pb"

# ---------------------
# Cargar estaciones
# ---------------------

with open(
    "estaciones-madrid.json",
    encoding="utf-8"
) as f:

    estaciones = json.load(f)

# ---------------------
# Trip -> línea
# ---------------------

trip_linea = {}

with open(
    "trips.txt",
    encoding="utf-8"
) as f:

    reader = csv.DictReader(f)

    for row in reader:

        trip_id = row["trip_id"]

        m = re.search(
            r"(C\d+[ABab]?)$",
            trip_id
        )

        if m:

            trip_linea[trip_id] = (
                m.group(1).upper()
            )

# ---------------------
# Trip -> recorrido
# ---------------------

trip_stops = {}

with open(
    "stop_times.txt",
    encoding="utf-8"
) as f:

    reader = csv.DictReader(f)

    for row in reader:

        trip_id = row["trip_id"]

        stop_id = row["stop_id"]

        if stop_id not in estaciones:
            continue

        trip_stops.setdefault(
            trip_id,
            []
        ).append(stop_id)

# ---------------------
# Feed de vehículos
# ---------------------

feed = gtfs_realtime_pb2.FeedMessage()

response = requests.get(
    URL,
    timeout=60
)

response.raise_for_status()

feed.ParseFromString(
    response.content
)

resultado = []

for entity in feed.entity:

    if not entity.HasField(
        "vehicle"
    ):
        continue

    vehicle = entity.vehicle

    trip_id = (
        vehicle.trip.trip_id
    )

    if trip_id not in trip_stops:
        continue

    linea = trip_linea.get(
        trip_id,
        ""
    )

    recorrido = trip_stops[
        trip_id
    ]

    if len(recorrido) < 2:
        continue

    origen = recorrido[0]
    destino = recorrido[-1]

    siguiente = None

    if recorrido:

        siguiente = recorrido[0]

    resultado.append({

        "linea": linea,

        "trip_id": trip_id,

        "latitud":
            vehicle.position.latitude,

        "longitud":
            vehicle.position.longitude,

        "origen_viaje":
            origen,

        "destino_viaje":
            destino,

        "siguiente_estacion":
            siguiente,

        "sentido":
            f"hacia {destino}"

    })

# ---------------------
# Guardar
# ---------------------

with open(
    "vehiculos_sentido.json",
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
    f"{len(resultado)} trenes procesados"
)
