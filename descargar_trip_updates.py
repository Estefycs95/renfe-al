import json
import requests

from google.transit import gtfs_realtime_pb2

URL = "https://gtfsrt.renfe.com/trip_updates.pb"

feed = gtfs_realtime_pb2.FeedMessage()

data = requests.get(URL, timeout=60).content

feed.ParseFromString(data)

salidas = []

for entity in feed.entity:

    if not entity.HasField("trip_update"):
        continue

    trip = entity.trip_update

    item = {
        "trip_id": trip.trip.trip_id,
        "route_id": trip.trip.route_id,
        "stops": []
    }

    for stop in trip.stop_time_update:

        registro = {
            "stop_id": stop.stop_id
        }

        if stop.arrival.time:
            registro["arrival"] = stop.arrival.time

        if stop.departure.time:
            registro["departure"] = stop.departure.time

        item["stops"].append(registro)

    salidas.append(item)

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

print(f"Guardados {len(salidas)} viajes")
