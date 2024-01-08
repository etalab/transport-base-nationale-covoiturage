import csv
import requests
from prettytable import PrettyTable

FILENAME = "datasets.csv"
TARGET_SCHEMA = "etalab/schema-lieux-covoiturage"
URL_SCHEMA = (
    "https://raw.githubusercontent.com/etalab/lieux-covoiturage/master/schema.json"
)


def get_slug(dataset_url):
    return dataset_url.replace("https://www.data.gouv.fr/fr/datasets/", "")


def dataset_api_url(dataset_url):
    return f"https://www.data.gouv.fr/api/1/datasets/{get_slug(dataset_url)}"


def validata(resource_url):
    params = {"url": resource_url, "schema": URL_SCHEMA}
    validata_response = requests.get(
        "https://api.validata.etalab.studio/validate", params=params
    )
    validata_response.raise_for_status()
    return validata_response.json()["report"]


with open(FILENAME) as f:
    x = PrettyTable()
    x.field_names = ["LINE", "DATASET", "RESSOURCE", "NB ROWS", "VALIDE", "ERROR"]
    nb_rows = 0
    rows = [r for r in csv.DictReader(f)]
    errors = []
    for row_number, row in enumerate(rows, 1):
        dataset_url = row["dataset_url"]
        response = requests.get(dataset_api_url(dataset_url))
        response.raise_for_status()
        hasSchema = False

        for r in response.json()["resources"]:
            if r["schema"].get("name") == TARGET_SCHEMA:
                hasSchema = True
                validataInfo = validata(r["url"])
                x.add_row(
                    [
                        row_number,
                        get_slug(dataset_url),
                        r["title"],
                        validataInfo["tasks"][0]["resource"]["stats"]["rows"],
                        validataInfo.get("valid"),
                        "",
                    ]
                )
                nb_rows += validataInfo["tasks"][0]["resource"]["stats"]["rows"]

        if not hasSchema:
            x.add_row(
                [
                    row_number,
                    get_slug(dataset_url),
                    "",
                    "",
                    False,
                    "Aucune ressource avec le schéma",
                ]
            )

    x.add_row(["-", "---", "TOTAL", nb_rows, "", ""])


print(x)
