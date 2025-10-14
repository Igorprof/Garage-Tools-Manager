import pandas as pd
import sqlite3
import datetime
import uuid

from commands import Commands

class Service:
    nums = ['ноль', 'один', 'два', 'три', 'четыре',
            'пять', 'шесть', 'семь', 'восемь', 'девять']

    def __init__(self, db_path='garage.db'):
        self.db_path = db_path
        # self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Создаем таблицы
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tools (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    size TEXT,
                    location TEXT,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS debtors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    review INTEGER CHECK(review BETWEEN 1 AND 5)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rent (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    debtor_id INTEGER NOT NULL,
                    tool_id INTEGER NOT NULL,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    is_done BOOLEAN DEFAULT 0,
                    quantity INTEGER DEFAULT 1,
                    FOREIGN KEY (debtor_id) REFERENCES debtors(id) ON DELETE CASCADE,
                    FOREIGN KEY (tool_id) REFERENCES tools(id) ON DELETE CASCADE
                )
            ''')
            # Создаем индексы
            cursor.execute(
                'CREATE INDEX IF NOT EXISTS idx_tools_name ON tools(name)')
            cursor.execute(
                'CREATE INDEX IF NOT EXISTS idx_rent_dates ON rent(start_time, end_time)')
            cursor.execute(
                'CREATE INDEX IF NOT EXISTS idx_debtors_name ON debtors(name)')
            conn.commit()

    def now(self):
        return datetime.datetime.now()

    def _execute_query(self, query, params=(), fetch=False, commit=False):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            if commit:
                conn.commit()
            if fetch:
                return cursor.fetchall()
            return cursor.lastrowid

    def add(self, options):
        good, size, quantity, location, _ = self._get_info(options)
        if not good:
            return Commands.ERROR_OPTIONS

        # Проверяем существование инструмента
        existing = self._execute_query(
            "SELECT id, quantity, location FROM tools WHERE name=? AND size=?",
            (good, str(size)), fetch=True
        )

        if not existing:
            # Добавляем новый инструмент
            self._execute_query(
                "INSERT INTO tools (name, size, quantity, location, last_used, notes) VALUES (?, ?, ?, ?, ?, ?)",
                (good, str(size), quantity, location,
                 self.now(), f"Количество: {quantity}"),
                commit=True
            )
        else:
            # Обновляем информацию о существующем инструменте
            tool_id = existing[0][0]
            quantity_old = existing[0][1]
            self._execute_query(
                "UPDATE tools SET quantity=?, last_used=? WHERE id=?",
                (quantity_old + quantity, self.now(), tool_id),
                commit=True
            )
        return ' '.join(options) + ' добавлен в базу\n'

    def delete(self, options):
        good, size, quantity, _, _ = self._get_info(options)
        print(good)
        if not good:
            return Commands.ERROR_OPTIONS

        # Находим инструмент
        tool = self._execute_query(
            "SELECT id, quantity FROM tools WHERE name=? AND size=?",
            (good, str(size)), fetch=True
        )

        if not tool:
            return Commands.NO_GOODS

        tool_id = tool[0][0]
        old_quantity = tool[0][1]

        # Проверяем активные аренды
        active_rents = self._execute_query(
            "SELECT id FROM rent WHERE tool_id=? AND is_done=0",
            (tool_id,), fetch=True
        )

        if active_rents:
            return Commands.ERROR_DELETE_ACTIVE_TOOL

        if quantity < old_quantity:
            self._execute_query(
                "UPDATE tools SET quantity=? WHERE id=?",
                (old_quantity - quantity, tool_id),
                commit=True
            )
        else:
            # Удаляем инструмент
            self._execute_query(
                "DELETE FROM tools WHERE id=?",
                (tool_id,),
                commit=True
            )
        return ' '.join(options) + ' удален из базы\n'

    def search(self, options):
        good, size, _, _, _ = self._get_info(options)
        if not good:
            return Commands.ERROR_OPTIONS

        # Ищем инструменты
        results = self._execute_query(
            "SELECT id FROM tools WHERE name LIKE ?",
            (f'%{good}%',), fetch=True
        )

        if not results:
            return Commands.ERROR_NOT_FOUND

        return [row[0] for row in results]
    
    def add_debtor(self, name, review=5):
        try:
            debtor_id = self._execute_query(
                "INSERT INTO debtors(name, review) VALUES (?, ?)",
                (name, review),
                commit=True
            )
            return debtor_id
        except Exception as e:
            print(str(e))
            return None

    def rent(self, options=None, data=None):
        good, size, quantity, _, name = self._get_info(options)

        if not good or not name:
            return Commands.ERROR_OPTIONS if not good else Commands.ERROR_NOT_NAME

        # Находим или создаем должника
        debtor = self._execute_query(
            "SELECT id FROM debtors WHERE name=?",
            (name,), fetch=True
        )

        if not debtor:
            return Commands.ERROR_NOT_NAME_IN_DB
            debtor_id = self._execute_query(
                "INSERT INTO debtors (name) VALUES (?)",
                (name,),
                commit=True
            )
        else:
            debtor_id = debtor[0][0]

        # Находим инструмент
        tool = self._execute_query(
            "SELECT id, quantity FROM tools WHERE name LIKE ? AND size=?",
            (f'%{good}%', str(size)), fetch=True
        )

        if not tool:
            return Commands.ERROR_NOT_FOUND

        tool_id = tool[0][0]
        tool_quantity = tool[0][1]

        # # Проверяем доступность инструмента
        # active_rents = self._execute_query(
        #     "SELECT SUM(quantity) FROM rent WHERE tool_id=? AND is_done=0",
        #     (tool_id,), fetch=True
        # )[0][0] or 0

        # total_tools = self._execute_query(
        #     "SELECT COUNT(*) FROM tools WHERE id=?",
        #     (tool_id,), fetch=True
        # )[0][0]

        # if total_tools - active_rents < quantity:
        #     return Commands.ERROR_FEW_FOR_RENT

        # Создаем запись об аренде
        if quantity > tool_quantity:
            return Commands.ERROR_FEW_FOR_RENT
        
        self._execute_query(
            "INSERT INTO rent (debtor_id, tool_id, quantity, start_time, end_time) VALUES (?, ?, ?, ?, ?)",
            (debtor_id, tool_id, quantity, self.now(), self.now() + datetime.timedelta(days=7)),
            commit=True
        )
        self._execute_query(
            "UPDATE tools SET quantity=? WHERE id=?",
            (tool_quantity - quantity, tool_id),
            commit=True
        )
        return ' '.join(options) + ' Арендовано\n'

    def unrent(self, options):
        good, size, _, _, name = self._get_info(options)
        if not good or not name:
            return Commands.ERROR_OPTIONS if not good else Commands.ERROR_NOT_NAME

        # Находим должника
        debtor = self._execute_query(
            "SELECT id FROM debtors WHERE name=?",
            (name,), fetch=True
        )

        if not debtor:
            return Commands.ERROR_NOT_NAME

        debtor_id = debtor[0][0]

        # Находим инструмент
        tool = self._execute_query(
            "SELECT id FROM tools WHERE name LIKE ? AND size=?",
            (f'%{good}%', str(size)), fetch=True
        )

        if not tool:
            return Commands.ERROR_NOT_FOUND

        tool_id = tool[0][0]

        # Находим активную аренду
        rent = self._execute_query(
            "SELECT id, quantity FROM rent WHERE debtor_id=? AND tool_id=? AND is_done=0",
            (debtor_id, tool_id), fetch=True
        )

        if not rent:
            return Commands.ERROR_NOT_RENT

        rent_id, rent_quantity = rent[0]

        # Помечаем аренду как завершенную
        self._execute_query(
            "UPDATE rent SET end_time=?, is_done=1 WHERE id=?",
            (self.now(), rent_id),
            commit=True
        )
        return 'Возврат совершен'

    def get_data(self):
        tools = self._execute_query(
            "SELECT name, size, location FROM tools", fetch=True)
        return "\n".join([f"{name}, {size}, {location}" for name, size, location in tools])

    def get_html(self):
        tools = self._execute_query(
            "SELECT id, name, size, quantity, location, last_used, notes FROM tools", fetch=True
        )

        html = "<table border='1'><tr>"
        headers = ["ID", "Наименование", "Размер", "Количество",
                   "Место", "Последнее использование", "Заметки"]
        html += "".join(f"<th>{h}</th>" for h in headers) + "</tr>"

        for row in tools:
            html += "<tr>" + \
                "".join(f"<td>{str(col)}</td>" for col in row) + "</tr>"

        return html + "</table>"

    def get_data_for_ui(self, rows=None):
        if rows:
            placeholders = ",".join("?" * len(rows))
            query = f"SELECT * FROM tools WHERE id IN ({placeholders})"
            tools = self._execute_query(query, rows, fetch=True)
        else:
            tools = self._execute_query("SELECT * FROM tools", fetch=True)

        if not tools:
            return (0, 0, []), []

        columns = ["ID", "Наименование", "Размер", "Количество",
                   "Место", "Последнее использование", "Заметки"]
        items = []
        for row_idx, row in enumerate(tools):
            for col_idx, value in enumerate(row):
                items.append((row_idx, col_idx, str(value)))

        return (len(tools), len(columns), columns), items
    
    def get_data_for_bot(self, rows=None):
        if rows:
            placeholders = ",".join("?" * len(rows))
            query = f"SELECT * FROM tools WHERE id IN ({placeholders})"
            tools = self._execute_query(query, rows, fetch=True)
        else:
            tools = self._execute_query("SELECT * FROM tools", fetch=True)

        if not tools:
            return (0, 0, []), []

        columns = ["ID", "Наименование", "Размер", "Количество",
                   "Место", "Последнее использование", "Заметки"]
        
        if len(tools) == 1:
            tool = tools[0]
            return True, 'Найден инструмент:\n' + \
                '\n'.join(list(map(lambda t: f'{t[0]}: {t[1]}', zip(columns, tool))))
        
        df = pd.DataFrame(tools, columns=columns)

        report_file_name = 'search_reports/' + str(uuid.uuid4()) + '.xlsx'
        df.to_excel(report_file_name, index=False)

        return False, report_file_name

    def get_data_for_ui_rent(self):
        rents = self._execute_query('''
            SELECT r.id, d.name, t.name, t.size, r.quantity
            FROM rent r
            JOIN debtors d ON r.debtor_id = d.id
            JOIN tools t ON r.tool_id = t.id
            ORDER BY r.start_time DESC
        ''', fetch=True)

        if not rents:
            return (0, 0, []), []

        columns = ["ID", "Должник", "Инструмент", "Размер", "Количество"]
        items = []
        for row_idx, row in enumerate(rents):
            for col_idx, value in enumerate(row):
                items.append((row_idx, col_idx, str(value)))

        return (len(rents), len(columns), columns), items

    # def get_data_for_bot(self, rows=None):
    #     if rows:
    #         placeholders = ",".join("?" * len(rows))
    #         tools = self._execute_query(
    #             f"SELECT name, location FROM tools WHERE id IN ({placeholders})",
    #             rows, fetch=True
    #         )
    #     else:
    #         tools = self._execute_query(
    #             "SELECT name, location FROM tools", fetch=True
    #         )

    #     columns = ("Наименование", "Место")
    #     return columns, tools

    def get_data_for_ui_debtors(self):
        debtors = self._execute_query("SELECT * FROM debtors order by id", fetch=True)

        if not debtors:
            return (0, 0, []), []

        columns = ["ID", "Имя", "Отзыв"]
        items = []
        for row_idx, row in enumerate(debtors):
            for col_idx, value in enumerate(row):
                items.append((row_idx, col_idx, str(value)))

        return (len(debtors), len(columns), columns), items

    def _get_info(self, options):
        good = ''
        location = ''
        quantity = 1
        size = 0
        name = ''
        options = [w.lower() for w in options]

        size_words = ['на', 'размер']
        quantity_words = ['количество', 'количества']
        location_words = ['место', 'вместо', 'места', 'локация']
        client_words = ['клиент', 'имя', 'должник']

        good_phrase = []
        i = 0
        while i < len(options) and options[i] not in [*size_words, *quantity_words, *location_words, *client_words]:
            good_phrase.append(options[i])
            i += 1
        good = ' '.join(good_phrase).replace('номер', '№')

        while i < len(options):
            if options[i] in size_words and i+1 < len(options):
                try:
                    size = int(options[i+1])
                except ValueError:
                    if options[i+1] in self.nums:
                        size = self.nums.index(options[i+1])
                i += 1
            elif options[i] in quantity_words and i+1 < len(options):
                try:
                    quantity = int(options[i+1])
                except ValueError:
                    if options[i+1] in self.nums:
                        quantity = self.nums.index(options[i+1])
                i += 1
            elif options[i] in location_words:
                location_phrase = []
                i += 1
                while i < len(options) and options[i] not in [*quantity_words, *size_words, *client_words]:
                    location_phrase.append(options[i])
                    i += 1
                location = ' '.join(location_phrase)
                continue
            elif options[i] in client_words:
                name_phrase = []
                i += 1
                while i < len(options) and options[i] not in [*quantity_words, *size_words, *location_words]:
                    name_phrase.append(options[i])
                    i += 1
                name = ' '.join(name_phrase)
                continue
            i += 1

        return good, size, quantity, location, name
