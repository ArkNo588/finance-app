from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import Account, AssetPrice, Transaction
from schemas import AccountValue, PositionRead
from security import get_current_user

router = APIRouter(
    prefix="/portfolio",
    tags=["portfolio"],
    dependencies=[Depends(get_current_user)],
)


def latest_prices(db: Session) -> dict[str, AssetPrice]:
    rows = db.scalars(select(AssetPrice).order_by(AssetPrice.price_date)).all()
    return {row.ticker: row for row in rows}  # le cours le plus récent écrase les autres


def build_positions(db: Session) -> list[PositionRead]:
    transactions = db.scalars(
        select(Transaction)
        .where(Transaction.type.in_(["buy", "sell"]))
        .order_by(Transaction.date, Transaction.id)
    ).all()

    book: dict[tuple[int, str], dict[str, Decimal]] = {}
    for t in transactions:
        pos = book.setdefault((t.account_id, t.ticker), {"qty": Decimal(0), "cost": Decimal(0)})
        if t.type == "buy":
            pos["qty"] += t.quantity
            pos["cost"] += t.quantity * t.unit_price + t.fees
        else:
            if t.quantity > pos["qty"]:
                raise HTTPException(
                    status_code=409,
                    detail=f"La transaction {t.id} vend plus que la quantité détenue",
                )
            average = pos["cost"] / pos["qty"]
            pos["cost"] -= average * t.quantity
            pos["qty"] -= t.quantity

    prices = latest_prices(db)
    result = []
    for (account_id, ticker), pos in book.items():
        if pos["qty"] <= 0:
            continue
        price = prices.get(ticker)
        market_value = unrealized_pl = None
        if price:
            market_value = (pos["qty"] * price.price).quantize(Decimal("0.01"))
            unrealized_pl = (market_value - pos["cost"]).quantize(Decimal("0.01"))
        result.append(
            PositionRead(
                account_id=account_id,
                ticker=ticker,
                quantity=pos["qty"],
                average_cost=(pos["cost"] / pos["qty"]).quantize(Decimal("0.0001")),
                total_cost=pos["cost"].quantize(Decimal("0.01")),
                last_price=price.price if price else None,
                price_date=price.price_date if price else None,
                market_value=market_value,
                unrealized_pl=unrealized_pl,
            )
        )
    return result


def build_cash(db: Session, accounts: list[Account]) -> dict[int, Decimal]:
    cash = {a.id: Decimal(0) for a in accounts}
    for t in db.scalars(select(Transaction)).all():
        if t.type in ("deposit", "dividend"):
            cash[t.account_id] += t.amount
        elif t.type == "withdrawal":
            cash[t.account_id] -= t.amount
        elif t.type == "buy":
            cash[t.account_id] -= t.amount + t.fees
        elif t.type == "sell":
            cash[t.account_id] += t.amount - t.fees
    return cash


@router.get("/positions", response_model=list[PositionRead])
def positions(db: Session = Depends(get_db)):
    return build_positions(db)


def compute_account_values(db: Session) -> list[AccountValue]:
    accounts = db.scalars(select(Account).order_by(Account.id)).all()
    cash = build_cash(db, accounts)
    holdings = {a.id: Decimal(0) for a in accounts}
    unpriced = {a.id: 0 for a in accounts}

    for p in build_positions(db):
        if p.market_value is None:
            holdings[p.account_id] += p.total_cost
            unpriced[p.account_id] += 1
        else:
            holdings[p.account_id] += p.market_value

    return [
        AccountValue(
            account_id=a.id,
            name=a.name,
            type=a.type,
            cash=cash[a.id],
            holdings_value=holdings[a.id],
            total_value=cash[a.id] + holdings[a.id],
            unpriced_positions=unpriced[a.id],
        )
        for a in accounts
    ]


@router.get("/accounts", response_model=list[AccountValue])
def account_values(db: Session = Depends(get_db)):
    return compute_account_values(db)