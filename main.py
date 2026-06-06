import os
import sys
import ctypes
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from app.ui.main_window import MainWindow
from app.utils.path_helpers import resource_path

def main():
    # Force application icon for Windows taskbar
    myappid = 'com.thirumal.docforge'
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except AttributeError:
        pass # Not on Windows

    app = QApplication(sys.argv)
    
    icon_path = resource_path("assets/icons/app.ico")
    icon = QIcon(icon_path)
    
    app.setWindowIcon(icon)
    QApplication.instance().setWindowIcon(icon)
    
    window = MainWindow()
    window.setWindowIcon(icon)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
