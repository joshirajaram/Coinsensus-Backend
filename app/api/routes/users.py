# Login, Create New User, Get User Profile


from fastapi import APIRouter, Depends, HTTPException
from typing import Any
from datetime import datetime
from core import db, sqlite_db
from models import User
import uuid

router = APIRouter()

@router.post("/createUser")
def create_user(user: dict) -> Any:
    """
    Create new user.
    """
    user_object = User(
        id = str(uuid.uuid4()),
        public_key = user["public_key"],
        private_key = user["private_key"],
        username = user["username"],
        password = user["password"],
        name = user["username"],
        signup_ts = datetime.now().timestamp(),
    )
    print(user, user_object)
    (id, err) = db.add_user(user_object)
    if err is not None:
        print("Transaction not committed. Error:", err)
    else:
        sqlite_db.SQLiteDB().insert_user(user_object, id)
        print("Transaction committed successfully")
        return id