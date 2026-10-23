from fastapi import FastAPI
from sqlalchemy import text

from database import engine
from routers import accounts, auth, portfolio, prices, transactions

app = FastAPI(title="Finance App")
app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(portfolio.router)
app.include_router(prices.router)


@app.get("/health")
def health():
    return {"status": "ok"}
