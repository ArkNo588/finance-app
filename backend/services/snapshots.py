from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from models import PortfolioSnapshot
from routers.portfolio import compute_account_values


def take_snapshot(db: Session) -> int:
    today = datetime.now(ZoneInfo("Europe/Paris")).date()
    values = compute_account_values(db)
    for v in values:
        row = db.scalars(
            select(PortfolioSnapshot).where(
                PortfolioSnapshot.account_id == v.account_id,
                PortfolioSnapshot.snapshot_date == today,
            )
        ).first()
        if row:
            row.cash, row.holdings_value, row.total_value = (
                v.cash, v.holdings_value, v.total_value,
            )
        else:
            db.add(
                PortfolioSnapshot(
                    account_id=v.account_id,
                    snapshot_date=today,
                    cash=v.cash,
                    holdings_value=v.holdings_value,
                    total_value=v.total_value,
                )
            )
    db.commit()
    return len(values)