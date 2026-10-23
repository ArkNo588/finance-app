from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import PortfolioSnapshot
from schemas import SnapshotRead
from security import get_current_user
from services.snapshots import take_snapshot

router = APIRouter(
    prefix="/snapshots",
    tags=["snapshots"],
    dependencies=[Depends(get_current_user)],
)


@router.post("")
def create_snapshot(db: Session = Depends(get_db)):
    return {"accounts_saved": take_snapshot(db)}


@router.get("", response_model=list[SnapshotRead])
def list_snapshots(account_id: int | None = None, db: Session = Depends(get_db)):
    query = select(PortfolioSnapshot).order_by(
        PortfolioSnapshot.snapshot_date, PortfolioSnapshot.account_id
    )
    if account_id is not None:
        query = query.where(PortfolioSnapshot.account_id == account_id)
    return db.scalars(query).all()