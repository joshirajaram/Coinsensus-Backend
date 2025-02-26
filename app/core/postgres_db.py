import psycopg2
from psycopg2 import Error
from models import User, Transaction
import os
from typing import Optional, Dict, List
from core import config

class PostgresDB:
    _instance = None

    def __init__(self):
        # Get connection details from environment variables for security
        if not PostgresDB._instance:
            PostgresDB._instance = self
            self.connection = psycopg2.connect(
                dbname=os.getenv('POSTGRES_DB', config.POSTGRES_DB),
                user=os.getenv('POSTGRES_USER', config.POSTGRES_USER),
                password=os.getenv('POSTGRES_PASSWORD', config.POSTGRES_PASSWORD),
                host=os.getenv('POSTGRES_HOST', config.POSTGRES_HOST),
                port=os.getenv('POSTGRES_PORT', config.POSTGRES_PORT)
            )
            self.cursor = self.connection.cursor()
        else:
            # Shares values if its not the same instance -> Pseudo singleton
            self.__dict__ = PostgresDB._instance.__dict__

    def __del__(self):
        self.close_connection()

    def insert_user(self, user: User, block_id: str):
        try:
            self.cursor.execute('''
                INSERT INTO users (username, password, public_key, resdb_block_id) 
                VALUES (%s, %s, %s, %s)
            ''', (user.username, user.password, user.public_key, block_id))
            self.connection.commit()
        except Error as e:
            print(f"Error inserting user: {e}")
            self.connection.rollback()

    def check_user(self, user: User) -> bool:
        try:
            self.cursor.execute('SELECT 1 FROM users WHERE username = %s', (user.username,))
            return self.cursor.fetchone() is not None
        except Error as e:
            print(f"Error checking user: {e}")
            return False

    def validate_username_password(self, username: str, password: str) -> bool:
        try:
            self.cursor.execute('SELECT password FROM users WHERE username = %s', (username,))
            row = self.cursor.fetchone()
            return row is not None and row[0] == password
        except Error as e:
            print(f"Error validating credentials: {e}")
            return False

    def update_block_id(self, username: str, new_id: int) -> bool:
        try:
            self.cursor.execute('''
                UPDATE users 
                SET resdb_block_id = %s 
                WHERE username = %s
            ''', (new_id, username))
            self.connection.commit()
            return self.cursor.rowcount > 0
        except Error as e:
            print(f"Error updating block ID: {e}")
            self.connection.rollback()
            return False

    def get_user_block_id(self, username: str) -> Optional[str]:
        try:
            self.cursor.execute('SELECT resdb_block_id FROM users WHERE username = %s', (username,))
            result = self.cursor.fetchone()
            return str(result[0]) if result else None
        except Error as e:
            print(f"Error getting user block ID: {e}")
            return None

    def get_user_public_key(self, username: str) -> Optional[str]:
        try:
            self.cursor.execute('SELECT public_key FROM users WHERE username = %s', (username,))
            result = self.cursor.fetchone()
            return str(result[0]) if result else None
        except Error as e:
            print(f"Error getting user public key: {e}")
            return None

    def insert_transaction(self, sender: str, receiver: str, amount: int, 
                         description: str, timestamp: float, resdb_transaction_id: str):
        try:
            self.cursor.execute('''
                INSERT INTO transactions (sender, receiver, amount, description, timestamp, resdb_transaction_id) 
                VALUES (%s, %s, %s, %s, to_timestamp(%s), %s)
            ''', (sender, receiver, amount, description, timestamp, resdb_transaction_id))
            self.connection.commit()
        except Error as e:
            print(f"Error inserting transaction: {e}")
            self.connection.rollback()

    def get_transaction_history(self, user: str) -> List[Dict]:
        try:
            self.cursor.execute('''
                SELECT sender, receiver, amount, description, TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') 
                FROM transactions 
                WHERE sender = %s OR receiver = %s 
                ORDER BY timestamp DESC
            ''', (user, user))
            
            return [{
                "sender": row[0],
                "receiver": row[1],
                "amount": row[2],
                "description": row[3],
                "timestamp": row[4]
            } for row in self.cursor.fetchall()]
        except Error as e:
            print(f"Error getting transaction history: {e}")
            return []

    def get_balances(self, user: str) -> Dict:
        try:
            transactions = {}

            # Get sent transactions
            self.cursor.execute('''
                SELECT receiver, amount, description, TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') 
                FROM transactions 
                WHERE sender = %s
                ORDER BY timestamp DESC
            ''', (user,))
            
            for txn in self.cursor.fetchall():
                if txn[0] not in transactions:
                    transactions[txn[0]] = []
                transactions[txn[0]].append({
                    "amount": txn[1],
                    "description": txn[2],
                    "timestamp": txn[3]
                })

            # Get received transactions
            self.cursor.execute('''
                SELECT sender, amount, description, TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') 
                FROM transactions 
                WHERE receiver = %s
                ORDER BY timestamp DESC
            ''', (user,))
            
            for txn in self.cursor.fetchall():
                if txn[0] not in transactions:
                    transactions[txn[0]] = []
                transactions[txn[0]].append({
                    "amount": -1 * txn[1],
                    "description": txn[2],
                    "timestamp": txn[3]
                })
            
            return transactions
        except Error as e:
            print(f"Error getting balances: {e}")
            return {}

    def close_connection(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
        except Error as e:
            print(f"Error closing connection: {e}")

