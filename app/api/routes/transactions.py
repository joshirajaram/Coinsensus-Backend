# Add Transaction, Get Transaction History


from fastapi import APIRouter, Depends, HTTPException
from typing import Any

router = APIRouter()

@router.post("/createTransaction")
def create_user(user: dict) -> Any:
    """
    Create new trans.
    """
    pass