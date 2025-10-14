from PyQt5 import QtCore

import telebot
from telebot import types
import uuid
import os
import soundfile as sf
import speech_recognition as sr

from config import TOKEN

bot = telebot.TeleBot(TOKEN)

class BotThread(QtCore.QThread):
    signal = QtCore.pyqtSignal(list)

    def __init__(self, _settings, *args, **kwargs):
        super(BotThread, self).__init__(*args, **kwargs)
        self._settings = _settings

    def run(self):
        @bot.message_handler(commands=['start'])
        def handle_start(message):
            bot.send_message(message.chat.id, 'Бот готов к работе')
            self.signal.emit([message, 'подключился'])

        @bot.message_handler(func=lambda message: True)
        def handle_message(message):
            # bot.send_message(message.chat.id, message.text + '!')
            # self.signal.emit([message.from_user.username, message.text + '!'])

            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton('Посмотреть базу', callback_data='show')
            markup.add(button1)
            bot.send_message(message.chat.id, 'Меню', reply_markup=markup)
        
        @bot.callback_query_handler(func=lambda callback: True)
        def callback_handler(callback):
            self.signal.emit([callback.message, callback.data])

        @bot.message_handler(content_types=['voice'])
        def audio_handler(message):
            filename = str(uuid.uuid4())
            file_name_full = filename + ".ogg"
            file_name_full_converted = filename + ".wav"
            file_info = bot.get_file(message.voice.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with open(file_name_full, 'wb') as new_file:
                new_file.write(downloaded_file)

            data, samplerate = sf.read(file_name_full)
            sf.write(file_name_full_converted, data, samplerate)            

            text = self.recognise(file_name_full_converted)

            os.remove(file_name_full)
            os.remove(file_name_full_converted)

            self.signal.emit([message, text])
            # bot.reply_to(message, text)
           

        bot.polling(none_stop=True)
    
    def reply(self, message, text):
        bot.reply_to(message, text)
    
    def send(self, chat_id, text):
        bot.send_message(chat_id, text)

    def send_document(self, chat_id, document_file):
        bot.send_document(chat_id, document_file)

    def send_photo(self, chat_id, photo_path):
        with open(photo_path, 'rb') as photo:
            bot.send_photo(chat_id, photo)

    def recognise(self, filename):
        r = sr.Recognizer()
        r.pause_threshold = self._settings.pause
        with sr.AudioFile(filename) as source:
            audio_text = r.record(source)
            try:
                text = r.recognize_google(audio_text, language="ru-RU")
                return text
            except:
                print('Sorry.. run again...')
                return "Sorry.. run again..."