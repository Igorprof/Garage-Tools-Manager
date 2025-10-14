from PyQt5 import QtCore

from service import Service

from commands import Commands, TypesOfAction

class Controller(QtCore.QObject):
    signal = QtCore.pyqtSignal(list)

    def __init__(self, _settings):   
        super(Controller, self).__init__()
        self.working = False
        self.service = Service()
        self._settings = _settings

    def feed(self, query, tg=False, username=None):
        query = query.lower()
        if tg:
            if username not in self._settings.allowed_users:
                self.signal.emit([TypesOfAction.ERROR, Commands.ERROR_ACCESS])
                return Commands.ERROR_ACCESS
            self.working = True
        if not self.working: 
            if self._settings.start.lower() in query:
                self.signal.emit([TypesOfAction.LISTENING, Commands.LISTEN])  
                self.working = True      
            if self._settings.stop_word.lower() in query: 
                self.signal.emit([TypesOfAction.STOPING, Commands.STOP])
        else:
            try:
                action, *options = query.split(' ')
                if not options:
                    self.signal.emit([TypesOfAction.ERROR, Commands.ERROR_FEW_DATA])
                    return Commands.ERROR_FEW_DATA
            except ValueError:
                self.signal.emit([TypesOfAction.ERROR, Commands.ERROR_FEW_DATA])
                return Commands.ERROR_FEW_DATA

            self.working = False

            print(action, options)
            res = None
            action_type = None
            if action.capitalize() in self._settings.add_words:
                res = self.service.add(options)
                action_type = TypesOfAction.ADDING
            elif action.capitalize() in self._settings.delete_words:                
                res = self.service.delete(options)
                action_type = TypesOfAction.REMOVING
            elif action.capitalize() in self._settings.search_words:
                res = self.service.search(options)
                if tg:
                    return res
                action_type = TypesOfAction.SEARCHING
                if res == Commands.ERROR_OPTIONS or res == Commands.ERROR_NOT_FOUND:
                    action_type = TypesOfAction.ERROR
            elif action.lower() == self._settings.rent_word.lower():
                res = self.service.rent(options)
                action_type = TypesOfAction.RENT
            elif action.lower() == 'возврат':
                res = self.service.unrent(options)
                action_type = TypesOfAction.UNRENT
            elif action.capitalize() == 'Показать':
                res = self.service.get_data()
            else:
                res = Commands.ERROR_UNKNOWN_ACTION
                action_type = TypesOfAction.ERROR

            self.signal.emit([action_type, res])
            return res
    
    def update_settings(self):
        self._settings.update()

    def get_data(self):
        return self.service.get_data()
    
    def get_html(self):
        return self.service.get_html()

    def get_data_for_ui(self, rows):
        return self.service.get_data_for_ui(rows)
    
    def get_data_for_bot(self, rows):
        return self.service.get_data_for_bot(rows)
    
    def get_data_for_ui_rent(self):
        return self.service.get_data_for_ui_rent()
    
    def get_data_for_ui_debtors(self):
        return self.service.get_data_for_ui_debtors()
    
    def add(self, table, data):
        if table == 'debtors':
            name, review = data
            return self.service.add_debtor(name, review)
        if table == 'rent':
            debtor_id, tool_id, quantity = data
            return self.service.rent()
    
    def search(self, good):
        return self.service.search([good])