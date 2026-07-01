from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Expense

router = APIRouter(prefix="/api/expenses", tags=["expenses"])


class ExpenseCreate(BaseModel):
    amount: float
    category: str
    note: str | None = None


class ExpenseOut(BaseModel):
    id: int
    amount: float
    category: str
    note: str | None
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("", response_model=list[ExpenseOut])
def list_expenses(limit: int = 10, db: Session = Depends(get_db)):
    return (
        db.query(Expense)
        .order_by(Expense.created_at.desc())
        .limit(limit)
        .all()
    )


@router.get("/summary")
def get_month_total(db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    total = (
        db.query(func.sum(Expense.amount))
        .filter(func.strftime("%Y-%m", Expense.created_at) == now.strftime("%Y-%m"))
        .scalar()
    )
    return {"month_total": total or 0}


@router.post("", response_model=ExpenseOut)
def create_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    db_expense = Expense(
        amount=expense.amount, category=expense.category, note=expense.note
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense
