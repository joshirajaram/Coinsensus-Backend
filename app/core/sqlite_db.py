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
        
    def check_user(self, user: User) -> bool:
        self.cursor.execute('SELECT 1 FROM users WHERE username = ?', (user.username,)) 
        row = self.cursor.fetchone()
        return row is not None


    
    def validate_username_password(self, username: str, password: str) -> bool:
        self.cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
        row = self.cursor.fetchone()
        print('entered password', password)
        print('correct password', row[0])
        if row:
            return row[0] == password  # Compare stored password with the input
        return False  # Return False if the user is not found


    def update_block_id(self, username: str, new_id: int) -> bool:
        try:
            self.cursor.execute('''
                UPDATE users 
                SET resdb_block_id = ? 
                WHERE username = ?
            ''', (new_id, username))
            self.connection.commit()
            if self.cursor.rowcount > 0:
                return True
            return False
            
        except sqlite3.Error as e:
            print(f"Error updating block ID: {e}")
            return False

    def get_user_block_id(self, username: str):
        self.cursor.execute('SELECT resdb_block_id FROM users WHERE username=\'{}\''.format(username))
        return str(self.cursor.fetchall()[0][0])
    
    def get_user_public_key(self, username: str):
        self.cursor.execute('SELECT public_key FROM users WHERE username=\'{}\''.format(username))
        return str(self.cursor.fetchall()[0][0])

    def close_connection(self):
        self.connection.close()
