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

    hora = None

    for stop in trip.stop_time_update:

        if stop.arrival.time:

            hora = datetime.fromtimestamp(
                stop.arrival.time
            ).strftime("%H:%M:%S")

            break

        if stop.departure.time:

            hora = datetime.fromtimestamp(
                stop.departure.time
            ).strftime("%H:%M:%S")

            break

    if not hora:
        continue

    if (
        linea not in salidas
        or hora < salidas[linea]
    ):

        salidas[linea] = hora

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

print(
    f"Generadas {len(salidas)} líneas"
)
