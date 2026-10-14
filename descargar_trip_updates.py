import json
import re
import requests

from datetime import datetime
from google.transit import gtfs_realtime_pb2

URL = "https://gtfsrt.renfe.com/trip_updates.pb"

ESTACIONES_MADRID = {
    "17000",
    "18000",
    "18001",
    "18002",
    "18101"
}

feed = gtfs_realtime_pb2.FeedMessage()

response = requests.get(URL, timeout=60)
response.raise_for_status()

feed.ParseFromString(response.content)

salidas = {}

for entity in feed.entity:

    if not entity.HasField("trip_update"):
        continue

    trip = entity.trip_update

    trip_id = trip.trip.trip_id

    match = re.search(
        r"(C\d+[ABab]?)$",
        trip_id
    )

    if not match:
        continue

    linea = match.group(1).upper()

    for stop in trip.stop_time_update:

        stop_id = stop.stop_id

        if stop_id not in ESTACIONES_MADRID:
            continue

        timestamp = None

        if stop.arrival.time:
            timestamp = stop.arrival.time

        elif stop.departure.time:
            timestamp = stop.departure.time

        if not timestamp:
            continue

        hora = datetime.fromtimestamp(
            timestamp
        ).strftime("%H:%M:%S")

        if stop_id not in salidas:
            salidas[stop_id] = {}

        existente = salidas[stop_id].get(linea)

        if (
            existente is None
            or hora < existente
        ):
            salidas[stop_id][linea] = hora

with open(
    "salidas.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        salidas,
        f,
        ensure_ascii=False,
        indent=2
    )

print("Salidas generadas")
