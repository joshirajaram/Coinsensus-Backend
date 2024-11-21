# Get Balances and Settle Debts

from fastapi import APIRouter, Depends, HTTPException
from typing import Any

router = APIRouter()

@router.post("/createSettlement")
def create_user(user: dict) -> Any:
    """
    Create new settlement.
    """
    pass