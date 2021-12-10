from datapackage import Package as Pkg
from typing import Optional
import os


def get_cache() -> Optional[list[str]]:
    if os.path.exists("codes.csv"):
        return open("codes.csv").read().split(",")


def cache_codes(codes: list[str]):
    if os.path.exists("codes.csv"):
        return

    open("codes.csv", "w").write(",".join(codes))


def get_codes() -> list[str]:
    cache = get_cache()

    print(f"{cache=}")

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
