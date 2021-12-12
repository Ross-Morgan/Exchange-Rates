# Stdlib imports
import json
import os
import re
import subprocess
from datetime import date, timedelta
from enum import Enum, auto
from typing import Optional

# Installed module imports
import httpx


class API(Enum):
    LATEST = auto()
    HISTORICAL = auto()


CODES_PATH = "Assets/csv/codes.csv"
DEFAULT_CURRENCY_PATH = "Assets/csv/default_currency.csv"

IPKEY = os.getenv("IPREGISTRY_API_KEY")  # IP_API_KEY but line length limit :(
IP_API_URL = f"https://api.ipregistry.co/?key={IPKEY}&fields=location.country"

RATES_API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")
RATES_API_ENDPOINTS = {
    API.LATEST: "https://freecurrencyapi.net/api/v2/latest?apikey={}",
    API.HISTORICAL: "https://freecurrencyapi.net/api/v2/historical?apikey={}",
}

float_regex = re.compile(r"[^\d.]+")
devnull = open(os.devnull, "wb")


def get_codes_cache() -> Optional[set[str]]:
    if os.path.exists(CODES_PATH):
        return set(open(CODES_PATH).read().strip().split(","))


def cache_currency_codes(currency_codes: set[str]):
    set(open(CODES_PATH, "w+").write(",".join(currency_codes)))


def get_country() -> str:
    return httpx.get(IP_API_URL).json()["location"]["country"]["name"]


def get_codes() -> set[str]:
    cache = get_codes_cache()

    if cache:
        return cache

    currency_codes: set[str] = set()

    stdout, stderr = subprocess.Popen(["curl", _construct_url(
                                      API.LATEST, "GBP")],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.DEVNULL).communicate()

    if stderr:
        print(stderr.decode("utf-8"))
        raise(subprocess.SubprocessError())

    stdout: dict[str, float] = json.loads(stdout.decode("utf-8"))["data"]

    currency_codes: set[str] = set(stdout.keys())

    cache_currency_codes(currency_codes)

    return currency_codes


def set_default_currency(code: str):
    open(DEFAULT_CURRENCY_PATH, "w+").write(code.upper())


def get_default_currency() -> tuple[str, str]:
    if os.path.exists(DEFAULT_CURRENCY_PATH):
        return open(DEFAULT_CURRENCY_PATH).read().strip().split(",")[0:2]


def floatify(val: str) -> float:
    if not val:
        return 0.0
    return float(float_regex.sub("", val))


def _construct_url(mode: API, base_currency: str,
                   date_from: date = None,
                   date_to: date = None):
    url = [
        RATES_API_ENDPOINTS[mode].format(RATES_API_KEY),
        f"base_currency={base_currency}",
    ]

    if date_from is not None:
        url.append(f"date_from={date_from.strftime('%Y-%m-%d')}")
    if date_to is not None:
        url.append(f"date_to={date_to.strftime('%Y-%m-%d')}")

    print("&".join(url), open("urls.log", "a"))

    return "&".join(url)


# TODO: Merge functions to (repeated code)


def get_rate(code1: str, code2: str,
             date: date) -> float:
    mode = (API.HISTORICAL if date is not None
            else API.LATEST)

    stdout, stderr = subprocess.Popen(["curl", _construct_url(
                                      mode, code1, date)],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.DEVNULL).communicate()

    if stderr:
        print(stderr.decode("utf-8"))
        raise(subprocess.SubprocessError())

    rates = json.loads(stdout)["data"]

    print(json.dumps(rates, indent=4), file=open("response.json", "w"))

    return rates[date.strftime("%Y-%m-%d")][code2]


def get_rates(code1: str,
              date_from: Optional[date] = None,
              date_to: Optional[date] = None) -> dict[str, dict[str, float]]:
    mode = (API.HISTORICAL if date_from is not None else API.LATEST)

    stdout, stderr = subprocess.Popen(["curl", _construct_url(
                                      mode, code1, date_from, date_to)],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.DEVNULL).communicate()

    if stderr:
        print(stderr.decode("utf-8"))
        raise(subprocess.SubprocessError())

    rates: list[dict[str, float]] = json.loads(stdout)["data"]

    print(json.dumps(rates, indent=4), file=open("response.json", "w"))

    return rates


def convert(code1: str, code2: str, val: float,
            dt: Optional[date] = None) -> float:
    rate = get_rate(code1, code2, dt)
    return round(val * rate, 3)


if __name__ == "__main__":
    get_rates("GBP", date.today() - timedelta(days=30), date.today())
