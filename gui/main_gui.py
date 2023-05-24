# -*- coding: utf-8 -*-

# Native python
import logging
import os
import sys

# qt
from PySide6.QtWidgets import QApplication

# personal module
import main_window

# debug log output

logging.basicConfig(level=logging.DEBUG,
                    filename='log.txt',
                    filemode='a',
                    format='%(asctime)s - %(levelname)s: %(message)s'
                    )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = main_window.MainWindow()
    sys.exit(app.exec())
