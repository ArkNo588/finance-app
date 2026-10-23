from fastapi import FastAPI
from sqlalchemy import text

from database import engine
from routers import accounts

app = FastAPI(title="Finance App")
app.include_router(accounts.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/db-check")
def db_check():
    with engine.connect() as conn:
        version = conn.execute(text("SELECT version()")).scalar()
    return {"database": "ok", "version": version}