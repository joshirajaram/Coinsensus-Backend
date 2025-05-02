from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
import uvicorn
import time

from api.main import api_router
from core import postgres_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/healthz")
def health_check():
    postgres = postgres_db.PostgresDB()
    is_db_connected = postgres.check_connection()
    if not is_db_connected:
        return {
            "status": "error",
            "message": "Database connection failed",
            "timestamp": time.time()
        }
    else:
        return {
            "status": "ok",
            "timestamp": time.time()
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
