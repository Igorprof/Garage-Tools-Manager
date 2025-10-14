import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PyQt5 import uic, QtCore
from settings_interface import SettingsWindow, SettingsTgWindow
from settings import Settings
from commands import Commands

import speech_recognition as sr
from control import Controller

# import pandas as pd

from bot_thread import BotThread
from gtts_thread import SpeechThread

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
            recognizer.adjust_for_ambient_noise(source=mic, duration=0.5)
            while True:           
                if self.handler_status:         
                    try:
                        audio = recognizer.listen(source=mic)

                        text = recognizer.recognize_google(audio, language='ru-RU')

                        self.signal.emit(['response', text])
                    except sr.exceptions.UnknownValueError:
                        pass
        self.signal.emit(['stop_thread'])


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        uic.loadUi('./ui/micro_interface.ui', self)
        self.setFixedSize(671, 858)

        self.main_start = False
        self.tg_start = False

        self._settings = Settings.from_json()

        self.controller = Controller(self._settings)
        self.controller.signal.connect(self.controllerHandler)        

        self.thread_record = RecordThreadHandler(self._settings)
        self.thread_record.signal.connect(self.recordHandler)
        # self.thread_record.signal.connect(self.sound.play)       

        self.thread_bot = BotThread(self._settings) 
        self.thread_bot.signal.connect(self.botHandler)

        self.thread_speech = None         

        self.pushButton_start.clicked.connect(self.startBtnClicked)
        # self.pushButton_start.clicked.connect(self.sound.play)
        self.pushButton_load.clicked.connect(self.loadBtnClicked)

        self.actionSettingsGeneral.triggered.connect(self.settingsClicked)
        self.actionSettingsTg.triggered.connect(self.settingsTgClicked)

        self.pushButton_start_tg.clicked.connect(self.startTgBtnClicked)

        self.pushButton_log_clear.clicked.connect(self.logClearBtnClicked)
        self.pushButton_actions_clear.clicked.connect(self.actionsClearBtnClicked)
 
    def startBtnClicked(self):      
        if not self.main_start:  
            self.thread_record.start()
            self.pushButton_start.setText('Стоп')
            self.pushButton_start.setStyleSheet('QPushButton {background-color: #A3C1DA; border:  none}')
            self.main_start = True
        else:
            self.thread_record.terminate()
            self.pushButton_start.setText('Старт')
            self.pushButton_start.setStyleSheet('QPushButton {background-color: #FFFFFF; border:  none}')
            self.main_start = False

    def startTgBtnClicked(self):
        if not self.tg_start:
            self.thread_bot.start()
            self.pushButton_start_tg.setText('Стоп бот')
            self.pushButton_start_tg.setStyleSheet('QPushButton {background-color: #008000; border:  none}')
            self.tg_start = True
        else:
            self.thread_bot.terminate()
            self.pushButton_start_tg.setText('Телеграмм бот')
            self.pushButton_start_tg.setStyleSheet('QPushButton {background-color: #FFFFFF; border:  none}')
            self.tg_start = False
    
    def loadBtnClicked(self):
        info, items = self.controller.get_data_for_ui()

        self.tableWidget.setRowCount(info[0])
        self.tableWidget.setColumnCount(info[1])
        self.tableWidget.setHorizontalHeaderLabels(info[2])

        for index, index_col, item in items:
                self.tableWidget.setItem(index, index_col, QTableWidgetItem(item))

        
    def recordHandler(self, value):
        if value[0] == 'response':
            self.plainTextEdit.appendPlainText(value[1])
            self.controller.feed(value[1])

            # self.thread_speech = SpeechThread(value[1])
            # self.thread_speech.start()
        elif value[0] == 'stop_thread':
            self.plainTextEdit.appendPlainText('Остановлено')

    def controllerHandler(self, value):
        self.plainTextEdit_actions.appendPlainText(value)
        if value == Commands.STOP:
            self.thread_record.terminate()
            self.pushButton_start.setText('Старт')
            self.pushButton_start.setStyleSheet('QPushButton {background-color: #FFFFFF; border:  none}')
            self.main_start = False
        self.loadBtnClicked()
        self.thread_speech = SpeechThread(value)
        self.thread_speech.start()

    def botHandler(self, value):
        message, text = value
        if text == 'show':
            self.thread_bot.send(message.chat.id, self.controller.get_data())
        else:            
            username = message.from_user.username
            self.plainTextEdit.appendPlainText(f'{username}: {text}')
            answer = self.controller.feed(text, tg=True, username=username)
            self.thread_bot.reply(message, answer)

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

if __name__ == '__main__':
    application = QApplication(sys.argv)

    window = Window()
    window.show()

    sys.exit(application.exec_()) 

