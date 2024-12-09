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

    def get_user_block_id(self, username: str):
        # Query data from the table
        # self.cursor.execute('SELECT resdb_block_id FROM users')
        self.cursor.execute('SELECT resdb_block_id FROM users WHERE username=\'{}\''.format(username))
        # self.cursor.execute('SELECT resdb_block_id FROM users WHERE username=user_name_1')
        # print("Block id",str(self.cursor.fetchall()[0][0]))
        return str(self.cursor.fetchall()[0][0])
        # return "Hello"

    def close_connection(self):
        self.connection.close()
