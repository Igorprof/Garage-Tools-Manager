import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QColor
from settings_interface import SettingsWindow, SettingsTgWindow
from instruction_interface import InstructionWindow
from rent_interface import RentWindow
from about_interface import AboutWindow
from settings import Settings
from commands import Commands, TypesOfAction

import speech_recognition as sr
from control import Controller

# import pandas as pd

from bot_thread import BotThread
from gtts_thread import SpeechThread
from data_control_thread import BackupThread, DeleteSoundsThread

from styles import Styles


class RecordThreadHandler(QtCore.QThread):
    signal = QtCore.pyqtSignal(list)
    handler_status = True

    def __init__(self, _settings, *args, **kwargs):
        super(RecordThreadHandler, self).__init__(*args, **kwargs)
        self._settings = _settings

    def run(self):
        self.signal.emit(['start_thread'])
        recognizer = sr.Recognizer()
        recognizer.pause_threshold = self._settings.pause

        with sr.Microphone() as mic:
            # recognizer.adjust_for_ambient_noise(source=mic, duration=0.5)
            while True:
                if self.handler_status:
                    try:
                        audio = recognizer.listen(source=mic)

                        text = recognizer.recognize_google(
                            audio, language='ru-RU')

                        self.signal.emit(['response', text])
                    except sr.exceptions.UnknownValueError:
                        pass
        self.signal.emit(['stop_thread'])


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        uic.loadUi('./ui/micro_interface.ui', self)
        self.setFixedSize(917, 858)

        self.main_start = False
        self.tg_start = False
        self.speech = True

        self._settings = Settings.from_json()

        self.views = {
            'main': self.loadData,
            'rent': self.loadDataRent,
            'debtors': self.loadDebtors
        }
        self.active_view = 'main'

        self.controller = Controller(self._settings)
        self.controller.signal.connect(self.controllerHandler)

        self.thread_record = RecordThreadHandler(self._settings)
        self.thread_record.signal.connect(self.recordHandler)
        # self.thread_record.signal.connect(self.sound.play)

        self.thread_bot = BotThread(self._settings)
        self.thread_bot.signal.connect(self.botHandler)

        self.thread_speech = None

        self.thread_backup = BackupThread()
        self.thread_backup.signal.connect(self.backupHandler)
        self.thread_backup.start()

        self.pushButton_start.clicked.connect(self.startBtnClicked)
        # self.pushButton_start.clicked.connect(self.sound.play)
        self.pushButton_load.clicked.connect(self.loadData)
        self.pushButton_rent.clicked.connect(self.rentClicked)
        self.pushButton_load_debtors.clicked.connect(self.loadDebtors)

        self.actionSettingsGeneral.triggered.connect(self.settingsClicked)
        self.actionSettingsTg.triggered.connect(self.settingsTgClicked)
        # self.actionAbout.triggered.connect(self.aboutClicked)

        self.pushButton_start_tg.clicked.connect(self.startTgBtnClicked)

        self.pushButton_log_clear.clicked.connect(self.logClearBtnClicked)
        self.pushButton_actions_clear.clicked.connect(
            self.actionsClearBtnClicked)

        self.checkBox_speech.stateChanged.connect(self.speechStateChanged)

        self.actionInstruction.triggered.connect(self.instructionClicked)

        self.lineEdit_search.textChanged.connect(self.onSearch)

    def startBtnClicked(self):
        if not self.main_start:
            self.thread_record.start()
            self.pushButton_start.setText('Стоп')
            self.pushButton_start.setStyleSheet(
                f'QPushButton {Styles.btn_stop}')
            self.label_active.setText(Styles.active_text(True, 'Активно'))
            self.main_start = True
        else:
            self.thread_record.terminate()
            self.pushButton_start.setText('Старт')
            self.pushButton_start.setStyleSheet(
                f'QPushButton {Styles.btn_start}')
            self.label_active.setText(Styles.active_text(False, 'Ожидание'))
            self.main_start = False

    def startTgBtnClicked(self):
        if not self.tg_start:
            self.thread_bot.start()
            self.pushButton_start_tg.setText('Стоп бот')
            self.pushButton_start_tg.setStyleSheet(
                f'QPushButton {Styles.btn_tg_stop}')
            self.label_active_bot.setText(Styles.active_text(True))
            self.tg_start = True
        else:
            self.thread_bot.terminate()
            self.pushButton_start_tg.setText('Телеграмм бот')
            self.pushButton_start_tg.setStyleSheet(
                f'QPushButton {Styles.btn_tg_start}')
            self.label_active_bot.setText(Styles.active_text(False))
            self.tg_start = False

    def loadData(self, rows=None):
        # print(self.controller.add(['ключик 2', 'размер', '12', 'количество', '7', 'место', 'гараж 2']))
        self.active_view = 'main'
        info, items = self.controller.get_data_for_ui(rows)

        self.tableWidget.clear()

        self.tableWidget.setRowCount(info[0])
        self.tableWidget.setColumnCount(info[1])
        self.tableWidget.setHorizontalHeaderLabels(info[2])
        # print(info, items)
        for index, index_col, item, rented in items:
            self.tableWidget.setItem(index, index_col, QTableWidgetItem(item))
            item = self.tableWidget.item(index, index_col)
            if rented > 0:
                item.setBackground(QColor(255, 92, 92))
                item.setToolTip(f'В аренде: {rented} ед.')
        self.tableWidget.setColumnWidth(4, 180)
        self.tableWidget.setColumnWidth(5, 150)

    def loadDataRent(self, rows=None):
        info, items = self.controller.get_data_for_ui_rent()
        self.tableWidget.clear()

        self.tableWidget.setRowCount(info[0])
        self.tableWidget.setColumnCount(info[1])
        self.tableWidget.setHorizontalHeaderLabels(info[2])
        # print(info, items)
        for index, index_col, item in items:
            self.tableWidget.setItem(index, index_col, QTableWidgetItem(item))

    def rentClicked(self):
        self.rentWindow = RentWindow(self)
        self.rentWindow.show()

    def loadDebtors(self, rows=None):
        self.active_view = 'debtors'
        info, items = self.controller.get_data_for_ui_debtors()

        self.tableWidget.clear()

        self.tableWidget.setRowCount(info[0])
        self.tableWidget.setColumnCount(info[1])
        self.tableWidget.setHorizontalHeaderLabels(info[2])
        for index, index_col, item in items:
            self.tableWidget.setItem(index, index_col, QTableWidgetItem(item))
        self.tableWidget.setColumnWidth(4, 180)
        self.tableWidget.setColumnWidth(5, 150)

    def recordHandler(self, data):
        if data[0] == 'response':
            self.plainTextEdit.appendPlainText(data[1])
            self.controller.feed(data[1])
        elif data[0] == 'stop_thread':
            self.plainTextEdit.appendPlainText('Остановлено')

    def controllerHandler(self, data):
        type_of_act, result = data
        if type_of_act == TypesOfAction.SEARCHING:
            self.loadData(rows=result)
            print(result)
            self.plainTextEdit_actions.appendPlainText('Выдача результатов')
            self.play('Выдача результатов')
            return

        self.plainTextEdit_actions.appendPlainText(result)
        if type_of_act == TypesOfAction.STOPING:
            self.thread_record.terminate()
            self.pushButton_start.setText('Старт')
            self.pushButton_start.setStyleSheet(
                f'QPushButton {Styles.btn_start}')
            self.label_active.setText(Styles.active_text(False, 'Ожидание'))
            self.main_start = False

        if type_of_act == TypesOfAction.RENT:
            print('Аренда')

        if type_of_act == TypesOfAction.UNRENT:
            print('Возврат')

        self.loadData()
        self.play(result)

    def play(self, text):
        if self.speech:
            self.thread_speech = SpeechThread(text, self._settings)
            self.thread_speech.start()

    def botHandler(self, value):
        message, text = value
        if text == 'show':
            self.thread_bot.send(message.chat.id, self.controller.get_data())
        else:
            try:
                username = message.from_user.username
            except:
                self.plainTextEdit.appendPlainText(
                    'Проблема с username пользователя')
                return
            self.plainTextEdit.appendPlainText(f'{username}: {text}')
            answer = self.controller.feed(text, tg=True, username=username)
            if isinstance(answer, list):
                is_single, data = self.controller.get_data_for_bot(answer)
                if is_single:
                    self.thread_bot.reply(message, data)
                else:
                    with open(data, 'rb') as file_report:  
                        self.thread_bot.send_document(message.chat.id, file_report)                    
                return
            self.thread_bot.reply(message, answer)

    def onSearch(self):
        text = self.lineEdit_search.text()
        if not text:
            self.views[self.active_view]()
            return
        results_rows = self.controller.search(text)
        self.loadData(rows=results_rows)

    def backupHandler(self, msg):
        self.plainTextEdit_actions.appendPlainText(msg)
        # QMessageBox.information(self, 'Backup', msg)

    def settingsClicked(self):
        self.settingsWindow = SettingsWindow(self)
        self.settingsWindow.show()

    def settingsTgClicked(self):
        self.settingsTgWindow = SettingsTgWindow(self)
        self.settingsTgWindow.show()

    def logClearBtnClicked(self):
        self.plainTextEdit.clear()

    def actionsClearBtnClicked(self):
        self.plainTextEdit_actions.clear()

    def speechStateChanged(self, checked):
        self.speech = bool(checked)

    # def aboutClicked(self):
    #     self.about_window = AboutWindow(self)
    #     self.about_window.show()

    def instructionClicked(self):
        self.instruction_window = InstructionWindow(self)
        self.instruction_window.show()


if __name__ == '__main__':
    application = QApplication(sys.argv)

    window = Window()
    window.show()

    sys.exit(application.exec_())
