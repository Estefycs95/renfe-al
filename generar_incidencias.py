import json

with open(
    "incidencias.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        {
            "entity": []
        },
        f,
        ensure_ascii=False,
        indent=2
    )

print("incidencias.json generado")
