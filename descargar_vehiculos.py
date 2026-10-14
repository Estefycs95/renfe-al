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

    return round(R * c, 2)


ESTACIONES = {

    "18000": (
        "Atocha",
        40.4066191,
        -3.6894391
    ),

    "18001": (
        "Recoletos",
        40.4233731,
        -3.6909310
    ),

    "18002": (
        "Nuevos Ministerios",
        40.4466271,
        -3.6923468
    ),

    "18101": (
        "Sol",
        40.4168665,
        -3.7028765
    ),

    "17000": (
        "Chamartín",
        40.4711789,
        -3.6829524
    )

}


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

    # Solo Madrid

    if not (
        40.0 <= lat <= 41.1
        and
        -4.4 <= lon <= -3.0
    ):
        continue

    distancias = {}

    for stop_id, datos in ESTACIONES.items():

        nombre, lat_est, lon_est = datos

        distancias[nombre] = distancia_km(
            lat,
            lon,
            lat_est,
            lon_est
        )

    vehiculos.append({

        "linea": linea,

        "trip_id": trip_id,

        "latitud": lat,

        "longitud": lon,

        "timestamp": vehicle.timestamp,

        "distancias": distancias

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
