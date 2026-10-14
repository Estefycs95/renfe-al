import csv
import json

estaciones = {}

with open(
    "stops.txt",
    encoding="utf-8"
) as f:

    reader = csv.DictReader(f)

    for row in reader:

        lat = float(row["stop_lat"])
        lon = float(row["stop_lon"])

        # Caja aproximada Madrid

        if (
            40.0 <= lat <= 41.1
            and
            -4.4 <= lon <= -3.0
        ):

            estaciones[row["stop_id"]] = {
                "nombre": row["stop_name"],
                "lat": lat,
                "lon": lon
            }

with open(
    "estaciones-madrid.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        estaciones,
        f,
        ensure_ascii=False,
        indent=2
    )

print(
    f"{len(estaciones)} estaciones encontradas"
)
