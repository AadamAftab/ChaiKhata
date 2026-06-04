# app/schemas/social.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class ProfileCreateSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, description="Unique identifier handle.")
    display_name: str = Field(..., min_length=2, max_length=50, description="Real name.")

class CampaignCreateSchema(BaseModel):
    campaign_id: str = Field(..., min_length=3, max_length=30, description="e.g., 'gokarna_2026'")
    title: str = Field(..., min_length=3, max_length=100, description="e.g., 'Gokarna Surf Trip'")
    members: List[str] = Field(..., min_length=2, description="List of participant usernames.")

class CampaignTransactionSchema(BaseModel):
    payer: str = Field(..., description="The user who paid the total bill upfront.")
    total_bill: float = Field(..., gt=0, description="Total cost of this individual item.")
    description: str = Field(..., max_length=150, description="e.g., 'Beach Shack Dinner'")
    is_itemized: bool = Field(default=False, description="Set to True if split is unequal.")
    allocations: Optional[Dict[str, float]] = Field(default=None, description="Explicit cost breakdown mapping per user.")