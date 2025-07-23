import ctypes
import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from bar_code_reader.main_window import MainWindow


def get_icon_path() -> str:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # Executável PyInstaller
        return str(Path(sys._MEIPASS) / "files" / "barcode-scan.png")
    # Script normal
    return str(Path(__file__).parent.parent.parent / "files" / "barcode-scan.png")


def main() -> None:
    """Main function to run the application."""
    app = QApplication(sys.argv)
    icon_path = get_icon_path()
    app.setWindowIcon(QIcon(icon_path))
    window = MainWindow()

    if sys.platform.startswith("win"):
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "codebar.version.1.0"
        )

    window.show()
    app.exec()


if __name__ == "__main__":
    main()
