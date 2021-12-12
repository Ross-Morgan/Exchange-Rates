from __future__ import annotations

import sys
from contextlib import suppress
from datetime import datetime as dt
from json.decoder import JSONDecodeError
from typing import Optional, Union

from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg, QtOpenGL

from currency import convert as _convert
from currency import floatify, get_codes, get_default_currency
from graph import generate_graph


def qss_sheet(name) -> str:
    return open(f"Assets/Scripts/{name}.qss").read()


class SvgView(QtWidgets.QGraphicsView):
    Native, OpenGL, Image = range(3)

    def __init__(self, parent=None):
        super(SvgView, self).__init__(parent)

        self.renderer = SvgView.Native
        self.svgItem = None
        self.backgroundItem = None
        self.outlineItem = None
        self.image = QtGui.QImage()

        self.setScene(QtWidgets.QGraphicsScene(self))
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)

        # Prepare background check-board pattern.
        tilePixmap = QtGui.QPixmap(64, 64)
        tilePixmap.fill(QtCore.Qt.white)
        tilePainter = QtGui.QPainter(tilePixmap)
        color = QtGui.QColor(220, 220, 220)
        tilePainter.fillRect(0, 0, 32, 32, color)
        tilePainter.fillRect(32, 32, 32, 32, color)
        tilePainter.end()

        self.setBackgroundBrush(QtGui.QBrush(tilePixmap))

    def drawBackground(self, p, rect):
        p.save()
        p.resetTransform()
        p.drawTiledPixmap(self.viewport().rect(),
                          self.backgroundBrush().texture())
        p.restore()

    def openFile(self, svg_file):
        if not svg_file.exists():
            return

        s = self.scene()

        if self.backgroundItem:
            drawBackground = self.backgroundItem.isVisible()
        else:
            drawBackground = False

        if self.outlineItem:
            drawOutline = self.outlineItem.isVisible()
        else:
            drawOutline = True

        s.clear()
        self.resetTransform()

        self.svgItem = QtSvg.QGraphicsSvgItem(svg_file.fileName())
        self.svgItem.setFlags(QtWidgets.QGraphicsItem.ItemClipsToShape)
        self.svgItem.setCacheMode(QtWidgets.QGraphicsItem.NoCache)
        self.svgItem.setZValue(0)

        self.backgroundItem = QtWidgets.QGraphicsRectItem(self.svgItem.
                                                          boundingRect())
        self.backgroundItem.setBrush(QtCore.Qt.white)
        self.backgroundItem.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        self.backgroundItem.setVisible(drawBackground)
        self.backgroundItem.setZValue(-1)

        self.outlineItem = QtWidgets.QGraphicsRectItem(self.svgItem.
                                                       boundingRect())
        outline = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.DashLine)
        outline.setCosmetic(True)
        self.outlineItem.setPen(outline)
        self.outlineItem.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
        self.outlineItem.setVisible(drawOutline)
        self.outlineItem.setZValue(1)

        s.addItem(self.backgroundItem)
        s.addItem(self.svgItem)
        s.addItem(self.outlineItem)

        s.setSceneRect(self.outlineItem.boundingRect()
                       .adjusted(-10, -10, 10, 10))

    def setRenderer(self, renderer):
        self.renderer = renderer

        if self.renderer == SvgView.OpenGL:
            if QtOpenGL.QGLFormat.hasOpenGL():
                self.setViewport(QtOpenGL.QGLWidget(
                                  QtOpenGL.QGLFormat(
                                   QtOpenGL.QGL.SampleBuffers)))
        else:
            self.setViewport(QtWidgets.QWidget())

    def setHighQualityAntialiasing(self, highQualityAntialiasing):
        if QtOpenGL.QGLFormat.hasOpenGL():
            self.setRenderHint(QtGui.QPainter.HighQualityAntialiasing,
                               highQualityAntialiasing)

    def setViewBackground(self, enable):
        if self.backgroundItem:
            self.backgroundItem.setVisible(enable)

    def setViewOutline(self, enable):
        if self.outlineItem:
            self.outlineItem.setVisible(enable)

    def paintEvent(self, event):
        if self.renderer == SvgView.Image:
            if self.image.size() != self.viewport().size():
                self.image = QtGui.QImage(self.viewport().size(),
                                          QtGui.QImage.
                                          Format_ARGB32_Premultiplied)

            imagePainter = QtGui.QPainter(self.image)
            QtWidgets.QGraphicsView.render(self, imagePainter)
            imagePainter.end()

            p = QtGui.QPainter(self.viewport())
            p.drawImage(0, 0, self.image)
        else:
            super(SvgView, self).paintEvent(event)

    def wheelEvent(self, event):
        factor = pow(1.2, event.delta() / 240.0)
        self.scale(factor, factor)
        event.accept()


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

        self.graph_window = self.subwindow((1500, int(1500 // 2.34655532)),
                                           "Currency Graph",
                                           QtGui.QIcon(self.icon))

        self.ui["background"] = QtWidgets.QLabel(self)
        self.ui["background"].setGeometry(0, 0, self.width(), self.height())
        self.ui["background"].setStyleSheet(qss_sheet("background"))

        self.ui["logo"] = QtWidgets.QLabel(self)
        self.ui["logo"].setGeometry(self.width() - 164, 41, 128, 128)
        self.ui["logo"].setPixmap(QtGui.QPixmap(self.icon).scaled(128, 128))

        self.ui["fields"] = {}

        self.ui["fields"]["code1"] = QtWidgets.QComboBox(self)
        self.ui["fields"]["code1"].setGeometry(20, 20, 200, 75)
        self.ui["fields"]["code1"].setInsertPolicy(_insert_policy)
        self.ui["fields"]["code1"].setStyleSheet(qss_sheet("combo_box"))
        self.ui["fields"]["code1"].setFont(QtGui.QFont("helvetica", 20))

        self.ui["fields"]["code2"] = QtWidgets.QComboBox(self)
        self.ui["fields"]["code2"].setGeometry(240, 20, 200, 75)
        self.ui["fields"]["code2"].setInsertPolicy(_insert_policy)
        self.ui["fields"]["code2"].setStyleSheet(qss_sheet("combo_box"))
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

        QDate = QtCore.QDate
        _today = dt.today()
        _today = _today.year, _today.month, _today.day

        self.ui["fields"]["date"] = QtWidgets.QDateEdit(self)
        self.ui["fields"]["date"].setGeometry(20, 210, 200, 50)
        self.ui["fields"]["date"].setMinimumDate(QDate(2000, 1, 1))
        self.ui["fields"]["date"].setMaximumDate(QDate(*_today))
        self.ui["fields"]["date"].setDate(QDate(*_today))
        self.ui["fields"]["date"].setFont(QtGui.QFont("helvetica", 20))

        self.ui["buttons"] = {}
        self.ui["buttons"]["convert"] = QtWidgets.QPushButton("CONVERT", self)
        self.ui["buttons"]["convert"].setGeometry(20, 280, 200, 50)
        self.ui["buttons"]["convert"].setStyleSheet(qss_sheet("button"))
        self.ui["buttons"]["convert"].clicked.connect(self.convert)

        self.ui["buttons"]["generate"] = QtWidgets.QPushButton("GRAPH", self)
        self.ui["buttons"]["generate"].setGeometry(20, 350, 200, 50)
        self.ui["buttons"]["generate"].setStyleSheet(qss_sheet("button"))
        self.ui["buttons"]["generate"].clicked.connect(self.generate_graph)

        self.ui["pixmap"] = QtGui.QPixmap("graph.svg")
        self.ui["graph"] = QtWidgets.QLabel(self)
        self.ui["graph"].setGeometry(240, 210, 380, 190)
        self.ui["graph"].setPixmap(self.ui["pixmap"].scaled(380, 190))

        self.ui["buttons"]["show_graph"] = QtWidgets.QPushButton(self)
        self.ui["buttons"]["show_graph"].setGeometry(240, 210, 380, 190)
        self.ui["buttons"]["show_graph"].setStyleSheet(qss_sheet("show_graph"))
        self.ui["buttons"]["show_graph"].clicked.connect(self.show_graph)

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

        print(code1, code2)

        generate_graph(code1, code2)

        self.ui["pixmap"] = QtGui.QPixmap("graph.svg")
        self.ui["graph"].setPixmap(self.ui["pixmap"].scaled(380, 190))


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
    main()
