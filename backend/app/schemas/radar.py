# app/schemas/radar.py
from pydantic import BaseModel, Field

class CampusReviewSchema(BaseModel):
    restaurant_key: str = Field(..., description="Unique slug ID, e.g., 'cali_burrito'")
    restaurant_name: str = Field(..., description="Clean display name of the venue")
    specialty: str = Field(..., description="e.g., 'Mughlai / Rolls'")
    avg_cost_per_head: float = Field(..., gt=0)
    reviewer_username: str = Field(..., description="The student posting the review")
    vibe_score: int = Field(..., ge=1, le=5, description="Atmosphere rating from 1 to 5")
    paisa_vasool_pct: int = Field(..., ge=0, le=100, description="Wallet efficiency percentage from 0% to 100%")
    review_text: str = Field(..., max_length=250, description="Brief field notes for other students")

class CampusDealSchema(BaseModel):
    vendor_key: str = Field(..., description="e.g., 'cali_burrito', 'empire_rolls'")
    title: str = Field(..., description="e.g., 'Tuesday BOGO Offer'")
    discount_description: str = Field(..., description="e.g., 'Buy one get one free on all regular burritos'")
    day_of_week: str = Field(..., description="Lowercase weekday name, e.g., 'tuesday', 'friday', 'all'")
    estimated_savings: float = Field(..., gt=0, description="Approximate cash saved per transaction using this deal")