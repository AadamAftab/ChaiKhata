# backend/app/main.py
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

app = FastAPI(title="ChaiKhata Premium Engine", version="1.1.0")

# -------------------------------------------------------------------------
# GLOBAL IN-MEMORY REPOSITORIES
# -------------------------------------------------------------------------
EXPENSE_DATA_STORE: List[dict] = []
USER_PROFILES: Dict[str, str] = {}  # username -> display_name
MUTUAL_DEBT_LEDGER: Dict[str, Dict[str, float]] = {}

# Step 5 Structural Database Container
CAMPAIGN_STORE: Dict[str, dict] = {}
# Schema layout: 
# {
#   "gokarna_2026": {
#        "title": "Gokarna Surf Trip",
#        "members": ["aadam", "aarav", "vinay"],
#        "queue": [ {transaction_document} ]
#   }
# }

# -------------------------------------------------------------------------
# VALIDATION MODULE CONTRACTS (Pydantic Schemas)
# -------------------------------------------------------------------------
class ExpenseCreateSchema(BaseModel):
    amount: float = Field(..., gt=0)
    source: str
    category: str
    description: Optional[str] = Field(None, max_length=150)

class ProfileCreateSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    display_name: str = Field(..., min_length=2, max_length=50)

class PeerSplitSchema(BaseModel):
    payer: str
    borrower: str
    total_bill: float
    split_amount: Optional[float] = None
    description: Optional[str] = None

# Step 5: Campaign Engineering Schemas
class CampaignCreateSchema(BaseModel):
    campaign_id: str = Field(..., min_length=3, max_length=30, description="URL safe unique identifier, e.g., 'gokarna_2026'")
    title: str = Field(..., min_length=3, max_length=100, description="Display name, e.g., 'Gokarna Beach Trip'")
    members: List[str] = Field(..., min_length=2, description="List of participant usernames involved in this container.")

class CampaignTransactionSchema(BaseModel):
    payer: str = Field(..., description="The user who paid the total bill upfront.")
    total_bill: float = Field(..., gt=0, description="Total cost of this individual item.")
    description: str = Field(..., max_length=150, description="e.g., 'Seafood & Veg Dinner at Beach Shack'")
    is_itemized: bool = Field(default=False, description="Set to True if split is unequal based on custom consumption.")
    # If is_itemized is True, allocations maps username -> exact cost they owe
    allocations: Optional[Dict[str, float]] = Field(default=None, description="Explicit cost breakdown mapping per user.")

# -------------------------------------------------------------------------
# FALLBACK PASS ENDPOINTS (Steps 2 - 4)
# -------------------------------------------------------------------------
@app.get("/")
def read_root(): return {"status": "online", "engine": "ChaiKhata Premium Node"}

@app.post("/api/v1/profiles/", status_code=status.HTTP_201_CREATED)
def create_user_profile(profile: ProfileCreateSchema):
    u = profile.username.strip().lower()
    if u in USER_PROFILES: raise HTTPException(400, "Profile matches an existing node.")
    USER_PROFILES[u] = profile.display_name.strip()
    MUTUAL_DEBT_LEDGER[u] = {}
    return {"message": "Profile initialized", "username": u}

# -------------------------------------------------------------------------
# SYSTEM CAMPAIGN & TRIP ENGINE OPERATIONS (Step 5)
# -------------------------------------------------------------------------
@app.post("/api/v1/campaigns/", status_code=status.HTTP_201_CREATED, summary="Initialize a shared Trip/Campaign vault")
def create_campaign_vault(campaign: CampaignCreateSchema):
    c_id = campaign.campaign_id.strip().lower()
    if c_id in CAMPAIGN_STORE:
        raise HTTPException(400, detail="Campaign identifier already active.")
    
    # Verify all group members exist as registered users in our app
    for member in campaign.members:
        member_clean = member.strip().lower()
        if member_clean not in USER_PROFILES:
            raise HTTPException(404, detail=f"Member registration check failed: User '{member_clean}' does not exist.")

    CAMPAIGN_STORE[c_id] = {
        "title": campaign.title.strip(),
        "members": [m.strip().lower() for m in campaign.members],
        "queue": []
    }
    return {"message": "Shared campaign vault deployed successfully", "campaign_id": c_id}

@app.post("/api/v1/campaigns/{campaign_id}/transactions/", status_code=status.HTTP_200_OK, summary="Push an itemized or equal transaction into a trip queue")
def push_campaign_transaction(campaign_id: str, tx_payload: CampaignTransactionSchema):
    c_id = campaign_id.strip().lower()
    if c_id not in CAMPAIGN_STORE:
        raise HTTPException(404, detail="Target campaign vault context not found.")

    payer_clean = tx_payload.payer.strip().lower()
    if payer_clean not in CAMPAIGN_STORE[c_id]["members"]:
        raise HTTPException(400, detail="The specified transaction payer must be an registered member of this specific campaign.")

    # Validation and processing logic for custom itemized breakdowns (Gokarna Veg/Non-Veg Case)
    if tx_payload.is_itemized:
        if not tx_payload.allocations:
            raise HTTPException(400, detail="Allocations map must be provided if is_itemized flag is set to True.")
        
        # Ensure sum of explicit allocations matches the total bill precisely to avoid leakage
        allocation_sum = sum(tx_payload.allocations.values())
        if abs(allocation_sum - tx_payload.total_bill) > 0.05:
            raise HTTPException(400, detail=f"Data verification crash: Itemized allocation matrix sum (₹{allocation_sum}) does not match Total Bill amount (₹{tx_payload.total_bill}).")
    
    # Save transaction block directly into the chronological array queue
    tx_document = {
        "id": len(CAMPAIGN_STORE[c_id]["queue"]) + 1,
        "payer": payer_clean,
        "total_bill": round(tx_payload.total_bill, 2),
        "description": tx_payload.description.strip(),
        "is_itemized": tx_payload.is_itemized,
        "allocations": tx_payload.allocations if tx_payload.is_itemized else None,
        "timestamp": datetime.now().isoformat()
    }
    
    CAMPAIGN_STORE[c_id]["queue"].append(tx_document)
    return {"message": "Transaction token queued successfully into campaign", "tx_id": tx_document["id"]}

@app.get("/api/v1/campaigns/{campaign_id}/settle/", status_code=status.HTTP_200_OK, summary="Execute multi-way itemized matrix settlement calculations")
def calculate_campaign_settlement(campaign_id: str):
    c_id = campaign_id.strip().lower()
    if c_id not in CAMPAIGN_STORE:
        raise HTTPException(404, detail="Target campaign vault context not found.")

    campaign = CAMPAIGN_STORE[c_id]
    members = campaign["members"]
    
    # Initialize metric tracking grids
    total_trip_cost = 0.00
    amount_paid_by_user = {m: 0.00 for m in members}
    debt_incurred_by_user = {m: 0.00 for m in members}

    # Iterate through the entire transaction queue
    for tx in campaign["queue"]:
        total_trip_cost += tx["total_bill"]
        amount_paid_by_user[tx["payer"]] += tx["total_bill"]

        if tx["is_itemized"]:
            # Apply strict custom weight allocations
            for member in members:
                member_debt = tx["allocations"].get(member, 0.00)
                debt_incurred_by_user[member] += member_debt
        else:
            # Fallback to absolute standard equal distribution split
            split_share = tx["total_bill"] / len(members)
            for member in members:
                debt_incurred_by_user[member] += split_share

    # Compute Net Status vectors: Paid - Incurred
    net_balances = {}
    for m in members:
        net_balances[m] = round(amount_paid_by_user[m] - debt_incurred_by_user[m], 2)

    return {
        "campaign_id": c_id,
        "campaign_title": campaign["title"],
        "analytics_summary": {
            "total_combined_expenditure": round(total_trip_cost, 2),
            "per_capita_contributions": amount_paid_by_user,
            "actual_consumption_debts": debt_incurred_by_user
        },
        "resolution_balances": net_balances,
        "instructions": "Positive metrics indicate the campaign owes that user. Negative metrics indicate the user must pay into the vault to balance the node."
    }