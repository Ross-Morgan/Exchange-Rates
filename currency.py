# Stdlib imports
from datetime import date
from typing import Optional
import os

# Install module imports
from forex_python.converter import CurrencyCodes, CurrencyRates
from datapackage import Package as Pkg
import httpx


CODES_PATH = "Assets/Scripts/csv/codes.csv"
DEFAULT_CURRENCY_PATH = "ASsets/Scripts/csv/default_currency.csv"
API_KEY = os.getenv("IPREGISTRY_API_KEY")
API_URL = f"https://api.ipregistry.co/?key={API_KEY}&fields=location.country"

codes = CurrencyCodes()
rates = CurrencyRates()


def get_codes_cache() -> Optional[list[str]]:
    if os.path.exists(CODES_PATH):
        return open(CODES_PATH).read().strip().split(",")


def cache_currency_codes(codes: set[str]):
    open(CODES_PATH, "w+").write(",".join(codes))


def get_country() -> str:
    return httpx.get(API_URL).json()["location"]["country"]["name"]


def get_codes() -> set[str]:
    cache = get_codes_cache()

    if cache:
        return set(cache)

    package = Pkg("https://datahub.io/core/currency-codes/datapackage.json")
    codes: list[str] = set()

    for resource in package.resources:
        if resource.descriptor["datahub"]["type"] != "derived/csv":
            continue

        codes = set(map(lambda x: x[2], resource.read()))

        while None in codes:
            codes.remove(None)

        break

    cache_currency_codes(codes)

    return codes


def set_default_currency(code: str):
    open(DEFAULT_CURRENCY_PATH, "w+").write(code.upper())


def get_default_currency() -> tuple[str, str]:
    if os.path.exists(DEFAULT_CURRENCY_PATH):
        return open(DEFAULT_CURRENCY_PATH).read().strip().split(",")[0:2]


def get_symbol(code: str) -> str:
    return codes.get_symbol(code)


def get_rate(code1: str, code2: str, date: date = None) -> float:
    return rates.get_rate(code1, code2, date)


def convert(code1: str, code2: str, val: float, date: date) -> float:
    return rates.convert(code1, code2, val, date)
