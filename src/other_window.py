from os import makedirs
from PySide6.QtWidgets import QMainWindow, QRubberBand
from PySide6.QtCore import Qt, QRect, QSize, QPoint, Signal
from PySide6.QtGui import QKeyEvent, QPainter, QPen, QColor


class OtherWindow(QMainWindow):
    closeSignal = Signal()  # Sinal para fechar ambas as janelas
    codeBarSignal = Signal()

    def __init__(self, mainWindow: QMainWindow, screen):
        super().__init__()
        self.mainWindow = mainWindow
        self._screen = screen
        self.setWindowOpacity(0.4)  # Torna a janela semi-transparente
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint |
                            Qt.WindowType.WindowStaysOnTopHint)

        self.rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self)
        self.origin = QPoint()
        self.selection_rect = QRect()

    def closeEvent(self, event):
        self.closeSignal.emit()  # Emite o sinal quando a janela é fechada
        super().closeEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.origin = event.pos()
            self.rubber_band.setGeometry(QRect(self.origin, QSize()))
            self.rubber_band.show()

    def mouseMoveEvent(self, event):
        if not self.origin.isNull():
            # Atualiza o retângulo de seleção com as novas coordenadas
            self.selection_rect = QRect(self.origin, event.pos()).normalized()
            self.rubber_band.setGeometry(self.selection_rect)
            self.update()  # Solicita a atualização da janela para redesenho

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.rubber_band.hide()
            self.close()
            self.capture_area()
            self.mainWindow.show()

    def capture_area(self):
        screenshot = self._screen.grabWindow(0,
                                             self.selection_rect.x(),
                                             self.selection_rect.y(),
                                             self.selection_rect.width(),
                                             self.selection_rect.height()
                                             )
        # screenshot.save("captura_area.png", "png")
        makedirs('C:/temp/capture', exist_ok=True)
        path_file = 'C:/temp/capture/bar_capture.png'
        screenshot.save(path_file, "png")
        self.codeBarSignal.emit()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.mainWindow.show()
            self.close()  # Fecha a janela ao pressionar Esc
        else:
            super().keyPressEvent(event)

    def paintEvent(self, event):
        """Desenha uma linha vermelha no centro do RubberBand."""
        if not self.selection_rect.isNull():
            painter = QPainter(self)
            pen = QPen(QColor("red"))
            pen.setWidth(3)
            painter.setPen(pen)

            center_y = (
                self.selection_rect.y() + self.selection_rect.height() // 2)

            # Linha horizontal
            painter.drawLine(
                self.selection_rect.left(), center_y,
                self.selection_rect.right(), center_y
            )

            painter.end()
