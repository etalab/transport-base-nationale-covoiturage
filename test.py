import csv

import requests

FILENAME = "datasets.csv"
TARGET_SCHEMA = "etalab/schema-lieux-covoiturage"


def dataset_api_url(dataset_url):
    slug = dataset_url.replace("https://www.data.gouv.fr/fr/datasets/", "")
    return f"https://www.data.gouv.fr/api/1/datasets/{slug}"


with open(FILENAME) as f:
    rows = [r for r in csv.DictReader(f)]
    for row in rows:
        dataset_url = row["dataset_url"]
        response = requests.get(dataset_api_url(dataset_url))
        response.raise_for_status()
        if not any(
            [
                r
                for r in response.json()["resources"]
                if r["schema"].get("name") == TARGET_SCHEMA
            ]
        ):
            raise ValueError(
                f"{dataset_url} ne contient aucune ressource avec le schéma de covoiturage"
            )

    urls = [r["dataset_url"] for r in rows]
    if len(urls) != len(set(urls)):
        raise ValueError(f"{FILENAME} ne doit pas contenir de doublons")
