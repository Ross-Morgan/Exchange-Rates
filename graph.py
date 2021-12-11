from datetime import date, timedelta

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

from currency import get_rates

matplotlib.use("Qt5Agg")


def generate_graph(currency_from: str,
                   currency_to: str):

    date_from = date.today() - timedelta(days=29)
    date_to = date.today()

    json_data = get_rates(currency_from, date_from, date_to)

    fig, ax = plt.subplots(figsize=(12, 6))

    hist_data = []
    for key, value in json_data.items():
        hist_dict = {"date": key, "rate": value[currency_to]}
        hist_data.append(hist_dict)

    hist_data.sort(key=lambda x: x["date"])

    from pprint import pprint
    pprint(hist_data, indent=4)

    df = pd.DataFrame(hist_data)

    x = df["date"]
    y = df["rate"]

    plt.plot(x, y)

    plt.xticks(rotation=90)

    plt.xlabel("Date")
    plt.ylabel("Exchange Rate")

    plt.savefig("graph.svg")


if __name__ == "__main__":
    generate_graph("GBP", "USD")
