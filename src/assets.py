import os

normalise = os.path.normpath


def temp(name: str) -> str:
    return normalise(f"../temp/{name}")


def image(name: str) -> str:
    return normalise(f"../assets/images/{name}")

def script(name: str) -> str:
    return normalise(f"../assets/scripts/{name}")


class Assets:
    class Images:
        exchange = image("exhange.png")
        money = image("money.png")

    class Scripts:
        # qss
        background = script("qss/background.qss")
        button = script("qss/button.qss")
        combo_box = script("qss/combo_box.qss")
        show_graph = script("qss/show_graph.qss")

        # csv
        currency_codes = script("csv/codes.csv")
        default_currencies = script("csv/default_currencies.csv")

    class Temp:
        # json
        response = temp("response.json")

        # log
        urls = temp("urls.log")

        # svg
        graph = temp("graph.svg")
