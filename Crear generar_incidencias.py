import json
import requests

URL = "https://gtfsrt.renfe.com/alerts.pb"

salida = {
    "descargado": False
}

try:

    r = requests.get(
        URL,
        timeout=60
    )

    r.raise_for_status()

    salida = {
        "descargado": True,
        "tamano_bytes": len(r.content)
    }

except Exception as e:

    salida = {
        "descargado": False,
        "error": str(e)
    }

with open(
    "incidencias.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        salida,
        f,
        ensure_ascii=False,
        indent=2
    )

print("Incidencias actualizadas")
