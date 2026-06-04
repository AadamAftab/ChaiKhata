# backend/app/main.py
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

app = FastAPI(
    title="ChaiKhata Core Engine",
    description="Backend operations engine for individual portfolio analytics, social debt ledgers, and campus guide pipelines.",
    version="1.0.0"
)

# -------------------------------------------------------------------------
# DATA REPOSITORIES (In-Memory Sandbox Databases)
# -------------------------------------------------------------------------
EXPENSE_DATA_STORE: List[dict] = []

# New in-memory ledgers for social tracking
USER_PROFILES: Dict[str, str] = {}  # Maps username -> Display Name
MUTUAL_DEBT_LEDGER: Dict[str, Dict[str, float]] = {} 
# Structured as: { "User_A": { "User_B": balance } }
# Net Balance rule: If MUTUAL_DEBT_LEDGER["Aarav"]["Vinay"] == 150.0,
# it means Aarav owes Vinay ₹150.0. If negative, Vinay owes Aarav.

# -------------------------------------------------------------------------
# DATA VALIDATION CONTRACTS (Pydantic Schemas)
# -------------------------------------------------------------------------
class ExpenseCreateSchema(BaseModel):
    amount: float = Field(..., gt=0)
    source: str
    category: str
    description: Optional[str] = Field(None, max_length=150)

class ProfileCreateSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, description="Unique identifier handle, e.g., 'aarav_11'")
    display_name: str = Field(..., min_length=2, max_length=50, description="Real name, e.g., 'Aarav Sharma'")

class PeerSplitSchema(BaseModel):
    payer: str = Field(..., description="The username of the friend who paid the bill upfront.")
    borrower: str = Field(..., description="The username of the friend splitting the bill who owes money.")
    total_bill: float = Field(..., gt=0, description="The total amount of the transaction.")
    split_amount: Optional[float] = Field(default=None, description="Optional custom share. If blank, defaults to a clean 50/50 split.")
    description: Optional[str] = Field(None, max_length=150, description="Context, e.g., 'Cali Burrito lunch'")

# -------------------------------------------------------------------------
# CORE LOGIC ROUTING
# -------------------------------------------------------------------------
@app.get("/", status_code=status.HTTP_200_OK)
def read_root():
    return {"status": "online", "system": "ChaiKhata Core API Node"}

@app.post("/api/v1/expenses/", status_code=status.HTTP_201_CREATED)
def log_student_expense(expense_payload: ExpenseCreateSchema):
    new_id = len(EXPENSE_DATA_STORE) + 1
    expense_document = {
        "id": new_id,
        "amount": round(expense_payload.amount, 2),
        "source": expense_payload.source.strip(),
        "category": expense_payload.category.strip(),
        "timestamp": datetime.now().isoformat()
    }
    EXPENSE_DATA_STORE.append(expense_document)
    return {"message": "Transaction token logged successfully", "transaction_id": new_id}

@app.get("/api/v1/expenses/")
def fetch_all_expenses():
    return {"ledger": EXPENSE_DATA_STORE}

@app.get("/api/v1/analytics/runway/")
def calculate_financial_runway(monthly_allowance: float = 5000.00):
    total_spent = sum(item["amount"] for item in EXPENSE_DATA_STORE)
    remaining_balance = max(0.00, monthly_allowance - total_spent)
    return {"total_spent": total_spent, "remaining_balance": remaining_balance}

# -------------------------------------------------------------------------
# SOCIAL LEDGER OPERATIONS ENDPOINTS (Step 4)
# -------------------------------------------------------------------------
@app.post(
    "/api/v1/profiles/", 
    status_code=status.HTTP_201_CREATED,
    summary="Register a peer campus profile"
)
def create_user_profile(profile: ProfileCreateSchema):
    """
    Registers a friend into the network tracking layer and initializes their empty ledger matrix.
    """
    username_clean = profile.username.strip().lower()
    
    if username_clean in USER_PROFILES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Profile with username '{username_clean}' already exists within this node."
        )
        
    USER_PROFILES[username_clean] = profile.display_name.strip()
    MUTUAL_DEBT_LEDGER[username_clean] = {}
    return {
        "message": "Peer profile initialized successfully",
        "username": username_clean,
        "display_name": USER_PROFILES[username_clean]
    }

@app.post(
    "/api/v1/splits/", 
    status_code=status.HTTP_200_OK,
    summary="Log a mutual transaction split between two friends"
)
def log_peer_transaction_split(split_payload: PeerSplitSchema):
    """
    Processes a financial split transaction. Computes proportional shares
    and registers balances bidirectionally inside the network adjacency map.
    """
    payer = split_payload.payer.strip().lower()
    borrower = split_payload.borrower.strip().lower()

    if payer not in USER_PROFILES or borrower not in USER_PROFILES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both of the specified usernames do not exist in the active system profiles."
        )
        
    if payer == borrower:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Self-referential splits are invalid. Payer and borrower must be distinct accounts."
        )

    # If no custom share is specified, split the bill evenly down the middle (50/50 split)
    allocated_debt = split_payload.split_amount if split_payload.split_amount else (split_payload.total_bill / 2)
    allocated_debt = round(allocated_debt, 2)

    # Update Payer -> Borrower matrix balance tracking
    # If borrower isn't in payer's dictionary yet, initialize their balance at 0.0
    if borrower not in MUTUAL_DEBT_LEDGER[payer]:
        MUTUAL_DEBT_LEDGER[payer][borrower] = 0.0
    if payer not in MUTUAL_DEBT_LEDGER[borrower]:
        MUTUAL_DEBT_LEDGER[borrower][payer] = 0.0

    # Execute directional balancing
    # Payer ledger tracks that the borrower owes them positive funds
    MUTUAL_DEBT_LEDGER[borrower][payer] = round(MUTUAL_DEBT_LEDGER[borrower][payer] + allocated_debt, 2)
    # Borrower ledger tracks that they owe the payer negative funds
    MUTUAL_DEBT_LEDGER[payer][borrower] = round(MUTUAL_DEBT_LEDGER[payer][borrower] - allocated_debt, 2)

    return {
        "status": "MUTUAL_LEDGER_MUTATED",
        "message": f"Successfully recorded split. {USER_PROFILES[borrower]} owes {USER_PROFILES[payer]} ₹{allocated_debt}.",
        "current_balance_summary": {
            f"{payer}_view": f"Net from {borrower}: +₹{MUTUAL_DEBT_LEDGER[borrower][payer]}",
            f"{borrower}_view": f"Net to {payer}: -₹{MUTUAL_DEBT_LEDGER[borrower][payer]}"
        }
    }

@app.get(
    "/api/v1/splits/ledger/",
    status_code=status.HTTP_200_OK,
    summary="Fetch full directional balance sheets"
)
def fetch_social_balances():
    """
    Exposes the raw state maps showing exactly who owes what across the node.
    """
    return {
        "active_profiles": USER_PROFILES,
        "directional_matrix": MUTUAL_DEBT_LEDGER
    }