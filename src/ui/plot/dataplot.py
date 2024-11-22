# Needed to be imported for other modules to be able to access some dlls
if __name__ == "__main__":
    from PySide6.QtCore import Qt

import pyqtgraph as pg
from PySide6.QtWidgets import QFrame, QVBoxLayout
from PySide6.QtCore import Slot
from PySide6.QtGui import QLinearGradient, QBrush
import numpy as np


class DataPlot(QFrame):
    '''
    Used to make interactive plots from data

    Args:
        
    '''
    def __init__(self) -> None:
        super().__init__()

        self.__layout = QVBoxLayout()
        self.__layout.setContentsMargins(5, 5, 5, 5)

        self.__graph = pg.GraphicsLayoutWidget()
        self.__graph.viewport().setMouseTracking(True)

        self.__plot = self.__graph.addPlot()
        self.__plot.setRange(xRange=(-5, 5), yRange=(2, -2))
        self.__plot.setMenuEnabled(False)
        self.__plot.setMouseEnabled(x=False, y=False)
        self.__plot.hideButtons()
        self.__plot.scene().sigMouseMoved.connect(self.__on_mouse_moved)

        self.__crosshair = pg.InfiniteLine(pos=(0, 0), angle=90, pen=pg.mkPen("red"))
        self.__crosshair.setZValue(1)
        self.__plot.addItem(
            self.__crosshair,
        )

        self.__x_value = pg.TextItem(
            text="",
            color="black",
            anchor=(0.5, 0.5),
            border=pg.mkPen("white"),
            fill=pg.mkBrush("white"),
        )
        self.__x_value.setZValue(2)
        self.__plot.addItem(self.__x_value)

        self.__y_value = pg.TextItem(
            text="",
            color="black",
            anchor=(0.5, 0.5),
            border=pg.mkPen("white"),
            fill=pg.mkBrush("white"),
        )
        self.__y_value.setZValue(2)
        self.__plot.addItem(self.__y_value)

        grad = QLinearGradient(0, 0, 0, 6)
        grad.setColorAt(0.0, pg.mkColor("#000000"))
        grad.setColorAt(0.5, pg.mkColor("orange"))
        brush = QBrush(grad)

        # Testing:
        self.__x_data = np.linspace(start=-5, stop=5, num=1000)
        self.__y_data = np.cos(5 * self.__x_data)
        self.__plot.plot(
            self.__x_data,
            self.__y_data,
            pen=pg.mkPen("orange"),
            brush=brush,
            fillLevel=0,
        )

        self.__layout.addWidget(self.__graph)
        self.setLayout(self.__layout)

    @Slot(tuple)
    def __on_mouse_moved(self, pos):
        mouse_point = self.__plot.vb.mapSceneToView(pos)
        closest_index = np.abs(self.__x_data - mouse_point.x()).argmin()

        x_value = self.__x_data[closest_index]
        y_value = self.__y_data[closest_index]

        self.__x_value.setText(str(x_value))
        self.__y_value.setText(str(y_value))
        self.__crosshair.setPos(x_value)
        self.__x_value.setPos(x_value, -2)
        self.__y_value.setPos(x_value, y_value)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication()
    dataplot = DataPlot()
    dataplot.show()
    app.exec()
