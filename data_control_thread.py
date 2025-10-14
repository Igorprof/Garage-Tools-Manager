from PyQt5 import QtCore
import datetime
import time
import shutil
import os

from settings import DATABASE_FILE

class BackupThread(QtCore.QThread):
    signal = QtCore.pyqtSignal(str)

    def __init__(self, secs=10800, *args, **kwargs):
        super(BackupThread, self).__init__(*args, **kwargs)
        self.secs = secs
        self.backup_folder_create()
    
    def backup_folder_create(self):
        try:
            os.mkdir('backups')
        except:
            pass

    def run(self):
        while True:
            time.sleep(self.secs)
            date_str = datetime.datetime.now().strftime("%d.%m.%Y %H.%M")
            shutil.copy(DATABASE_FILE, f'./backups/backup_data_{date_str}.xlsx')
            self.signal.emit(f'Произведен backup от {date_str}')


class DeleteSoundsThread(QtCore.QThread):
    def run(self):
        for file in os.listdir('./sounds'):
            os.remove('./sounds/' + file)
