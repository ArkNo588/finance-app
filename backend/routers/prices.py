from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import AssetPrice, Transaction
from schemas import PriceRead
from security import get_current_user
from services.prices import refresh_prices

router = APIRouter(
    prefix="/prices",
    tags=["prices"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/refresh")
def refresh(db: Session = Depends(get_db)):
    tickers = db.scalars(
        select(Transaction.ticker).where(Transaction.ticker.is_not(None)).distinct()
    ).all()
    updated, failed = refresh_prices(db, list(tickers))
    return {"updated": updated, "failed": failed}


@router.get("/{ticker}", response_model=list[PriceRead])
def price_history(ticker: str, db: Session = Depends(get_db)):
    query = (
        select(AssetPrice)
        .where(AssetPrice.ticker == ticker.upper())
        .order_by(AssetPrice.price_date.desc())
    )
    return db.scalars(query).all()