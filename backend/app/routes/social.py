# app/routes/social.py
from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from app.schemas.social import ProfileCreateSchema, CampaignCreateSchema, CampaignTransactionSchema
from app.core.database import USER_PROFILES, MUTUAL_DEBT_LEDGER, CAMPAIGN_STORE

router = APIRouter(prefix="/api/v1/social", tags=["Social Debt Ledgers"])

@router.post("/profiles/", status_code=status.HTTP_201_CREATED, summary="Register a peer campus profile")
def create_user_profile(profile: ProfileCreateSchema):
    u = profile.username.strip().lower()
    if u in USER_PROFILES: 
        raise HTTPException(status_code=400, detail="Profile already exists.")
    USER_PROFILES[u] = profile.display_name.strip()
    MUTUAL_DEBT_LEDGER[u] = {}
    return {"message": "Peer profile initialized successfully", "username": u}

@router.post("/campaigns/", status_code=status.HTTP_201_CREATED, summary="Initialize a shared Trip/Campaign vault")
def create_campaign_vault(campaign: CampaignCreateSchema):
    c_id = campaign.campaign_id.strip().lower()
    if c_id in CAMPAIGN_STORE: 
        raise HTTPException(status_code=400, detail="Campaign identifier already active.")
    for member in campaign.members:
        if member.strip().lower() not in USER_PROFILES:
            raise HTTPException(status_code=404, detail=f"User '{member}' does not exist.")
    CAMPAIGN_STORE[c_id] = {"title": campaign.title.strip(), "members": [m.strip().lower() for m in campaign.members], "queue": []}
    return {"message": "Shared campaign vault deployed successfully", "campaign_id": c_id}

@router.post("/campaigns/{campaign_id}/transactions/", summary="Push a transaction into a trip queue")
def push_campaign_transaction(campaign_id: str, tx_payload: CampaignTransactionSchema):
    c_id = campaign_id.strip().lower()
    if c_id not in CAMPAIGN_STORE: 
        raise HTTPException(status_code=404, detail="Campaign not found.")
    
    payer_clean = tx_payload.payer.strip().lower()
    if tx_payload.is_itemized and not tx_payload.allocations:
        raise HTTPException(status_code=400, detail="Allocations map required for itemized splits.")

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
    return {"message": "Transaction token queued successfully", "tx_id": tx_document["id"]}

@router.get("/campaigns/{campaign_id}/settle/", summary="Execute multi-way matrix settlement calculations")
def calculate_campaign_settlement(campaign_id: str):
    c_id = campaign_id.strip().lower()
    if c_id not in CAMPAIGN_STORE: 
        raise HTTPException(status_code=404, detail="Campaign not found.")

    campaign = CAMPAIGN_STORE[c_id]
    members = campaign["members"]
    total_trip_cost = 0.0
    amount_paid_by_user = {m: 0.0 for m in members}
    debt_incurred_by_user = {m: 0.0 for m in members}

    for tx in campaign["queue"]:
        total_trip_cost += tx["total_bill"]
        amount_paid_by_user[tx["payer"]] += tx["total_bill"]
        if tx["is_itemized"]:
            for m in members:
                debt_incurred_by_user[m] += tx["allocations"].get(m, 0.0)
        else:
            share = tx["total_bill"] / len(members)
            for m in members:
                debt_incurred_by_user[m] += share

    net_balances = {m: round(amount_paid_by_user[m] - debt_incurred_by_user[m], 2) for m in members}
    return {"campaign_id": c_id, "total_combined_expenditure": total_trip_cost, "resolution_balances": net_balances}