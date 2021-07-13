import sqlite3


class SQLiter:

    def __init__(self, database_file):
        # connect to database
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def get_all_sub(self, status=True):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM users WHERE status = ?", (status,)).fetchall()
            return result

    def user_exists(self, telegram_user_id):
        # test user in base
        with self.connection:
            result = self.cursor.execute("SELECT * FROM users WHERE telegram_user_id = ?",
                                         (telegram_user_id,)).fetchall()
            return bool(len(result))

    def add_user(self, telegram_user_id, name, phone, inn, status):
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO users (telegram_user_id, first_name, phone_number, inn, status) VALUES (?, ?, ?, ?, ?)",
                (telegram_user_id, name, phone, inn, status)).fetchall()

    def update_status(self, telegram_user_id, status):
        return self.cursor.execute("UPDATE users SET status = ? WHERE telegram_user_id = ?",
                                   (status, telegram_user_id))
    def close(self):
        self.connection.close()