# app/routes/expense.py
from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from app.schemas.expense import ExpenseCreateSchema
from app.core.database import EXPENSE_DATA_STORE

router = APIRouter(prefix="/api/v1/expenses", tags=["Individual Portfolio"])

@router.post("/", status_code=status.HTTP_201_CREATED, summary="Log a localized transaction")
def log_student_expense(expense_payload: ExpenseCreateSchema):
    source_mapping = {"zepto": "Zepto", "zomato": "Zomato", "swiggy": "Swiggy", "cali burrito": "Cali Burrito", "cash": "Cash"}
    normalized_source = expense_payload.source.strip().lower()
    final_source = source_mapping.get(normalized_source, expense_payload.source.strip())

    new_id = len(EXPENSE_DATA_STORE) + 1
    expense_document = {
        "id": new_id,
        "amount": round(expense_payload.amount, 2),
        "source": final_source,
        "category": expense_payload.category.strip(),
        "description": expense_payload.description.strip() if expense_payload.description else None,
        "timestamp": datetime.now().isoformat()
    }
    EXPENSE_DATA_STORE.append(expense_document)
    return {"message": "Transaction token logged successfully", "transaction_id": new_id}

@router.get("/", summary="Fetch full transactional ledger")
def fetch_all_expenses():
    return {"total_count": len(EXPENSE_DATA_STORE), "ledger": EXPENSE_DATA_STORE}

@router.get("/analytics/runway/", summary="Calculate financial burn rate and runway velocity")
def calculate_financial_runway(monthly_allowance: float = 5000.00):
    if monthly_allowance <= 0:
        raise HTTPException(status_code=400, detail="Monthly allowance must be greater than zero.")

    total_spent = sum(item["amount"] for item in EXPENSE_DATA_STORE)
    remaining_balance = max(0.00, monthly_allowance - total_spent)

    if not EXPENSE_DATA_STORE:
        return {"total_spent": 0.00, "remaining_balance": monthly_allowance, "daily_burn_velocity": 0.00, "days_to_broke": "Infinite", "burn_status": "STABLE"}

    timestamps = [datetime.fromisoformat(item["timestamp"]) for item in EXPENSE_DATA_STORE]
    days_elapsed = (max(timestamps) - min(timestamps)).days + 1
    daily_burn_velocity = round(total_spent / days_elapsed, 2)
    days_to_broke = int(remaining_balance // daily_burn_velocity) if daily_burn_velocity > 0 else 999

    burn_status = "CRITICAL_BURN" if daily_burn_velocity > 350 else "ELEVATED" if daily_burn_velocity > 200 else "STABLE"

    return {
        "total_spent": round(total_spent, 2),
        "remaining_balance": round(remaining_balance, 2),
        "days_elapsed_in_tracking": days_elapsed,
        "daily_burn_velocity": daily_burn_velocity,
        "days_to_broke": days_to_broke,
        "burn_status": burn_status
    }