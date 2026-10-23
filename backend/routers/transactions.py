from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import Account, Transaction
from schemas import TransactionCreate, TransactionRead
from security import get_current_user

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[TransactionRead])
def list_transactions(account_id: int | None = None, db: Session = Depends(get_db)):
    query = select(Transaction).order_by(Transaction.date.desc(), Transaction.id.desc())
    if account_id is not None:
        query = query.where(Transaction.account_id == account_id)
    return db.scalars(query).all()


@router.post("", response_model=TransactionRead, status_code=201)
def create_transaction(data: TransactionCreate, db: Session = Depends(get_db)):
    if db.get(Account, data.account_id) is None:
        raise HTTPException(status_code=404, detail="Compte introuvable")

    values = data.model_dump()
    if values["ticker"]:
        values["ticker"] = values["ticker"].strip().upper()
    if data.type in ("buy", "sell"):
        # le montant est calculé côté serveur : jamais de contradiction possible
        values["amount"] = (data.quantity * data.unit_price).quantize(Decimal("0.01"))

    transaction = Transaction(**values)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.get(Transaction, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction introuvable")
    db.delete(transaction)
    db.commit()