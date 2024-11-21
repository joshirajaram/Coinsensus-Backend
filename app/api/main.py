from fastapi import APIRouter

from api.routes import users, friends, settlements, transactions

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(friends.router, prefix="/friends", tags=["friends"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(settlements.router, prefix="/balances", tags=["balances"])
