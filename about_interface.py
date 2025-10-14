from PyQt5.QtWidgets import QWidget
from PyQt5 import QtCore
from PyQt5 import uic

import random
import time

variants = ['Про', 'Я', 'Профи']

class GenerThread(QtCore.QThread):
    signal = QtCore.pyqtSignal(str)

    def run(self):
        for _ in range(100):
            self.signal.emit(random.choice(variants))
            time.sleep(0.01)



class AboutWindow(QWidget):
    def __init__(self, parent=None):
        super(AboutWindow, self).__init__()
        uic.loadUi('./ui/about.ui', self)
        self.parent = parent
        self.gener_thread = GenerThread()
        self.gener_thread.signal.connect(self.proClicked)

        self.pushButton.clicked.connect(self.start)

    def start(self):
        self.gener_thread.start()

    def proClicked(self, value):
        self.label.setText(value)
        