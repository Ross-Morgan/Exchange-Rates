from datetime import date, timedelta

import matplotlib.pyplot as plt
import pandas as pd

from currency import get_rate


def generate_graph(code1: str, code2: str,
                   filename: str = "graph.png"):

    dates: list[date] = [date.today() - timedelta(weeks=20)]
    rates: list[float] = []

    for i in range(19):
        dates.append(dates[i] + timedelta(weeks=1))

    for i in range(20):
        rates.append(get_rate(code1, code2, dates[i]))

    dates = list(map(lambda d: date.strftime(d, "%d/%m"), dates))

    df = pd.DataFrame({
        "Date": dates,
        "Exchange_Rate": rates,
    }, columns=["Date", "Exchange_Rate"])

    plt.plot(df["Date"], df["Exchange_Rate"])
    plt.title(f"Exchange rate for {code1} -> {code2}", fontsize=14)
    plt.xlabel("Date")
    plt.ylabel("Exchange Rate")
    plt.grid(False)
    plt.show()

import cProfile
import pstats


with cProfile.Profile() as pr:
    generate_graph("GBP", "USD")

stats = pstats.Stats(pr)
stats.sort_stats(pstats.SortKey.TIME)
stats.dump_stats("profile.prof")
