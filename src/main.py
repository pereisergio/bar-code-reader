import sys
from PySide6.QtWidgets import (QApplication)
from main_window import MainWindow
from PySide6.QtGui import QIcon
from constants import WINDOW_ICON_PATH
import ctypes  # Necessário para ajustar o ícone da barra de tarefas no Windows


if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = MainWindow()

    # Definir o ícone do aplicativo (afeta toda a aplicação)
    app.setWindowIcon(QIcon(str(WINDOW_ICON_PATH)))

    if sys.platform.startswith("win"):
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "capgemini.codebar.version.1.0")

    window.show()
    app.exec()
