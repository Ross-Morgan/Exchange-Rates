from datetime import datetime

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from currency import get_rate


def generate_graph(data: dict[str, dict[str, float]],
                   currency_to: str):
    data = get_rate(code1)


generate_graph("GBP", "USD")

matplotlib.use("Qt5Agg")
