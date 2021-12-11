from datetime import datetime

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from currency import get_rate


def generate_graph(code1: str, code2: str,
                   filename: str = "graph.png"):
    data = get_rate(code1)


generate_graph("GBP", "USD")

matplotlib.use("Qt5Agg")
