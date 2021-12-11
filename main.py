from __future__ import annotations

# Stdlib imports
import sys
from contextlib import suppress
from datetime import datetime
from typing import Optional, Union

# Installed module imports
from PyQt6 import QtGui, QtWidgets

# Local module imports
from currency import convert as _convert
from currency import floatify, get_codes, get_default_currency


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
        QtWidgets.QPushButton, QtWidgets.QLineEdit,
        QtWidgets.QDateTimeEdit
    ]]]

    """Main Window for application."""
    def __init__(self, size: tuple[int, int], title: str,
                 icon: QtGui.QIcon,
                 parent: Optional[QtWidgets.QWidget] = None) -> None:
        super(MainWindow, self).__init__(parent)

        self.ui: MainWindow.ui_types = {}
        self.shortcuts: dict[str, QtGui.QShortcut] = {}
        self.icon = "Assets/exchange.png"

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
        self.ui["logo"].setGeometry(self.width() - 154, 16, 128, 128)
        self.ui["logo"].setPixmap(QtGui.QPixmap(self.icon).scaled(128, 128))

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

        self.ui["fields"]["input"] = QtWidgets.QLineEdit(self)
        self.ui["fields"]["input"].setGeometry(20, 115, 200, 75)
        self.ui["fields"]["input"].setPlaceholderText("Amount: ")
        self.ui["fields"]["input"].setFont(QtGui.QFont("helvetica", 20))

        self.ui["fields"]["output"] = QtWidgets.QLineEdit(self)
        self.ui["fields"]["output"].setGeometry(240, 115, 200, 75)
        self.ui["fields"]["output"].setPlaceholderText("Result: ")
        self.ui["fields"]["output"].setFont(QtGui.QFont("helvetica", 20))
        self.ui["fields"]["output"].setReadOnly(True)

        self.ui["fields"]["date"] = QtWidgets.QDateTimeEdit

        self.ui["buttons"] = {}
        self.ui["buttons"]["convert"] = QtWidgets.QPushButton("CONVERT", self)
        self.ui["buttons"]["convert"].setGeometry(20, 210, 420, 50)
        self.ui["buttons"]["convert"].setFont(QtGui.QFont("helvetica", 20))
        self.ui["buttons"]["convert"].setStyleSheet(qss_sheet("convert"))
        self.ui["buttons"]["convert"].clicked.connect(self.convert)

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
        code1_index: int = self.ui["fields"]["code1"].currentIndex()
        code2_index: int = self.ui["fields"]["code2"].currentIndex()

        code1 = self.curr_codes[code1_index]
        code2 = self.curr_codes[code2_index]

        val = floatify(self.ui["fields"]["input"].text())

        print((code1, code2), val)

        rate = _convert(code1, code2, val, datetime.now())

        print(f"{code1}: {val} | {code2}: {rate}")


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
    DEBUG = True

    if DEBUG:
        import cProfile
        import pstats

        with cProfile.Profile() as pr:
            main()

        stats = pstats.Stats(pr)
        stats.sort_stats(pstats.SortKey.TIME)
        stats.dump_stats("profile.prof")

    else:
        main()
