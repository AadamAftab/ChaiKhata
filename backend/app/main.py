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
# This list acts as our temporary database table for individual expenses
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
                "description": "Late-night instant Maggi and ice cream haul"
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
@app.post(
    "/api/v1/expenses/", 
    response_model=dict, 
    status_code=status.HTTP_201_CREATED,
    summary="Log a localized transaction"
)
def log_student_expense(expense_payload: ExpenseCreateSchema):
    """
    Ingests, validates, and logs an incoming student expense token.
    Enforces normalization mapping for standard campus options.
    """
    # Standardize common strings to avoid duplicate variations in analytics
    source_mapping = {
        "zepto": "Zepto",
        "zomato": "Zomato",
        "swiggy": "Swiggy",
        "cali burrito": "Cali Burrito",
        "cash": "Cash"
    }
    
    normalized_source = expense_payload.source.strip().lower()
    final_source = source_mapping.get(normalized_source, expense_payload.source.strip())

    # Build the database item profile
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
    return {
        "message": "Transaction token logged successfully",
        "transaction_id": new_id,
        "data": expense_document
    }

@app.get(
    "/api/v1/expenses/", 
    response_model=dict, 
    status_code=status.HTTP_200_OK,
    summary="Fetch full transactional ledger"
)
def fetch_all_expenses():
    """
    Exposes the complete in-memory ledger list array sorted descending by newest entries.
    """
    # Returns newest items first
    sorted_ledger = sorted(EXPENSE_DATA_STORE, key=lambda x: x["id"], reverse=True)
    return {
        "engine_node": "IIITB_SANDBOX_STORE",
        "total_records": len(EXPENSE_DATA_STORE),
        "ledger": sorted_ledger
    }