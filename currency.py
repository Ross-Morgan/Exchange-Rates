from datapackage import Package as Pkg
from typing import Optional
import os

CSV_PATH = "Assets/Scripts/codes.csv"


def get_cache() -> Optional[list[str]]:
    if os.path.exists(CSV_PATH):
        return open(CSV_PATH).read().split(",")


def cache_codes(codes: list[str]):
    if os.path.exists(CSV_PATH):
        return

    open(CSV_PATH, "w").write(",".join(codes))


def get_codes() -> list[str]:
    cache = get_cache()

    if cache:
        return cache

    package = Pkg('https://datahub.io/core/currency-codes/datapackage.json')
    codes: list[str] = []

    for resource in package.resources:
        if resource.descriptor["datahub"]["type"] != "derived/csv":
            continue

        codes = list(map(lambda x: x[2], resource.read()))

        while None in codes:
            codes.remove(None)

        break

    cache_codes(codes)

    return codes
