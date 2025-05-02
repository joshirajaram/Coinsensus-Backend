from psycopg2 import Error
from psycopg2 import pool
from models import User, Transaction
import os
from typing import Optional, Dict, List
from core import config

class PostgresDB:
    _instance = None

    def __init__(self):
        self.pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=5,
            dbname=os.getenv('POSTGRES_DB', config.POSTGRES_DB),
            user=os.getenv('POSTGRES_USER', config.POSTGRES_USER),
            password=os.getenv('POSTGRES_PASSWORD', config.POSTGRES_PASSWORD),
            host=os.getenv('POSTGRES_HOST', config.POSTGRES_HOST),
            port=os.getenv('POSTGRES_PORT', config.POSTGRES_PORT)
        )

    def __del__(self):
        self.close_connection()

    def insert_user(self, user: User, block_id: str):
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO users (username, password, public_key, resdb_block_id) 
                    VALUES (%s, %s, %s, %s)
                ''', (user.username, user.password, user.public_key, block_id))
                conn.commit()
        except Error as e:
            print(f"Error inserting user: {e}")
            conn.rollback()
        finally:
            self.pool.putconn(conn)

    def check_user(self, user: User) -> bool:
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute('SELECT 1 FROM users WHERE username = %s', (user.username,))
                return cur.fetchone() is not None
        except Error as e:
            print(f"Error checking user: {e}")
            return False
        finally:
            self.pool.putconn(conn)

    def validate_username_password(self, username: str, password: str) -> bool:
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute('SELECT password FROM users WHERE username = %s', (username,))
                row = cur.fetchone()
                return row is not None and row[0] == password
        except Error as e:
            print(f"Error validating credentials: {e}")
            return False
        finally:
            self.pool.putconn(conn)

    def update_block_id(self, username: str, new_id: int) -> bool:
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute('''
                    UPDATE users 
                    SET resdb_block_id = %s 
                    WHERE username = %s
                ''', (new_id, username))
                conn.commit()
                return cur.rowcount > 0
        except Error as e:
            print(f"Error updating block ID: {e}")
            conn.rollback()
            return False
        finally:
            self.pool.putconn(conn)

    def get_user_block_id(self, username: str) -> Optional[str]:
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute('SELECT resdb_block_id FROM users WHERE username = %s', (username,))
                result = cur.fetchone()
                return str(result[0]) if result else None
        except Error as e:
            print(f"Error getting user block ID: {e}")
            return None
        finally:
            self.pool.putconn(conn)

    def get_user_public_key(self, username: str) -> Optional[str]:
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute('SELECT public_key FROM users WHERE username = %s', (username,))
                result = cur.fetchone()
                return str(result[0]) if result else None
        except Error as e:
            print(f"Error getting user public key: {e}")
            return None
        finally:
            self.pool.putconn(conn)

    def insert_transaction(self, sender: str, receiver: str, amount: int, 
                         description: str, timestamp: float, resdb_transaction_id: str):
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO transactions (sender, receiver, amount, description, timestamp, resdb_transaction_id) 
                    VALUES (%s, %s, %s, %s, to_timestamp(%s), %s)
                ''', (sender, receiver, amount, description, timestamp, resdb_transaction_id))
                conn.commit()
        except Error as e:
            print(f"Error inserting transaction: {e}")
            conn.rollback()
        finally:
            self.pool.putconn(conn)

    def get_transaction_history(self, user: str) -> List[Dict]:
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute('''
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
                } for row in cur.fetchall()]
        except Error as e:
            print(f"Error getting transaction history: {e}")
            return []
        finally:
            self.pool.putconn(conn)

    def get_balances(self, user: str) -> Dict:
        conn = self.pool.getconn()
        try:
            transactions = {}

            # Get sent transactions
            with conn.cursor() as cur:
                cur.execute('''
                    SELECT receiver, amount, description, TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') 
                    FROM transactions 
                    WHERE sender = %s
                    ORDER BY timestamp DESC
                ''', (user,))
                
                for txn in cur.fetchall():
                    if txn[0] not in transactions:
                        transactions[txn[0]] = []
                    transactions[txn[0]].append({
                        "amount": txn[1],
                        "description": txn[2],
                        "timestamp": txn[3]
                    })

                # Get received transactions
                cur.execute('''
                    SELECT sender, amount, description, TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') 
                    FROM transactions 
                    WHERE receiver = %s
                    ORDER BY timestamp DESC
                ''', (user,))
                
                for txn in cur.fetchall():
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
        finally:
            self.pool.putconn(conn)

    def check_connection(self):
        conn = self.pool.getconn()
        try:
            if conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    return True
            else:
                return False
        except Error as e:
            print(f"Error checking database connection: {e}")
            return False
        finally:
            self.pool.putconn(conn)

    def close_connection(self):
        try:
            self.pool.closeall()
        except Error as e:
            print(f"Error closing connection: {e}")

