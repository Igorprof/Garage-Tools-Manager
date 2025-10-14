from PyQt5 import QtCore

import gtts
from playsound import playsound
import uuid
import os


class SpeechThread(QtCore.QThread):
    # signal = QtCore.pyqtSignal(list)

    def __init__(self, text, _settings, *args, **kwargs):
        super(SpeechThread, self).__init__(*args, **kwargs)
        self.text = text
        self._settings = _settings

    def run(self):
        gts = gtts.gTTS(text=self.text, lang='ru', slow=False)
        filename = 'sounds/' + str(uuid.uuid4()) + '.mp3'
        gts.save(filename)

        speed_index = self._settings.speed_index

        if speed_index == 0:
            playsound(filename)
            # os.remove(filename)
        # else:
        #     filename_up = filename[:-4] + '_up.mp3'

        #     song, fs = librosa.load(filename)
        #     song_faster = librosa.effects.time_stretch(song, rate=speed_index*0.5 + 1)

        #     sf.write(filename_up, song_faster, fs)

        #     os.remove(filename)
        #     playsound(filename_up)
            # os.remove(filename_up)
        