import json
import re
import requests

from google.transit import gtfs_realtime_pb2

URL = "https://gtfsrt.renfe.com/alerts.pb"

feed = gtfs_realtime_pb2.FeedMessage()

response = requests.get(
    URL,
    timeout=60
)

response.raise_for_status()

feed.ParseFromString(
    response.content
)

resultado = {
    "entity": [],
    "lineas_afectadas": [],
    "estaciones_afectadas": []
}

lineas = set()
estaciones = set()

for entity in feed.entity:

    if not entity.HasField(
        "alert"
    ):
        continue

    alert = entity.alert

    texto = ""

    if (
        alert.description_text.translation
    ):
        texto = (
            alert
            .description_text
            .translation[0]
            .text
        )

    lineas_alerta = []

    for informed in alert.informed_entity:

        if informed.route_id:

            m = re.search(
                r"(C\d+[ABab]?)",
                informed.route_id,
                re.IGNORECASE
            )

            if m:

                linea = (
                    m.group(1)
                    .upper()
                )

                lineas_alerta.append(
                    linea
                )

                lineas.add(
                    linea
                )

    estaciones_en_texto = []

    patrones = [

        r"parada en ([A-Za-zÁÉÍÓÚÜÑñ\s\-]+)",
        r"estación(?:es)? ([A-Za-zÁÉÍÓÚÜÑñ\s\-]+)",
        r"entre ([A-Za-zÁÉÍÓÚÜÑñ\s\-]+) y ([A-Za-zÁÉÍÓÚÜÑñ\s\-]+)"

    ]

    for patron in patrones:

        for coincidencia in re.finditer(
            patron,
            texto,
            re.IGNORECASE
        ):

            grupos = coincidencia.groups()

            for g in grupos:

                if not g:
                    continue

                nombre = g.strip()

                estaciones.add(
                    nombre
                )

                estaciones_en_texto.append(
                    nombre
                )

    resultado["entity"].append({

        "texto":
            texto,

        "lineas":
            lineas_alerta,

        "estaciones":
            estaciones_en_texto

    })

resultado[
    "lineas_afectadas"
] = sorted(
    list(lineas)
)

resultado[
    "estaciones_afectadas"
] = sorted(
    list(estaciones)
)

with open(
    "incidencias.json",
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
    f"{len(resultado['entity'])} incidencias procesadas"
)
