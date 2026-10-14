import csv
import json
import re
import requests

from google.transit import gtfs_realtime_pb2

URL_TRIPS = "https://gtfsrt.renfe.com/trip_updates.pb"
URL_VEHICLES = "https://gtfsrt.renfe.com/vehicle_positions.pb"

# ---------------------------------
# Estaciones Madrid
# ---------------------------------

with open(
    "estaciones-madrid.json",
    encoding="utf-8"
) as f:

    estaciones = json.load(f)

# ---------------------------------
# Obtener línea desde trip_id
# ---------------------------------

def obtener_linea(trip_id):

    match = re.search(
        r"(C\d+[A-Za-z]?)",
        trip_id,
        re.IGNORECASE
    )

    if match:
        return match.group(1).upper()

    return ""

# ---------------------------------
# trip_id -> recorrido
# ---------------------------------

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

        trip_stops\
            .setdefault(
                trip_id,
                []
            )\
            .append(stop_id)

# ---------------------------------
# Leer Trip Updates
# ---------------------------------

trip_feed = gtfs_realtime_pb2.FeedMessage()

response = requests.get(
    URL_TRIPS,
    timeout=60
)

response.raise_for_status()

trip_feed.ParseFromString(
    response.content
)

proxima_parada = {}

for entity in trip_feed.entity:

    if not entity.HasField(
        "trip_update"
    ):
        continue

    trip_update = entity.trip_update

    trip_id = (
        trip_update.trip.trip_id
    )

    for stop in trip_update.stop_time_update:

        stop_id = stop.stop_id

        if stop_id in estaciones:

            proxima_parada[
                trip_id
            ] = stop_id

            break

# ---------------------------------
# Leer Vehicle Positions
# ---------------------------------

vehicle_feed = gtfs_realtime_pb2.FeedMessage()

response = requests.get(
    URL_VEHICLES,
    timeout=60
)

response.raise_for_status()

vehicle_feed.ParseFromString(
    response.content
)

resultado = []

for entity in vehicle_feed.entity:

    if not entity.HasField(
        "vehicle"
    ):
        continue

    vehicle = entity.vehicle

    trip_id = (
        vehicle.trip.trip_id
    )

    recorrido = trip_stops.get(
        trip_id
    )

    if not recorrido:
        continue

    linea = obtener_linea(
        trip_id
    )

    resultado.append({

        "linea":
            linea,

        "trip_id":
            trip_id,

        "origen_viaje":
            recorrido[0],

        "destino_viaje":
            recorrido[-1],

        "proxima_estacion":
            proxima_parada.get(
                trip_id
            ),

        "latitud":
            vehicle.position.latitude,

        "longitud":
            vehicle.position.longitude

    })

# ---------------------------------
# Guardar resultado
# ---------------------------------

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
