import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic

from settings import Settings

class SettingsWindow(QMainWindow):
    def __init__(self, parent=None):
        super(SettingsWindow, self).__init__()
        uic.loadUi('./ui/settings.ui', self)
        self.setFixedSize(649, 921)
        self.parent = parent

        self._settings = Settings.from_json()

        self.pushButton_save.clicked.connect(self.saveBtnClicked)
        self.pushButton_add_plus.clicked.connect(self.addPlusBtnClicked)
        self.pushButton_add_minus.clicked.connect(self.addMinusBtnClicked)
        self.pushButton_delete_plus.clicked.connect(self.deletePlusBtnClicked)
        self.pushButton_delete_minus.clicked.connect(self.deleteMinusBtnClicked)
        self.pushButton_search_plus.clicked.connect(self.searchPlusBtnClicked)
        self.pushButton_search_minus.clicked.connect(self.searchMinusBtnClicked)        

        # self.textEdit_start.setPlaceholderText(self._settings.start)
        self.textEdit_start.setText(self._settings.start)
        # self.textEdit_stop.setPlaceholderText(self._settings.stop_word)
        self.textEdit_stop.setText(self._settings.stop_word)
        self.textEdit_rent.setText(self._settings.rent_word)

        for add_command in self._settings.add_words:
            self.listWidget_add.addItem(add_command)

        for delete_command in self._settings.delete_words:
            self.listWidget_delete.addItem(delete_command)

        for search_command in self._settings.search_words:
            self.listWidget_search.addItem(search_command)

        self.doubleSpinBox.setValue(float(self._settings.pause))
        self.comboBox_speed.setCurrentIndex(int(self._settings.speed_index))


    def addPlusBtnClicked(self):
        txt = self.textEdit_add.toPlainText()
        if txt:
            self.listWidget_add.addItem(txt)
            self.textEdit_add.clear()

    def addMinusBtnClicked(self):
        self.listWidget_add.takeItem(self.listWidget_add.currentRow())

    def deletePlusBtnClicked(self):
        txt = self.textEdit_delete.toPlainText()
        if txt:
            self.listWidget_delete.addItem(txt)
            self.textEdit_delete.clear()

    def deleteMinusBtnClicked(self):
        self.listWidget_delete.takeItem(self.listWidget_delete.currentRow())

    def searchPlusBtnClicked(self):
        txt = self.textEdit_search.toPlainText()
        if txt:
            self.listWidget_search.addItem(txt)
            self.textEdit_search.clear()

    def searchMinusBtnClicked(self):
        self.listWidget_search.takeItem(self.listWidget_search.currentRow())
 
    def saveBtnClicked(self):
        start_command = self.textEdit_start.toPlainText()
        stop_command = self.textEdit_stop.toPlainText()

        add_commands = [self.listWidget_add.item(i).text() for i in range(self.listWidget_add.count())]
        delete_commands = [self.listWidget_delete.item(i).text() for i in range(self.listWidget_delete.count())]
        search_commands = [self.listWidget_search.item(i).text() for i in range(self.listWidget_search.count())]

        pause = self.doubleSpinBox.value()
        speed_index = self.comboBox_speed.currentIndex()

        # rent_words = [self.listWidget_rent.item(i).text() for i in range(self.listWidget_rent.count())]
        rent_word = self.textEdit_rent.toPlainText()

        self._settings.start = start_command
        self._settings.stop_word = stop_command
        self._settings.add_words = add_commands
        self._settings.delete_words = delete_commands
        self._settings.search_words = search_commands
        self._settings.pause = pause
        self._settings.speed_index = speed_index
        self._settings.rent_word = rent_word

        if start_command and stop_command:
            self._settings.save()
            self.parent.controller.update_settings()
        
        self.close()

class SettingsTgWindow(QMainWindow):
    def __init__(self, parent=None):
        super(SettingsTgWindow, self).__init__()
        uic.loadUi('./ui/settings_tg.ui', self)
        self.setFixedSize(372, 400)
        self.parent = parent
        # self.ui.setupUi(self)

        self._settings = Settings.from_json()

        self.pushButton_save.clicked.connect(self.saveBtnClicked)
        self.pushButton_plus.clicked.connect(self.plusBtnClicked)
        self.pushButton_minus.clicked.connect(self.minusBtnClicked)

        for user in self._settings.allowed_users:
            self.listWidget_users.addItem(user)
        
    def plusBtnClicked(self):
        user = self.textEdit_user.toPlainText()
        if user:
            self.listWidget_users.addItem(user)
            self.textEdit_user.clear()

    def minusBtnClicked(self):
        self.listWidget_users.takeItem(self.listWidget_users.currentRow())
    
    def saveBtnClicked(self):
        users = [self.listWidget_users.item(i).text() for i in range(self.listWidget_users.count())]

        self._settings.allowed_users = users
        self._settings.save()
        self.parent.controller.update_settings()

        self.close()


if __name__ == '__main__':
    application = QApplication(sys.argv)

    window = SettingsWindow()
    window.show()

    sys.exit(application.exec_()) # запуск основного цикла приложения