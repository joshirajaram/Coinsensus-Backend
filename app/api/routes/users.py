# Login, Create New User, Get User Profile


from fastapi import APIRouter, Depends, HTTPException
from typing import Any

router = APIRouter()

@router.post("/createUser")
def create_user(user: dict) -> Any:
    """
    Create new user.
    """
    pass