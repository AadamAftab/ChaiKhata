# app/core/database.py
from typing import List, Dict

EXPENSE_DATA_STORE: List[dict] = []
USER_PROFILES: Dict[str, str] = {}  
MUTUAL_DEBT_LEDGER: Dict[str, Dict[str, float]] = {}
CAMPAIGN_STORE: Dict[str, dict] = {}

LOCAL_RESTAURANT_DIRECTORY: Dict[str, dict] = {
    "cali_burrito": {
        "name": "Cali Burrito (E-City)",
        "specialty": "Mexican / Burritos",
        "avg_cost_per_head": 250.00,
        "reviews": [
            {"student": "system", "vibe_score": 4, "paisa_vasool_pct": 85, "text": "Solid standard choice near campus."}
        ]
    }
}

# app/core/database.py (Append to the bottom)

CAMPUS_DEALS_REGISTRY: Dict[str, List[dict]] = {
    "cali_burrito": [
        {
            "title": "Tuesday BOGO Student Special",
            "discount_description": "Buy one get one free on all regular size burritos and bowls.",
            "day_of_week": "tuesday",
            "estimated_savings": 170.00
        }
    ],
    "empire_rolls": [
        {
            "title": "Late Night Combo Discount",
            "discount_description": "Get a free single egg roll with any double chicken roll order after 11 PM.",
            "day_of_week": "all",
            "estimated_savings": 60.00
        }
    ]
}