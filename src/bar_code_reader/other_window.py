from PySide6.QtCore import QPoint, QRect, QSize, Qt, Signal
from PySide6.QtGui import QColor, QKeyEvent, QPainter, QPen
from PySide6.QtWidgets import QMainWindow, QRubberBand


class OtherWindow(QMainWindow):
    closeSignal = Signal()  # Sinal para fechar ambas as janelas
    codeBarSignal = Signal()

    def __init__(self, mainWindow: QMainWindow, screen, temp_file_path: str):
        super().__init__()
        self.mainWindow = mainWindow
        self._screen = screen
        self.temp_file_path = temp_file_path
        self.setWindowOpacity(0.5)  # Torna a janela semi-transparente
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )

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
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.rubber_band.hide()
            self.close()
            self.capture_area()
            self.mainWindow.show()

    def capture_area(self):
        screenshot = self._screen.grabWindow(
            0,
            self.selection_rect.x(),
            self.selection_rect.y(),
            self.selection_rect.width(),
            self.selection_rect.height(),
        )
        # Salva no caminho temporário recebido da MainWindow
        screenshot.save(self.temp_file_path, "png")
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

            center_y = self.selection_rect.y() + self.selection_rect.height() // 2

            # Linha horizontal
            painter.drawLine(
                self.selection_rect.left(),
                center_y,
                self.selection_rect.right(),
                center_y,
            )

            painter.end()
