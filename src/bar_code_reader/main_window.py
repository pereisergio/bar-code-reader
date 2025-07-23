import os
import tempfile
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QClipboard
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from bar_code_reader.decode_bar import CollectionGuide, DecodeBar, TransferGuide
from bar_code_reader.other_window import OtherWindow


class MainWindow(QMainWindow):
    def __init__(self, parent: QWidget | None = None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        self.cw = QWidget()
        self.vLayout = QVBoxLayout()
        self.cw.setLayout(self.vLayout)
        self.setCentralWidget(self.cw)

        # Título da janela
        self.setWindowTitle("Code Reader")

        self.button1 = self.makeButton("Bar / QR Code")
        self.button1.clicked.connect(self.openWindows)
        self.vLayout.addWidget(self.button1, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.label1 = self.makeLabel("Press the button to scan the code.")
        self.vLayout.addWidget(self.label1, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.listWindows: list[QMainWindow] = []
        self.temp_file_path = None

    def adjustFixedSize(self) -> None:
        self.adjustSize()
        self.setFixedSize(self.width(), self.height())

    def makeButton(self, text) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedSize(130, 45)
        btn.setStyleSheet("font-size: 14;  padding: 8;")
        return btn

    def makeLabel(self, text) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet("font-size: 14;  padding: 15;")
        label.setTextInteractionFlags(
            label.textInteractionFlags()
            | label.textInteractionFlags().TextSelectableByMouse
        )
        return label

    def openWindows(self):
        # Cria arquivo temporário na raiz do projeto
        temp_dir = Path(__file__).parent.parent.parent
        temp_file = tempfile.NamedTemporaryFile(
            dir=temp_dir, suffix=".png", delete=True
        )
        self.temp_file_path = temp_file.name
        temp_file.close()

        screens = QApplication.screens()
        for screen in screens:
            self.otherWindow = OtherWindow(
                mainWindow=self, screen=screen, temp_file_path=self.temp_file_path
            )
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
        # Usa o arquivo temporário gerado
        barcodes = DecodeBar(self.temp_file_path).decoded_bar()
        if not barcodes:
            self.label1.setText("Nenhum código de barras foi detectado na imagem.")
        else:
            code = self.codeCovert(barcodes[0].data.decode("utf-8"))
            self.showLabel(code)
        # Exclui o arquivo temporário após leitura
        try:
            os.remove(self.temp_file_path)
        except Exception as e:
            print(f"Erro ao remover arquivo temporário: {e}")

    def codeCovert(self, code: str) -> object | str:
        if code[0] == "8" and len(code) == 44:
            return CollectionGuide(code)
        if code[0] != "8" and len(code) == 44:
            return TransferGuide(code)
        return code

    def showLabel(self, codeConverted):
        clipboard = QApplication.clipboard()
        clipboard.setText(str(codeConverted), mode=QClipboard.Mode.Clipboard)
        self.label1.setText(f"Code: {codeConverted!r}")
