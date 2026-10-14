import json
import re
import requests

from google.transit import gtfs_realtime_pb2

URL = "https://gtfsrt.renfe.com/vehicle_positions.pb"

feed = gtfs_realtime_pb2.FeedMessage()

response = requests.get(URL, timeout=60)
response.raise_for_status()

feed.ParseFromString(response.content)

vehiculos = []

for entity in feed.entity:

    if not entity.HasField("vehicle"):
        continue

    vehicle = entity.vehicle

    trip_id = vehicle.trip.trip_id

    match = re.search(
        r"(C\d+[ABab]?)$",
        trip_id
    )

    linea = ""

    if match:
        linea = match.group(1).upper()

    lat = vehicle.position.latitude
    lon = vehicle.position.longitude

    # Filtro aproximado Madrid

    if not (
        40.0 <= lat <= 41.1
        and
        -4.4 <= lon <= -3.0
    ):
        continue

    vehiculos.append({

        "linea": linea,

        "trip_id": trip_id,

        "latitud": lat,

        "longitud": lon,

        "timestamp": vehicle.timestamp

    })

with open(
    "vehiculos.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        vehiculos,
        f,
        ensure_ascii=False,
        indent=2
    )

print(
    f"{len(vehiculos)} trenes de Madrid encontrados"
)
