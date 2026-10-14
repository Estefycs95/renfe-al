import json
import re
import requests

from datetime import datetime
from google.transit import gtfs_realtime_pb2

URL = "https://gtfsrt.renfe.com/trip_updates.pb"

feed = gtfs_realtime_pb2.FeedMessage()

response = requests.get(URL, timeout=60)
response.raise_for_status()

feed.ParseFromString(response.content)

salidas = []

for entity in feed.entity:

    if not entity.HasField("trip_update"):
        continue

    trip = entity.trip_update

    trip_id = trip.trip.trip_id

    match = re.search(
        r"(C\d+[ABab]?)$",
        trip_id
    )

    linea = ""

    if match:
        linea = match.group(1).upper()

    registro = {
        "trip_id": trip_id,
        "linea": linea,
        "stops": []
    }

    for stop in trip.stop_time_update:

        parada = {
            "stop_id": stop.stop_id
        }

        if stop.arrival.time:

            parada["arrival"] = stop.arrival.time

            parada["arrival_hora"] = (
                datetime.fromtimestamp(
                    stop.arrival.time
                ).strftime("%Y-%m-%d %H:%M:%S")
            )

        if stop.departure.time:

            parada["departure"] = stop.departure.time

            parada["departure_hora"] = (
                datetime.fromtimestamp(
                    stop.departure.time
                ).strftime("%Y-%m-%d %H:%M:%S")
            )

        registro["stops"].append(
            parada
        )

    salidas.append(
        registro
    )

with open(
    "trip_updates.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        salidas,
        f,
        ensure_ascii=False,
        indent=2
    )

print(
    f"Generados {len(salidas)} viajes"
)
