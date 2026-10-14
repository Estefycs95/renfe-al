import json

with open(
    "vehiculos_sentido.json",
    encoding="utf-8"
) as f:

    vehiculos = json.load(f)

resultado = {}

for tren in vehiculos:

    linea = tren.get("linea")

    if not linea:
        continue

    if linea not in resultado:

        resultado[linea] = []

    resultado[linea].append({

        "trip_id":
            tren["trip_id"],

        "origen_viaje":
            tren["origen_viaje"],

        "destino_viaje":
            tren["destino_viaje"],

        "proxima_estacion":
            tren.get(
                "proxima_estacion"
            )

    })

with open(
    "sentidos_resumen.json",
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
    f"{len(resultado)} líneas generadas"
)
