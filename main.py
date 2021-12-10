"""
GUI Application for converting currencies using forex_python module
"""

from typing import Optional
import sys

from PyQt5 import QtGui, QtWidgets
from forex_python.converter import CurrencyCodes, CurrencyRates


rates = CurrencyRates()
codes = CurrencyCodes()


ICON_PATH = "Assets/exchange.png"

currency_codes = (
    "JPY", "CNY", "SDG", "RON", "MKD", "MXN", "CAD", "XAF", "GYD", "AFN",
    "ZAR", "AUD", "NOK", "ILS", "ISK", "SYP", "LYD", "UYU", "YER", "CSD",
    "EEK", "THB", "IDR", "LBP", "AED", "BOB", "QAR", "BHD", "HNL", "HRK",
    "COP", "ALL", "DKK", "MYR", "SEK", "RSD", "BGN", "DOP", "KRW", "LVL",
    "VEF", "CZK", "TND", "KWD", "VND", "JOD", "NZD", "PAB", "CLP", "PEN",
    "GBP", "DZD", "CHF", "RUB", "UAH", "ARS", "SAR", "EGP", "INR", "PYG",
    "TWD", "TRY", "BAM", "OMR", "SGD", "MAD", "BYR", "NIO", "HKD", "LTL",
    "SKK", "GTQ", "BRL", "EUR", "HUF", "IQD", "CRC", "PHP", "SVC", "PLN",
    "USD", "XBB", "XBC", "XBD", "UGX", "MOP", "SHP", "TTD", "UYI", "KGS",
    "DJF", "BTN", "XBA", "HTG", "BBD", "XAU", "FKP", "MWK", "PGK", "XCD",
    "COU", "RWF", "NGN", "BSD", "XTS", "TMT", "SOS", "TOP", "AOA", "KPW",
    "GEL", "VUV", "FJD", "MVR", "AZN", "MNT", "MGA", "WST", "KMF", "GNF",
    "SBD", "BDT", "MMK", "TJS", "CVE", "MDL", "KES", "SRD", "LRD", "MUR",
    "CDF", "BMD", "USN", "CUP", "USS", "GMD", "UZS", "CUC", "ZMK", "NPR",
    "NAD", "LAK", "SZL", "XDR", "BND", "TZS", "MXV", "LSL", "KYD", "LKR",
    "ANG", "PKR", "SLL", "SCR", "GHS", "ERN", "BOV", "GIP", "IRR", "XPT",
    "BWP", "XFU", "CLF", "ETB", "STD", "XXX", "XPD", "AMD", "XPF", "JMD",
    "MRO", "BIF", "CHW", "ZWL", "AWG", "MZN", "CHE", "XOF", "KZT", "BZD",
    "XAG", "KHR",
)


def qml_sheet(name) -> str:
    return open(f"Assets/Scripts/{name}.qss").read()


class MainWindowWrapper(QtWidgets.QMainWindow):
    """It works? Adds exit prompt functionality"""
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.buttons = QtWidgets.QMessageBox.StandardButton

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        Yes, No = self.buttons.Yes, self.buttons.No
        title = "Exit Prompt"
        message = "Are you sure you want to exit?"
        reply = QtWidgets.QMessageBox.question(self, title, message, Yes | No)

        if reply == self.buttons.Yes:
            a0.accept()
        else:
            a0.ignore()


class MainWindow(MainWindowWrapper):
    """Main Window for application."""
    def __init__(self, size: tuple[int, int], title: str,
                 icon: QtGui.QIcon,
                 parent: Optional[QtWidgets.QWidget] = None):
        super(MainWindow, self).__init__(parent)

        self.ui = {}
        self.shortcuts = {}

        self.setFixedSize(*size)
        self.setWindowTitle(title)
        self.setWindowIcon(icon)

        self.setup_ui()
        self.setup_shortcuts()

    def setup_ui(self):
        self.ui["background"] = QtWidgets.QLabel(self)
        self.ui["background"].setGeometry(0, 0, self.width(), self.height())
        self.ui["background"].setStyleSheet(qml_sheet("background"))

        self.ui["logo"] = QtWidgets.QLabel(self)
        self.ui["logo"].setGeometry(self.width() - 138, 10, 128, 128)
        self.ui["logo"].setPixmap(QtGui.QPixmap(ICON_PATH).scaled(128, 128))

    def setup_shortcuts(self):
        pass


def main():
    """Main Function to run program"""
    app = QtWidgets.QApplication(sys.argv)

    width, height = 640, 480
    title = "Window Title"
    icon = QtGui.QIcon("Assets/exchange.png")
    parent = None

    window = MainWindow((width, height), title, icon, parent)
    window.show()

    print(f"Exit Code: {app.exec()}")


if __name__ == "__main__":
    main()
