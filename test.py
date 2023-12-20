import csv

import requests

FILENAME = "datasets.csv"
TARGET_SCHEMA = "etalab/schema-lieux-covoiturage"
URL_SCHEMA = "https://raw.githubusercontent.com/etalab/lieux-covoiturage/master/schema.json"


def dataset_api_url(dataset_url):
    slug = dataset_url.replace("https://www.data.gouv.fr/fr/datasets/", "")
    return f"https://www.data.gouv.fr/api/1/datasets/{slug}"

def ressource_validation(ressource_url):
        params = {"url":ressource_url , "schema": URL_SCHEMA}
        response_validata = requests.get("https://api.validata.etalab.studio/validate", params=params)
        response_validata.raise_for_status()
        return response_validata.json()["report"].get("valid")

with open(FILENAME) as f:
    rows = [r for r in csv.DictReader(f)]
    errors = []
    row_number = 1
    for row in rows:
        row_number += 1
        dataset_url = row["dataset_url"]
        response = requests.get(dataset_api_url(dataset_url))
        response.raise_for_status()
        haveSchema = False

        for r in response.json()["resources"]:
            if r["schema"].get("name") == TARGET_SCHEMA:
                haveSchema = True
                if not ressource_validation(r["url"]):
                    errors.append(f"LIGNE {row_number} - {dataset_url} : la ressource {r['title']} n'est pas conforme au schéma")
        
        if not haveSchema:
            errors.append(f"LIGNE {row_number} - {dataset_url} : aucune ressource avec le schéma")
        

    if len(errors) > 0:
        raise ValueError('\n'.join(errors))

    urls = [r["dataset_url"] for r in rows]
    duplicates = set([u for u in urls if urls.count(u) > 1])
    if len(duplicates) > 0:
        raise ValueError(f"{FILENAME} ne doit pas contenir de doublons. Doublons : f{duplicates}")
