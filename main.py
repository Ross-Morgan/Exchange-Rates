# Stdlib imports
from contextlib import suppress
from typing import Optional, Union
import sys

# Installed module imports
from PyQt6 import QtGui, QtWidgets

# Local module imports
from currency import (
    get_codes, get_default_currency,
    get_symbol,
    convert as _convert
)


ICON_PATH = "Assets/exchange.png"


def qss_sheet(name) -> str:
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

        self.curr_codes = list(get_codes())

        self.setFixedSize(*size)
        self.setWindowTitle(title)
        self.setWindowIcon(icon)

        self.setup_ui()
        self.setup_shortcuts()

    def setup_ui(self) -> None:
        _insert_policy = QtWidgets.QComboBox.InsertPolicy.InsertAlphabetically
        _default_currs = ("GBP", "USD")

        with suppress(ValueError):
            _default_currs = get_default_currency()

        self.ui["background"] = QtWidgets.QLabel(self)
        self.ui["background"].setGeometry(0, 0, self.width(), self.height())
        self.ui["background"].setStyleSheet(qss_sheet("background"))

        self.ui["logo"] = QtWidgets.QLabel(self)
        self.ui["logo"].setGeometry(self.width() - 144, 16, 128, 128)
        self.ui["logo"].setPixmap(QtGui.QPixmap(ICON_PATH).scaled(128, 128))

        self.ui["fields"] = {}

        self.ui["fields"]["code1"] = QtWidgets.QComboBox(self)
        self.ui["fields"]["code1"].setGeometry(20, 20, 200, 75)
        self.ui["fields"]["code1"].setInsertPolicy(_insert_policy)
        self.ui["fields"]["code1"].setFont(QtGui.QFont("helvetica", 20))

        self.ui["fields"]["code2"] = QtWidgets.QComboBox(self)
        self.ui["fields"]["code2"].setGeometry(240, 20, 200, 75)
        self.ui["fields"]["code2"].setInsertPolicy(_insert_policy)
        self.ui["fields"]["code2"].setFont(QtGui.QFont("helvetica", 20, 1))

        for i, field in enumerate([
                self.ui["fields"]["code1"],
                self.ui["fields"]["code2"]]):  # * Speedy thanks to caching :D
            field.addItems(sorted(self.curr_codes))
            field.setCurrentIndex(field.findText(_default_currs[i]))

        self.ui["fields"]["input1"] = QtWidgets.QLineEdit(self)
        self.ui["fields"]["input1"].setGeometry(20, 115, 200, 75)
        self.ui["fields"]["input1"].setPlaceholderText("Amount: ")
        self.ui["fields"]["input1"].setFont(QtGui.QFont("helvetica", 20))

        self.ui["fields"]["input2"] = QtWidgets.QLineEdit(self)
        self.ui["fields"]["input2"].setGeometry(240, 115, 200, 75)
        self.ui["fields"]["input2"].setPlaceholderText("Amount: ")
        self.ui["fields"]["input2"].setFont(QtGui.QFont("helvetica", 20))

        self.ui["buttons"] = {}
        self.ui["buttons"]["convert"] = QtWidgets.QPushButton("CONVERT", self)
        self.ui["buttons"]["convert"].setGeometry(20, 210, 420, 50)
        self.ui["buttons"]["convert"].setFont(QtGui.QFont("helvetica", 20))
        self.ui["buttons"]["convert"].setStyleSheet(qss_sheet("convert"))
        self.ui["buttons"]["convert"]

        # TODO: Add offline mode with cached variables
        # TODO: Maybe only conversions to and from 1 currency to save space
        # TODO: This could lead to rounding inaccuracies (due to floats)

    def setup_shortcuts(self) -> None:
        QKSq = QtGui.QKeySequence
        QSct = QtGui.QShortcut

        self.shortcuts["exit"] = QSct(QKSq("ctrl+w"), self)
        self.shortcuts["exit"].activated.connect(self.close)

        self.shortcuts["get_rate"] = QSct(QKSq("enter"), self)
        self.shortcuts["get_rate"].activated.connect(self.convert)

    def convert(self):
        code1 = self.ui["fields"]["input"].currentData()
        code2 = self.ui["fields"]["output"].currentData()

        print((code1, code2))

        rate = _convert(code1, code2, 10)

        print(10, rate)

    def text_changed(self, field: str):
        text = self.ui["fields"][field].text()
        selected_code = self.ui["fields"][field].currentData()
        print(f"{selected_code=}")

        text = "".join([get_symbol(selected_code), text[1:4]])

        self.ui["fields"][field].setText(text)


def main():
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
