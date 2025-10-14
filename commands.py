
class Commands:
    LISTEN = 'Слушаю'
    START = 'Старт записи'
    STOP = 'Стоп записи'
    ERROR_FEW_DATA = 'Ошибка: мало данных'
    ERROR_UNKNOWN_ACTION = 'Неизвестная команда'
    NO_GOODS = 'Такого инструмента нет'
    ERROR_ACCESS = 'Ошибка доступа'
    ERROR_OPTIONS = 'Ошибка распознавания свойств'
    ERROR_NOT_FOUND = 'Инструмент не найден'
    ERROR_NOT_PLACE = 'Отсутствует место'
    ERROR_NOT_NAME = 'Отсутствует имя заемщика'
    ERROR_FEW_FOR_RENT = 'Недостаточно инструментов для аредны'
    ERROR_NOT_RENT = 'Нет информации по аренде такого инструмента данным человеком'
    ERROR_DELETE_ACTIVE_TOOL = 'Нельзя удалить: инструмент в аренде'
    ERROR_NOT_NAME_IN_DB = 'Такого заёмщика нет в базе'


class TypesOfAction:
    LISTENING = 'Прослушивание'
    ADDING = 'Добавление'
    REMOVING = 'Удаление'
    SEARCHING = 'Поиск'
    ERROR = 'Ошибка'
    STOPING = 'Остановка'
    RENT = 'Аренда'
    UNRENT = 'Возврат'