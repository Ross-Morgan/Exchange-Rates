# stdlib imports
from contextlib import suppress
from typing import Optional, Union
import sys

# installed module imports
from forex_python.converter import CurrencyCodes, CurrencyRates
from PyQt6 import QtGui, QtWidgets

# local module imports
from currency import get_codes, get_default_currency


ICON_PATH = "Assets/exchange.png"


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
    ui_types = dict[str, dict[str, Union[
        QtWidgets.QComboBox, QtWidgets.QLabel,
        QtWidgets.QPushButton
    ]]]

    """Main Window for application."""
    def __init__(self, size: tuple[int, int], title: str,
                 icon: QtGui.QIcon,
                 parent: Optional[QtWidgets.QWidget] = None) -> None:
        super(MainWindow, self).__init__(parent)

        self.ui: MainWindow.ui_types = {}
        self.shortcuts: dict[str, QtGui.QShortcut] = {}

        self.curr_codes = get_codes()

        self.setFixedSize(*size)
        self.setWindowTitle(title)
        self.setWindowIcon(icon)

        self.setup_ui()
        self.setup_shortcuts()

    def setup_ui(self) -> None:
        self.ui["background"] = QtWidgets.QLabel(self)
        self.ui["background"].setGeometry(0, 0, self.width(), self.height())
        self.ui["background"].setStyleSheet(qml_sheet("background"))

        _insert_policy = QtWidgets.QComboBox.InsertPolicy.InsertAlphabetically
        _default_currency = 0

        with suppress(ValueError):
            _default_currency = self.curr_codes.index(get_default_currency())

        self.ui["fields"] = {}

        self.ui["fields"]["input"] = QtWidgets.QComboBox(self)
        self.ui["fields"]["input"].setGeometry(10, 10, 150, 50)
        self.ui["fields"]["input"].setInsertPolicy(_insert_policy)
        self.ui["fields"]["input"].setCurrentIndex(_default_currency)

        self.ui["fields"]["output"] = QtWidgets.QComboBox(self)
        self.ui["fields"]["output"].setGeometry(170, 10, 150, 50)
        self.ui["fields"]["output"].setInsertPolicy(_insert_policy)
        self.ui["fields"]["output"].setCurrentIndex(_default_currency)

        for field in self.ui["fields"].values():
            # * Fixed speed with caching, I'm proud of myself :)
            field.addItems(self.curr_codes)

        self.ui["logo"] = QtWidgets.QLabel(self)
        self.ui["logo"].setGeometry(self.width() - 138, 10, 128, 128)
        self.ui["logo"].setPixmap(QtGui.QPixmap(ICON_PATH).scaled(128, 128))

        # TODO: Add offline mode with cached variables
        # TODO: Maybe only conversions to and from 1 currency to save space
        # TODO: This could lead to rounding inaccuracies (due to floats)

    def setup_shortcuts(self) -> None:
        QKSq = QtGui.QKeySequence
        QSct = QtGui.QShortcut

        self.shortcuts["exit"] = QSct(QKSq("ctrl+w"), self)
        self.shortcuts["exit"].activated.connect(lambda: self.close())

        self.shortcuts


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
    import cProfile
    import pstats

    with cProfile.Profile() as pr:
        main()

    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.dump_stats("profile.prof")
