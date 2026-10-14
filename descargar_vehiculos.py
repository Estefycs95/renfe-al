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

    "18000": {
        "nombre": "Atocha",
        "lat": 40.4066191,
        "lon": -3.6894391
    },

    "18001": {
        "nombre": "Recoletos",
        "lat": 40.4233731,
        "lon": -3.6909310
    },

    "18002": {
        "nombre": "Nuevos Ministerios",
        "lat": 40.4466271,
        "lon": -3.6923468
    },

    "18101": {
        "nombre": "Sol",
        "lat": 40.4168665,
        "lon": -3.7028765
    },

    "17000": {
        "nombre": "Chamartín",
        "lat": 40.4711789,
        "lon": -3.6829524
    }

}


feed = gtfs_realtime_pb2.FeedMessage()

response = requests.get(URL, timeout=60)
response.raise_for_status()

feed.ParseFromString(response.content)

vehiculos = []

resumen = {}

for stop_id in ESTACIONES.keys():
    resumen[stop_id] = {}

for entity in feed.entity:

    if not entity.HasField("vehicle"):
        continue

    vehicle = entity.vehicle

    trip_id = vehicle.trip.trip_id

    match = re.search(
        r"(C\d+[ABab]?)$",
        trip_id
    )

    if not match:
        continue

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

    for stop_id, estacion in ESTACIONES.items():

        distancia = distancia_km(
            lat,
            lon,
            estacion["lat"],
            estacion["lon"]
        )

        distancias[estacion["nombre"]] = distancia

        actual = resumen[stop_id].get(linea)

        if actual is None or distancia < actual:
            resumen[stop_id][linea] = distancia

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


with open(
    "vehiculos_resumen.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        resumen,
        f,
        ensure_ascii=False,
        indent=2
    )

print(
    f"{len(vehiculos)} trenes Madrid procesados"
)
