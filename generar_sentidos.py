import csv
import json
import re
import requests

from google.transit import gtfs_realtime_pb2

URL_TRIPS = "https://gtfsrt.renfe.com/trip_updates.pb"
URL_VEHICLES = "https://gtfsrt.renfe.com/vehicle_positions.pb"

with open(
    "estaciones-madrid.json",
    encoding="utf-8"
) as f:

    estaciones = json.load(f)

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

trip_feed = gtfs_realtime_pb2.FeedMessage()

r = requests.get(
    URL_TRIPS,
    timeout=60
)

r.raise_for_status()

trip_feed.ParseFromString(
    r.content
)

proxima_parada = {}

for entity in trip_feed.entity:

    if not entity.HasField(
        "trip_update"
    ):
        continue

    update = entity.trip_update

    trip_id = (
        update.trip.trip_id
    )

    for stop in update.stop_time_update:

        if stop.stop_id in estaciones:

            proxima_parada[
                trip_id
            ] = stop.stop_id

            break

vehicle_feed = gtfs_realtime_pb2.FeedMessage()

r = requests.get(
    URL_VEHICLES,
    timeout=60
)

r.raise_for_status()

vehicle_feed.ParseFromString(
    r.content
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

    resultado.append({

        "linea":
            trip_linea.get(
                trip_id,
                ""
            ),

        "trip_id":
            trip_id,

        "origen_viaje":
            recorrido[0],

        "destino_viaje":
            recorrido[-1],

        "proxima_estacion":
            proxima_parada.get(
                trip_id
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
