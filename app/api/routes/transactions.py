# Add Transaction, Get Transaction History


from fastapi import APIRouter, Depends, HTTPException
from typing import Any
from datetime import datetime
from core import db
from models import Transaction
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
    #     "sender": "user_id",
    #     "sender_private_key": "private_key",
    #     "receiver": "user_id",
    #     "amount": 300
    # }
    asset = {
        "data": { 
            "method": transaction["method"],
            "total_owed_amount": transaction["amount"],
            "paid_by": transaction["paid_by"],
            "owed_by": transaction["owed_by"],
            "owed_amounts": transaction["owed_amounts"]
        }
    }
    txn = Transaction(
        id = str(uuid.uuid4()),
        sender = transaction["sender"],
        sender_private_key = transaction["sender_private_key"],
        receiver = transaction["receiver"],
        amount = int(transaction["amount"]),
        timestamp = datetime.now().timestamp(),
        asset = asset
    )
    err = db.add_transaction(txn)
    if err is not None:
        print("Transaction not committed. Error:", err)
    else:
        print("Transaction committed successfully")
