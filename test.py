import csv

import requests

FILENAME = "datasets.csv"
TARGET_SCHEMA = "etalab/schema-lieux-covoiturage"
URL_SCHEMA = "https://schema.data.gouv.fr/schemas/etalab/schema-lieux-covoiturage/latest/schema.json"


def dataset_api_url(dataset_url):
    slug = dataset_url.replace("https://www.data.gouv.fr/fr/datasets/", "")
    return f"https://www.data.gouv.fr/api/1/datasets/{slug}"


def resource_is_valid(resource_url):
    params = {"url": resource_url, "schema": URL_SCHEMA}
    validata_response = requests.get("https://api.validata.etalab.studio/validate", params=params)
    validata_response.raise_for_status()
    return validata_response.json()["report"].get("valid")


with open(FILENAME) as f:
    rows = [r for r in csv.DictReader(f)]
    errors = []
    for row_number, row in enumerate(rows, 1):
        dataset_url = row["dataset_url"]
        response = requests.get(dataset_api_url(dataset_url))
        response.raise_for_status()
        hasSchema = False

        for r in response.json()["resources"]:
            if r["schema"] is not None and r["schema"].get("name") == TARGET_SCHEMA:
                hasSchema = True
                if not resource_is_valid(r["url"]):
                    errors.append(
                        f"LIGNE {row_number} - {dataset_url} : la ressource {r['title']} n'est pas conforme au schéma"
                    )

        if not hasSchema:
            errors.append(f"LIGNE {row_number} - {dataset_url} : aucune ressource avec le schéma")

    if len(errors) > 0:
        raise ValueError("\n".join(errors))

    urls = [r["dataset_url"] for r in rows]
    duplicates = set([u for u in urls if urls.count(u) > 1])
    if len(duplicates) > 0:
        raise ValueError(f"{FILENAME} ne doit pas contenir de doublons. Doublons : f{duplicates}")
