# Add Transaction, Get Transaction History


from fastapi import APIRouter, Depends, HTTPException
from typing import Any
from datetime import datetime
from core import db
from models import Transaction
from core import sqlite_db
import uuid

router = APIRouter()

@router.post("/createTransaction")
def create_transaction(transaction: dict) -> Any:
    """
    Create new trans.
    """
    # transaction{
    #     "method": "add_expense",
    #     "paid_by": "user_id",
    #     "owed_by": ["user_id_1", "user_id_2"],
    #     "owed_amounts": [100, 100],
    #     "amount": 300
    # }
    asset = {
        "data": { 
            "method": transaction["method"],
            "total_owed_amount": transaction["amount"],
            "paid_by": transaction["paid_by"],
            "owed_by": transaction["owed_by"],
            "owed_amounts": transaction["owed_amounts"],
            "description": transaction["description"]
        }
    }
    sender_block_id = sqlite_db.SQLiteDB().get_user_block_id(transaction["paid_by"])
    sender_user_details = db.get_user_details(sender_block_id)
    
    for i in range(len(transaction["owed_by"])):
        receiver_public_key = sqlite_db.SQLiteDB().get_user_public_key(transaction["owed_by"][i])
        txn = Transaction(
            id = str(uuid.uuid4()),
            sender = sender_user_details['public_key'],
            sender_private_key = sender_user_details['private_key'],
            receiver = receiver_public_key,
            amount = int(transaction["owed_amounts"][i]),
            timestamp = datetime.now().timestamp(),
            asset = asset
        )
        (id, err) = db.add_transaction(txn)
        if err is not None:
            print("Transaction not committed. Error:", err)
            return {
                'success': False,
                'error': err
            }
        else:
            print("Transaction committed successfully")
    return {
        'success': True,
        'id': id
    }

@router.get("/getTransactionHistory")
def get_transaction_history(username: str) -> Any:
    resdb_block_id = sqlite_db.SQLiteDB().get_user_block_id(username)
    user_details = db.get_user_details(resdb_block_id)
    user_public_key = user_details['public_key']
    friends = user_details["friends"]
    friends_public_keys = []
    for friend in friends:
        friends_public_keys.append(sqlite_db.SQLiteDB().get_user_public_key(friend))
    transactions = db.get_transaction_history(user_public_key, friends, friends_public_keys)
    return {
        'transactions': transactions
    }
