from datapackage import Package as Pkg
from typing import Optional
import httpx
import os

CODES_PATH = "Assets/Scripts/codes.csv"
DEFAULT_CURRENCY_PATH = "ASsets/Scripts/default_currency.csv"
API_URL = "https://api.ipregistry.co/?key=tryout&fields=location.country"


def get_codes_cache() -> Optional[list[str]]:
    if os.path.exists(CODES_PATH):
        return open(CODES_PATH).read().strip().split(",")


def cache_currency_codes(codes: list[str]):
    open(CODES_PATH, "w+").write(",".join(codes))


def get_country() -> str:
    return httpx.get(API_URL).text


def get_codes() -> list[str]:
    cache = get_codes_cache()

    if cache:
        return cache

    package = Pkg("https://datahub.io/core/currency-codes/datapackage.json")
    codes: list[str] = []

    for resource in package.resources:
        if resource.descriptor["datahub"]["type"] != "derived/csv":
            continue

        codes = list(map(lambda x: x[2], resource.read()))

        while None in codes:
            codes.remove(None)

        break

    cache_currency_codes(codes)

    return codes


def set_default_currency(curr: str):
    open(DEFAULT_CURRENCY_PATH, "w+").write(curr.upper())


# TODO return random if multiple codes are in file
def get_default_currency() -> tuple[str, str]:
    if os.path.exists(DEFAULT_CURRENCY_PATH):
        return open(DEFAULT_CURRENCY_PATH).read().strip().split(",")[0:2]
