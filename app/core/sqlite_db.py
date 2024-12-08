import sqlite3
from models import User

class SQLiteDB:
    def __init__(self):
        self.connection = sqlite3.connect('coinsensus.db')
        self.cursor = self.connection.cursor()

    def insert_user(self, user: User, block_id: str):
        self.cursor.execute('''
            INSERT INTO users (username, password, public_key, resdb_block_id) 
            VALUES (?, ?, ?, ?)
        ''', (user.username, user.password, user.public_key, block_id))
        self.connection.commit()

    def get_user(self, user: User):
        # Query data from the table
        self.cursor.execute('SELECT * FROM users WHERE username=?', (user.username))

        # Fetch all rows
        rows = self.cursor.fetchall()

        # Print results
        for row in rows:
            print(row)

    def close_connection(self):
        self.connection.close()
