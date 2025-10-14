import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem
from PyQt5 import uic


class RentWindow(QMainWindow):
    def __init__(self, parent=None):
        super(RentWindow, self).__init__()
        uic.loadUi('./ui/rent_interface.ui', self)
        self.setFixedSize(928, 770)
        self.parent = parent

        self.pushButton_add_debtor.setEnabled(False)
        self.lineEdit_name.textChanged.connect(self.onChangeName)
        self.pushButton_add_debtor.clicked.connect(self.onAddDebtor)
        self.pushButton_rent.clicked.connect(self.onRent)

        self.loadDebtors()
        self.loadRent()

    def onChangeName(self):
        name = self.lineEdit_name.text()
        if not name:
            self.pushButton_add_debtor.setEnabled(False)
        else:
            self.pushButton_add_debtor.setEnabled(True)

    def onAddDebtor(self):
        name = self.lineEdit_name.text()
        review = self.spinBox_review.value()
        if self.parent.controller.add('debtors', [name, review]):
            QMessageBox.information(
                self, 'Добавление', f'Заёмщик {name} добавлен в базу')
            self.loadDebtors()
        else:
            QMessageBox.warning(
                self, 'Ошибка добавления', 'Такой заёмщик уже есть в базе!')
            
    def onRent(self):
        self.parent.controller.add('rent', [1, 1, 3])

    def loadDebtors(self):
        info, items = self.parent.controller.get_data_for_ui_debtors()

        self.tableWidget_debtors.clear()

        self.tableWidget_debtors.setRowCount(info[0])
        self.tableWidget_debtors.setColumnCount(info[1])
        self.tableWidget_debtors.setHorizontalHeaderLabels(info[2])
        for index, index_col, item in items:
            self.tableWidget_debtors.setItem(index, index_col, QTableWidgetItem(item))
        self.tableWidget_debtors.setColumnWidth(4, 180)
        self.tableWidget_debtors.setColumnWidth(5, 150)

    def loadRent(self):
        info, items = self.parent.controller.get_data_for_ui_rent()

        self.tableWidget_rent.clear()

        self.tableWidget_rent.setRowCount(info[0])
        self.tableWidget_rent.setColumnCount(info[1])
        self.tableWidget_rent.setHorizontalHeaderLabels(info[2])
        for index, index_col, item in items:
            self.tableWidget_rent.setItem(index, index_col, QTableWidgetItem(item))
        self.tableWidget_rent.setColumnWidth(4, 180)
        self.tableWidget_rent.setColumnWidth(5, 150)
