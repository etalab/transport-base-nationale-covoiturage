import csv
import requests
from prettytable import PrettyTable

FILENAME = "datasets.csv"
TARGET_SCHEMA = "etalab/schema-lieux-covoiturage"
URL_SCHEMA = "https://schema.data.gouv.fr/schemas/etalab/schema-lieux-covoiturage/latest/schema.json"


def dataset_slug(dataset_url):
    return dataset_url.replace("https://www.data.gouv.fr/fr/datasets/", "")


def dataset_api_url(dataset_url):
    return f"https://www.data.gouv.fr/api/1/datasets/{dataset_slug(dataset_url)}"


def get_validata_report(resource_url):
    params = {"url": resource_url, "schema": URL_SCHEMA}
    validata_response = requests.get("https://api.validata.etalab.studio/validate", params=params)
    validata_response.raise_for_status()
    return validata_response.json()["report"]


with open(FILENAME) as f:
    table = PrettyTable()
    table.field_names = ["LINE", "DATASET", "RESOURCE", "NB ROWS", "VALID", "ERROR"]
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
                validataReport = get_validata_report(r["url"])
                nbRowsInFile = validataReport["tasks"][0]["resource"]["stats"]["rows"]
                table.add_row(
                    [
                        row_number,
                        dataset_slug(dataset_url),
                        r["title"],
                        nbRowsInFile,
                        validataReport.get("valid"),
                        "",
                    ]
                )
                nb_rows += nbRowsInFile

        if not hasSchema:
            table.add_row(
                [
                    row_number,
                    dataset_slug(dataset_url),
                    "",
                    "",
                    False,
                    "Aucune ressource avec le schéma",
                ]
            )

    table.add_row(["-", "---", "TOTAL", nb_rows, "", ""])

print(table)
