# Stdlib imports
from datetime import datetime
from typing import Optional
import os
import re

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


def cache_currency_codes(currency_codes: set[str]):
    open(CODES_PATH, "w+").write(",".join(currency_codes))


def get_country() -> str:
    return httpx.get(API_URL).json()["location"]["country"]["name"]


def get_codes() -> set[str]:
    cache = get_codes_cache()

    if cache:
        return set(cache)

    package = Pkg("https://datahub.io/core/currency-codes/datapackage.json")
    currency_codes: list[str] = set()

    for resource in package.resources:
        if resource.descriptor["datahub"]["type"] != "derived/csv":
            continue

        currency_codes = set(map(lambda x: x[2], resource.read()))

        while None in currency_codes:
            currency_codes.remove(None)

        break

    cache_currency_codes(currency_codes)

    return currency_codes


def set_default_currency(code: str):
    open(DEFAULT_CURRENCY_PATH, "w+").write(code.upper())


def get_default_currency() -> tuple[str, str]:
    if os.path.exists(DEFAULT_CURRENCY_PATH):
        return open(DEFAULT_CURRENCY_PATH).read().strip().split(",")[0:2]


def get_symbol(code: str) -> str:
    return codes.get_symbol(code)


def remove_symbol(val: str) -> float:
    if not val.isdecimal():
        return 0.0
    return float(re.compile(r"[^\d.]+").sub("", val))


def get_rate(code1: str, code2: str, date: datetime = None) -> float:
    return rates.get_rate(code1, code2, date)


def convert(code1: str, code2: str, val: float, date: datetime) -> float:
    return rates.convert(code1, code2, val, date)


if __name__ == "__main__":
    print(remove_symbol("US$69,420.69"))
