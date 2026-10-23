from decimal import Decimal

import yfinance as yf
from sqlalchemy import select
from sqlalchemy.orm import Session

from models import AssetPrice


def fetch_latest(ticker: str):
    """Dernier cours de clôture connu, ou None si Yahoo ne répond pas."""
    stock = yf.Ticker(ticker)
    history = stock.history(period="5d")
    if history.empty:
        return None
    price = Decimal(str(round(float(history["Close"].iloc[-1]), 4)))
    price_date = history.index[-1].date()
    try:
        currency = stock.fast_info["currency"]
    except Exception:
        currency = "EUR"
    return price, price_date, currency


def refresh_prices(db: Session, tickers: list[str]):
    updated, failed = [], []
    for ticker in tickers:
        try:
            result = fetch_latest(ticker)
        except Exception:
            result = None
        if result is None:
            failed.append(ticker)
            continue

        price, price_date, currency = result
        row = db.scalars(
            select(AssetPrice).where(
                AssetPrice.ticker == ticker, AssetPrice.price_date == price_date
            )
        ).first()
        if row:
            row.price, row.currency = price, currency
        else:
            db.add(
                AssetPrice(
                    ticker=ticker, price=price, currency=currency, price_date=price_date
                )
            )
        updated.append(ticker)
    db.commit()
    return updated, failed