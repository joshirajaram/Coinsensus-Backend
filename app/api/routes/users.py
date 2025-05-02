# Login, Create New User, Get User Profile


from fastapi import APIRouter, Depends, HTTPException
from typing import Any
from datetime import datetime
from core import db, sqlite_db, postgres_db
from models import User
import uuid

router = APIRouter()
postgres = postgres_db.PostgresDB()

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
    # if sqlite_db.SQLiteDB().check_user(user_object):
    if postgres.check_user(user_object):
        err = "User already exists"
        return err

    (id, err) = db.add_user(user_object)
    if err is not None:
        print("Transaction not committed. Error:", err)
    else:
        # sqlite_db.SQLiteDB().insert_user(user_object, id)
        postgres.insert_user(user_object, id)
        print("Transaction committed successfully")
        return id,user_object.username
    
@router.get("/login/{username}/{password}")
def login(username: str, password: str) -> Any:
    print("Received login request:")
    print(f"Username: {username}")
    print(f"Password: {password}")
    
    # success = sqlite_db.SQLiteDB().validate_username_password(username, password)
    success = postgres.validate_username_password(username, password)
    print(success)
    if success:
        return {"success": True}
    else:
        return {"success": False}
    
@router.get("/getUser")
def get_user(username: str) -> Any:
    # resdb_block_id = sqlite_db.SQLiteDB().get_user_block_id(username)
    resdb_block_id = postgres.get_user_block_id(username)
    # print("Block id",resdb_block_id)
    
    user_details = db.get_user_details(resdb_block_id)
    ## map to User model and return
    return user_details

@router.post("/addFriend")
def add_friend(username: str,friendName: str) -> Any:
    # resdb_block_id = sqlite_db.SQLiteDB().get_user_block_id(username)
    resdb_block_id = postgres.get_user_block_id(username)
    new_id=db.add_friend(resdb_block_id, friendName)
    # resdb_block_id_friend = sqlite_db.SQLiteDB().get_user_block_id(friendName)
    resdb_block_id_friend = postgres.get_user_block_id(friendName)
    new_id_friend = db.add_friend(resdb_block_id_friend, username)
    # if(sqlite_db.SQLiteDB().update_block_id(username, new_id) and 
    #    sqlite_db.SQLiteDB().update_block_id(friendName, new_id_friend)):
    if(postgres.update_block_id(username, new_id) and 
       postgres.update_block_id(friendName, new_id_friend)):
        return {
            'success': True
        }
    return {
        'success': False,
    }


@router.get("/getFriends")
def get_friends(username: str) -> Any:
    # resdb_block_id = sqlite_db.SQLiteDB().get_user_block_id(username)
    resdb_block_id = postgres.get_user_block_id(username)
    user_details = db.get_user_details(resdb_block_id)
    return {'friends': user_details["friends"]}
