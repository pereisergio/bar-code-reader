from PySide6.QtWidgets import (QMainWindow, QPushButton, QApplication,
                               QWidget, QVBoxLayout, QLabel)
from PySide6.QtCore import Qt
from PySide6.QtGui import QClipboard
from typing import List
from decode_bar import DecodeBar
from other_window import OtherWindow
from linha_digitavel import LinhaDigitavel


class MainWindow(QMainWindow):
    def __init__(self, parent: QWidget | None = None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        self.cw = QWidget()
        self.vLayout = QVBoxLayout()
        self.cw.setLayout(self.vLayout)
        self.setCentralWidget(self.cw)

        # Título da janela
        self.setWindowTitle('Code Reader')

        self.button1 = self.makeButton('Bar / QR Code')
        self.button1.clicked.connect(self.openWindows)
        self.vLayout.addWidget(
            self.button1, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.label1 = self.makeLabel('Press the button to scan the code.')
        self.vLayout.addWidget(
            self.label1, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.listWindows: List[QMainWindow] = []

    def adjustFixedSize(self) -> None:
        self.adjustSize()
        self.setFixedSize(self.width(), self.height())

    def makeButton(self, text) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedSize(130, 45)
        btn.setStyleSheet('font-size: 14;  padding: 8;')
        return btn

    def makeLabel(self, text) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet('font-size: 14;  padding: 15;')
        label.setTextInteractionFlags(
            label.textInteractionFlags() |
            label.textInteractionFlags().TextSelectableByMouse)
        return label

    def openWindows(self):
        screens = QApplication.screens()
        for screen in screens:
            self.otherWindow = OtherWindow(
                mainWindow=self, screen=screen)
            self.otherWindow.setGeometry(screen.geometry())
            self.otherWindow.closeSignal.connect(self.closeBothWindows)
            self.otherWindow.codeBarSignal.connect(self.readCodeBar)
            self.otherWindow.show()
            self.listWindows.append(self.otherWindow)
        self.hide()

    def closeBothWindows(self):
        # Fecha ambas as janelas
        for _window in self.listWindows:
            _window.close()
            _window = None

    def readCodeBar(self):
        barcodes = DecodeBar('C:/temp/capture/bar_capture.png').decoded_bar()
        if not barcodes:
            self.label1.setText(
                'Nenhum código de barras foi detectado na imagem.')
        else:
            barcode_data = barcodes[0].data.decode('utf-8')
            if len(barcode_data) == 44:
                barcode_data = LinhaDigitavel().calcular_dac(barcode_data)
            clipboard = QApplication.clipboard()
            clipboard.setText(str(barcode_data.replace(' ', '')),
                              mode=QClipboard.Mode.Clipboard)
            self.label1.setText(
                f'Type: {barcodes[0].type} - Code: {barcode_data}')
