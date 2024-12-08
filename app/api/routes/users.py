# Login, Create New User, Get User Profile


from fastapi import APIRouter, Depends, HTTPException
from typing import Any
from datetime import datetime
from core import db
from models import User
import uuid

router = APIRouter()

@router.post("/createUser")
def create_user(user: dict) -> Any:
    """
    Create new user.
    """
    user = User(
        id = str(uuid.uuid4()),
        public_key = user["public_key"],
        private_key = user["private_key"],
        username = user["username"],
        password = user["password"],
        name = user["name"],
        signup_ts = datetime.now().timestamp(),
    )
    err = db.add_user(user)
    if err is not None:
        print("Transaction not committed. Error:", err)
    else:
        print("Transaction committed successfully")