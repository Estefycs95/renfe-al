import csv
import json
import re
import requests

from math import radians
from math import sin
from math import cos
from math import sqrt
from math import atan2

from google.transit import gtfs_realtime_pb2

URL = "https://gtfsrt.renfe.com/vehicle_positions.pb"


def distancia_km(lat1, lon1, lat2, lon2):

    R = 6371

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        +
        cos(radians(lat1))
        *
        cos(radians(lat2))
        *
        sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return R * c


# ----------------------------
# Estaciones
# ----------------------------

with open(
    "estaciones-madrid.json",
    encoding="utf-8"
) as f:

    estaciones = json.load(f)

# ----------------------------
# trip -> linea
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
            r"(C\d+[ABab]?)$",
            trip_id
        )

        if m:

            trip_linea[trip_id] = (
                m.group(1).upper()
            )

# ----------------------------
# trip -> recorrido
# ----------------------------

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

# ----------------------------
# Feed vehículos
# ----------------------------

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

    recorrido = trip_stops[
        trip_id
    ]

    if len(recorrido) < 2:
        continue

    lat_tren = (
        vehicle.position.latitude
    )

    lon_tren = (
        vehicle.position.longitude
    )

    indice_mas_cercano = None
    mejor_distancia = 999999

    for i, stop_id in enumerate(
        recorrido
    ):

        estacion = estaciones.get(
            stop_id
        )

        if not estacion:
            continue

        distancia = distancia_km(
            lat_tren,
            lon_tren,
            estacion["lat"],
            estacion["lon"]
        )

        if distancia < mejor_distancia:

            mejor_distancia = distancia

            indice_mas_cercano = i

    if indice_mas_cercano is None:
        continue

    siguiente_indice = min(
        indice_mas_cercano + 1,
        len(recorrido) - 1
    )

    estacion_actual = recorrido[
        indice_mas_cercano
    ]

    siguiente_estacion = recorrido[
        siguiente_indice
    ]

    resultado.append({

        "linea": trip_linea.get(
            trip_id,
            ""
        ),

        "trip_id": trip_id,

        "latitud": lat_tren,

        "longitud": lon_tren,

        "estacion_actual":
            estacion_actual,

        "siguiente_estacion":
            siguiente_estacion,

        "origen_viaje":
            recorrido[0],

        "destino_viaje":
            recorrido[-1],

        "sentido":
            f"hacia {recorrido[-1]}",

        "distancia_a_estacion":
            round(
                mejor_distancia,
                3
            )

    })

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
