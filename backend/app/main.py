# backend/app/main.py
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

app = FastAPI(
    title="ChaiKhata Core Engine",
    description="Backend operations engine for individual portfolio analytics, social debt ledgers, and campus guide pipelines.",
    version="1.0.0"
)

# -------------------------------------------------------------------------
# DATA REPOSITORY (In-Memory Database Sandbox)
# -------------------------------------------------------------------------
EXPENSE_DATA_STORE: List[dict] = []

# -------------------------------------------------------------------------
# DATA VALIDATION CONTRACTS (Pydantic Schemas)
# -------------------------------------------------------------------------
class ExpenseCreateSchema(BaseModel):
    amount: float = Field(..., gt=0, description="The monetary value of the transaction, must be greater than zero.")
    source: str = Field(..., description="The merchant or origin source: 'Zepto', 'Zomato', 'Swiggy', 'Cali Burrito', or 'Cash'")
    category: str = Field(..., description="The thematic grouping: e.g., 'Snacks', 'Main Meals', 'Groceries', 'Travel'")
    description: Optional[str] = Field(None, max_length=150, description="Optional brief context text.")

    class Config:
        json_schema_extra = {
            "example": {
                "amount": 180.50,
                "source": "Zepto",
                "category": "Snacks",
                "description": "Late-night instant Maggi haul"
            }
        }

# -------------------------------------------------------------------------
# ROOT ROUTE
# -------------------------------------------------------------------------
@app.get("/", status_code=status.HTTP_200_OK)
def read_root():
    return {
        "status": "online",
        "system": "ChaiKhata Core API Node",
        "timestamp": datetime.now().isoformat()
    }

# -------------------------------------------------------------------------
# TRANSACTIONAL API ENDPOINTS
# -------------------------------------------------------------------------
@app.post("/api/v1/expenses/", status_code=status.HTTP_201_CREATED)
def log_student_expense(expense_payload: ExpenseCreateSchema):
    source_mapping = {
        "zepto": "Zepto",
        "zomato": "Zomato",
        "swiggy": "Swiggy",
        "cali burrito": "Cali Burrito",
        "cash": "Cash"
    }
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

@app.get("/api/v1/expenses/")
def fetch_all_expenses():
    return {"total_count": len(EXPENSE_DATA_STORE), "ledger": EXPENSE_DATA_STORE}

# -------------------------------------------------------------------------
# MATHEMATICAL ANALYTICS ENGINE (Step 3)
# -------------------------------------------------------------------------
@app.get(
    "/api/v1/analytics/runway/", 
    status_code=status.HTTP_200_OK,
    summary="Calculate financial burn rate and runway velocity"
)
def calculate_financial_runway(monthly_allowance: float = 5000.00):
    """
    Evaluates total expenditures against an allowance parameter.
    Computes daily spending velocity and predicts exact days until financial exhaustion.
    """
    if monthly_allowance <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Monthly allowance parameter must be greater than zero."
        )

    # 1. Calculate total outflow from our repository loop
    total_spent = sum(item["amount"] for item in EXPENSE_DATA_STORE)
    remaining_balance = max(0.00, monthly_allowance - total_spent)

    if not EXPENSE_DATA_STORE:
        return {
            "total_spent": 0.00,
            "remaining_balance": monthly_allowance,
            "daily_burn_velocity": 0.00,
            "days_to_broke": "Infinite",
            "burn_status": "STABLE",
            "message": "No expenses recorded yet. Your financial status is completely stable."
        }

    # 2. Parse timestamps to track chronological days elapsed
    timestamps = [datetime.fromisoformat(item["timestamp"]) for item in EXPENSE_DATA_STORE]
    oldest_tx = min(timestamps)
    newest_tx = max(timestamps)
    
    # Compute the delta span of active usage (ensure minimum of 1 day to prevent DivisionByZero)
    days_elapsed = (newest_tx - oldest_tx).days + 1
    
    # 3. Compute core velocity math metrics
    daily_burn_velocity = round(total_spent / days_elapsed, 2)
    
    if daily_burn_velocity > 0:
        days_to_broke = int(remaining_balance // daily_burn_velocity)
    else:
        days_to_broke = 999  # Safe fallback if items exist but value is zero

    # 4. Generate dynamic, student-friendly threat assessment levels
    # Let's say a baseline safe daily speed for an Indian hostel student is ₹200/day
    if daily_burn_velocity > 350:
        burn_status = "CRITICAL_BURN"
        message = "⚠️ Danger! Your food/Zepto spending velocity is unsustainable. Slow down immediately."
    elif daily_burn_velocity > 200:
        burn_status = "ELEVATED"
        message = "Warning: Spending velocity is climbing. Consider cutting back on dining out."
    else:
        burn_status = "STABLE"
        message = "Excellent. Your spending velocity is entirely within safe parameters."

    return {
        "total_spent": round(total_spent, 2),
        "remaining_balance": round(remaining_balance, 2),
        "days_elapsed_in_tracking": days_elapsed,
        "daily_burn_velocity": daily_burn_velocity,
        "days_to_broke": days_to_broke,
        "burn_status": burn_status,
        "alert_message": message
    }