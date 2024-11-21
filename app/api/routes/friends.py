# Add Friends, Get Friend List, Create Group, Get Group List


from fastapi import APIRouter, Depends, HTTPException
from typing import Any

router = APIRouter()

@router.post("/createFriend")
def create_user(user: dict) -> Any:
    """
    Create new friend.
    """
    pass