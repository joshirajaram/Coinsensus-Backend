# Add Transaction, Get Transaction History


from fastapi import APIRouter, Depends, HTTPException
from typing import Any
from datetime import datetime
from core import db
from models import Transaction
import json
import uuid

router = APIRouter()

@router.post("/createTransaction")
def create_transaction(transaction: dict) -> Any:
    """
    Create new trans.
    """
    txn = Transaction(
        id = str(uuid.uuid4()),
        sender = transaction["sender"],
        sender_private_key = transaction["sender_private_key"],
        receiver = transaction["receiver"],
        amount = int(transaction['amount']) * 100,
        timestamp = datetime.now().timestamp()
    )
    err = db.add_transaction(txn)
    if err is not None:
        print("Transaction not committed. Error:", err)
    else:
        print("Transaction committed successfully")
