import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic

examples = ["""
-Склад\n-Слушаю\n-Добавить съемник место полка 13 количество 2\n-Съемник в место полка 13 количество 2 добавлен в базу            
""", """
-Склад\n-Слушаю\n-Добавить ключ размер 32 место полка 15\n-Ключ размер 32 в место полка 15 добавлен в базу
""", """
-Склад\n-Слушаю\n-Удалить ключ размер 32\n-Ключ размер 32 удален из базы
""", """
-Склад\n-Слушаю\n-Убрать съемник\n-Съемник удален из базы
""", """
-Склад\n-Слушаю\n-Убрать клипса\n-Такого инструмента нет
"""]

class InstructionWindow(QMainWindow):
    def __init__(self, parent=None):
        super(InstructionWindow, self).__init__()
        uic.loadUi('./ui/instruction.ui', self)
        self.setFixedSize(600, 500)
        self.parent = parent

        self.current_example = 0

        self.pushButton_next.clicked.connect(self.next)
        self.pushButton_prev.clicked.connect(self.prev)

    def next(self):
        self.current_example += 1
        if self.current_example >= len(examples):
            self.current_example = 0

        self.update_example()

    def prev(self):
        self.current_example -= 1
        if self.current_example < 0:
            self.current_example = len(examples) - 1

        self.update_example()

    def update_example(self):
        self.label_5.setText(examples[self.current_example])