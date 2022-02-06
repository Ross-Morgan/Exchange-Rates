from __future__ import annotations

import sys
from contextlib import suppress
from datetime import datetime as dt
from json.decoder import JSONDecodeError
from typing import Optional, Union

from PyQt6 import QtCore, QtGui, QtSvgWidgets, QtWidgets

from assets import Assets
from currency import convert as _convert
from currency import floatify, get_codes, get_default_currency
from graph import save_history_svg


class WindowWrapper(QtWidgets.QMainWindow):
    """It works? Adds exit prompt functionality"""
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.buttons = QtWidgets.QMessageBox.StandardButton

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        yes, no = self.buttons.Yes, self.buttons.No
        title = "Exit Prompt"
        message = "Are you sure you want to exit?"
        reply = QtWidgets.QMessageBox.question(self, title, message, yes | no)

        if reply == self.buttons.Yes:
            a0.accept()
        else:
            a0.ignore()


class MainWindow(WindowWrapper):
    ui_types = dict[str, dict[str, Union[
        QtWidgets.QComboBox, QtWidgets.QLabel,
        QtWidgets.QPushButton, QtWidgets.QLineEdit,
        QtWidgets.QDateTimeEdit
    ]]]

    """Main Window for application."""
    def __init__(self: MainWindow, size: tuple[int, int], title: str,
                 icon: QtGui.QIcon,
                 parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)

        self.ui: MainWindow.ui_types = {}
        self.shortcuts: dict[str, QtGui.QShortcut] = {}
        self.icon = Assets.Images.money

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
        self.ui["background"].setStyleSheet(open(Assets.Scripts.background).read())

        self.ui["logo"] = QtWidgets.QLabel(self)
        self.ui["logo"].setGeometry(self.width() - 164, 41, 128, 128)
        self.ui["logo"].setPixmap(QtGui.QPixmap(self.icon).scaled(128, 128))

        self.ui["fields"] = {}

        self.ui["fields"]["code1"] = QtWidgets.QComboBox(self)
        self.ui["fields"]["code1"].setGeometry(20, 20, 200, 75)
        self.ui["fields"]["code1"].setInsertPolicy(_insert_policy)
        self.ui["fields"]["code1"].setStyleSheet(open(Assets.Scripts.combo_box).read())
        self.ui["fields"]["code1"].setFont(QtGui.QFont("helvetica", 20))

        self.ui["fields"]["code2"] = QtWidgets.QComboBox(self)
        self.ui["fields"]["code2"].setGeometry(240, 20, 200, 75)
        self.ui["fields"]["code2"].setInsertPolicy(_insert_policy)
        self.ui["fields"]["code2"].setStyleSheet(open(Assets.Scripts.combo_box).read())
        self.ui["fields"]["code2"].setFont(QtGui.QFont("helvetica", 20, 1))

        for i, field in enumerate([
                self.ui["fields"]["code1"],
                self.ui["fields"]["code2"]]):  # * Speedy thanks to caching :D
            field.addItems(sorted(self.curr_codes))
            field.setCurrentIndex(field.findText(_default_currs[i]))

        self.ui["fields"]["input"] = QtWidgets.QLineEdit(self)
        self.ui["fields"]["input"].setGeometry(20, 115, 200, 75)
        self.ui["fields"]["input"].setPlaceholderText("Amount: ")
        self.ui["fields"]["input"].setFont(QtGui.QFont("helvetica", 10))

        self.ui["fields"]["output"] = QtWidgets.QLineEdit(self)
        self.ui["fields"]["output"].setGeometry(240, 115, 200, 75)
        self.ui["fields"]["output"].setPlaceholderText("Result: ")
        self.ui["fields"]["output"].setFont(QtGui.QFont("helvetica", 10))
        self.ui["fields"]["output"].setReadOnly(True)

        qdate = QtCore.QDate

        _today = dt.today()
        _today = _today.year, _today.month, _today.day

        self.ui["fields"]["date"] = QtWidgets.QDateEdit(self)
        self.ui["fields"]["date"].setGeometry(20, 210, 200, 50)
        self.ui["fields"]["date"].setMinimumDate(qdate(2000, 1, 1))
        self.ui["fields"]["date"].setMaximumDate(qdate(*_today))
        self.ui["fields"]["date"].setDate(qdate(*_today))
        self.ui["fields"]["date"].setFont(QtGui.QFont("helvetica", 20))

        self.ui["buttons"] = {}
        self.ui["buttons"]["convert"] = QtWidgets.QPushButton("CONVERT", self)
        self.ui["buttons"]["convert"].setGeometry(20, 280, 200, 50)
        self.ui["buttons"]["convert"].setStyleSheet(open(Assets.Scripts.button).read())
        self.ui["buttons"]["convert"].clicked.connect(self.convert)

        self.ui["buttons"]["generate"] = QtWidgets.QPushButton("GRAPH", self)
        self.ui["buttons"]["generate"].setGeometry(20, 350, 200, 50)
        self.ui["buttons"]["generate"].setStyleSheet(open(Assets.Scripts.button).read())
        self.ui["buttons"]["generate"].clicked.connect(self.generate_graph)

        self.ui["graph"] = QtSvgWidgets.QSvgWidget(self)
        self.ui["graph"].setGeometry(240, 210, 380, 190)

        self.ui["buttons"]["show_graph"] = QtWidgets.QPushButton(self)
        self.ui["buttons"]["show_graph"].setGeometry(240, 210, 380, 190)
        self.ui["buttons"]["show_graph"].setStyleSheet(open(Assets.Scripts.show_graph).read())
        self.ui["buttons"]["show_graph"].clicked.connect(self.generate_graph)

    def setup_shortcuts(self) -> None:
        def shortcut(key_sequence: str):
            return QtGui.QShortcut(QtGui.QKeySequence(key_sequence), self)

        self.shortcuts["exit"] = shortcut("ctrl+w")
        self.shortcuts["exit"].activated.connect(self.close)

        self.shortcuts["get_rate"] = shortcut("enter")
        self.shortcuts["get_rate"].activated.connect(self.convert)

    def convert(self):
        code1 = self.ui["fields"]["code1"].currentText()
        code2 = self.ui["fields"]["code2"].currentText()

        val = floatify(self.ui["fields"]["input"].text())

        date = self.ui["fields"]["date"].date().toPyDate()

        rate = 1.17

        with suppress(JSONDecodeError):
            rate = _convert(code1, code2, val, date)

        self.ui["fields"]["output"].setText(str(rate))

    def generate_graph(self):
        code1 = self.ui["fields"]["code1"].currentText()
        code2 = self.ui["fields"]["code2"].currentText()

        save_history_svg(code1, code2)

        self.ui["graph"].setWindowFilePath(Assets.Temp.graph)


def main():
    app = QtWidgets.QApplication(sys.argv)

    width, height = 640, 480
    title = "Window Title"
    icon = QtGui.QIcon(Assets.Images.exchange)

    window = MainWindow((width, height), title, icon)
    window.show()

    print(f"Exit Code: {app.exec()}")


if __name__ == "__main__":
    main()
