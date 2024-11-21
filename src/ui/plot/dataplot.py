if __name__ == "__main__":
    from PySide6.QtCore import Qt

import pyqtgraph as pg
from PySide6.QtWidgets import QFrame, QVBoxLayout
from PySide6.QtCore import Slot
from PySide6.QtGui import QLinearGradient, QBrush
import numpy as np


class DataPlot(QFrame):
    def __init__(self) -> None:
        super().__init__()

        self.__layout = QVBoxLayout()
        self.__layout.setContentsMargins(5, 5, 5, 5)

        self.__graph = pg.GraphicsLayoutWidget()
        self.__graph.viewport().setMouseTracking(True)

        self.__plot = self.__graph.addPlot()
        self.__plot.setRange(xRange=(0, 10), yRange=(1, -1))
        self.__plot.setMenuEnabled(False)
        self.__plot.setMouseEnabled(x=False, y=False)
        self.__plot.hideButtons()
        self.__plot.scene().sigMouseMoved.connect(self.__on_mouse_moved)

        self.__crosshair = pg.InfiniteLine(pos=(0, 0), angle=90, pen=pg.mkPen("red"))
        self.__crosshair.setZValue(1)
        self.__plot.addItem(
            self.__crosshair,
        )

        grad = QLinearGradient(0, 0, 0, 6)
        grad.setColorAt(0.0, pg.mkColor("#000000"))
        grad.setColorAt(0.5, pg.mkColor("orange"))
        brush = QBrush(grad)

        # Testing:
        x = np.linspace(0, 10, 500)
        y = np.cos(x)
        self.__plot.plot(x, y, pen=pg.mkPen("orange"), brush=brush, fillLevel=0)

        self.__layout.addWidget(self.__graph)
        self.setLayout(self.__layout)

    @Slot(tuple)
    def __on_mouse_moved(self, pos):
        mousePoint = self.__plot.vb.mapSceneToView(pos)
        self.__crosshair.setPos(mousePoint)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication()
    dataplot = DataPlot()
    dataplot.show()
    app.exec()
