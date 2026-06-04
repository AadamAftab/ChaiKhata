# app/routes/radar.py
from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from app.schemas.radar import CampusReviewSchema
from app.core.database import LOCAL_RESTAURANT_DIRECTORY, USER_PROFILES

router = APIRouter(prefix="/api/v1/radar", tags=["IIITB Crowdsourced Radar"])

@router.post("/reviews/", status_code=status.HTTP_201_CREATED, summary="Crowdsource a local food joint review")
def log_campus_restaurant_review(payload: CampusReviewSchema):
    reviewer = payload.reviewer_username.strip().lower()
    if reviewer not in USER_PROFILES:
        raise HTTPException(status_code=404, detail=f"Student '{reviewer}' does not exist.")

    r_key = payload.restaurant_key.strip().lower()
    if r_key not in LOCAL_RESTAURANT_DIRECTORY:
        LOCAL_RESTAURANT_DIRECTORY[r_key] = {
            "name": payload.restaurant_name.strip(),
            "specialty": payload.specialty.strip(),
            "avg_cost_per_head": round(payload.avg_cost_per_head, 2),
            "reviews": []
        }

    LOCAL_RESTAURANT_DIRECTORY[r_key]["reviews"].append({
        "student": reviewer,
        "vibe_score": payload.vibe_score,
        "paisa_vasool_pct": payload.paisa_vasool_pct,
        "text": payload.review_text.strip(),
        "timestamp": datetime.now().isoformat()
    })
    return {"message": f"Review securely logged for {LOCAL_RESTAURANT_DIRECTORY[r_key]['name']}", "restaurant_key": r_key}

@router.get("/explore/", status_code=status.HTTP_200_OK, summary="Explore food spots backed by community indices")
def explore_campus_food_radar():
    explorer_feed = []
    for key, data in LOCAL_RESTAURANT_DIRECTORY.items():
        reviews_list = data["reviews"]
        avg_vibe = round(sum(r["vibe_score"] for r in reviews_list) / len(reviews_list), 1) if reviews_list else 0.0
        avg_paisa = int(sum(r["paisa_vasool_pct"] for r in reviews_list) / len(reviews_list)) if reviews_list else 0

        explorer_feed.append({
            "key": key,
            "name": data["name"],
            "specialty": data["specialty"],
            "avg_cost_per_head": data["avg_cost_per_head"],
            "aggregated_metrics": {"community_vibe_score": avg_vibe, "paisa_vasool_index_pct": avg_paisa},
            "total_reviews_count": len(reviews_list)
        })
    return {"spots": sorted(explorer_feed, key=lambda x: x["aggregated_metrics"]["paisa_vasool_index_pct"], reverse=True)}


# app/routes/radar.py (Append to the bottom)
from app.schemas.radar import CampusDealSchema
from app.core.database import CAMPUS_DEALS_REGISTRY
from app.routes.expense import calculate_financial_runway # Cross-reference your runway math!

@router.post("/deals/", status_code=status.HTTP_201_CREATED, summary="Register a local campus deal promotion")
def log_local_campus_deal(payload: CampusDealSchema):
    v_key = payload.vendor_key.strip().lower()
    if v_key not in CAMPUS_DEALS_REGISTRY:
        CAMPUS_DEALS_REGISTRY[v_key] = []
        
    deal_entry = {
        "title": payload.title.strip(),
        "discount_description": payload.discount_description.strip(),
        "day_of_week": payload.day_of_week.strip().lower(),
        "estimated_savings": round(payload.estimated_savings, 2)
    }
    CAMPUS_DEALS_REGISTRY[v_key].append(deal_entry)
    return {"message": f"Deal successfully posted for vendor '{v_key}'", "current_deals_count": len(CAMPUS_DEALS_REGISTRY[v_key])}


@router.get("/advisor/{username}", status_code=status.HTTP_200_OK, summary="Generate smart financial and lifestyle recommendations")
def generate_ai_campus_advice(username: str, monthly_allowance: float = 5000.00):
    """
    Analyzes historical spending velocity, tracks the 'Days to Broke' vector, 
    and builds a contextual advisory payload mapped against active local E-City promotions.
    """
    u_clean = username.strip().lower()
    
    # 1. Fetch current cash runway metrics directly from our portfolio analytics logic
    portfolio_stats = calculate_financial_runway(monthly_allowance=monthly_allowance)
    burn_status = portfolio_stats.get("burn_status", "STABLE")
    daily_velocity = portfolio_stats.get("daily_burn_velocity", 0.0)
    days_left = portfolio_stats.get("days_to_broke", 999)

    # 2. Match active promotions based on current real-time clock factors
    current_day = datetime.now().strftime("%A").lower() # e.g., 'thursday'
    matched_saving_deals = []
    
    for vendor, deals in CAMPUS_DEALS_REGISTRY.items():
        for deal in deals:
            if deal["day_of_week"] == current_day or deal["day_of_week"] == "all":
                matched_saving_deals.append({
                    "vendor": vendor,
                    "deal_title": deal["title"],
                    "actionable_savings": deal["estimated_savings"]
                })

    # 3. Hybrid Analysis Engine: Evaluate metrics against local deals to formulate tactical tips
    advisory_insights = []
    lifestyle_warnings = []
    
    if burn_status == "CRITICAL_BURN":
        advisory_insights.append(f"⚠️ HIGH THREAT ALERT: Your daily cash burn velocity is ₹{daily_velocity}/day. At this rate, you have exactly {days_left} days left before you run out of funds.")
        if matched_saving_deals:
            top_deal = max(matched_saving_deals, key=lambda x: x["actionable_savings"])
            advisory_insights.append(f"TACTICAL MITIGATION: Stop using open delivery apps. Walk to {top_deal['vendor']} right now to leverage the '{top_deal['deal_title']}'—this saves you roughly ₹{top_deal['actionable_savings']} instantly.")
    elif burn_status == "ELEVATED":
        advisory_insights.append(f"Warning: Spending velocity is climbing. Consider utilizing campus vendor discount cycles to stabilize your runway trajectory.")
    else:
        advisory_insights.append("Your financial velocity profile is healthy and entirely within safe parameters. Keep practicing solo budget discipline.")

    # Lifestyle Health Auditing based on merchant categories found in individual expense entries
    from app.core.database import EXPENSE_DATA_STORE
    junk_categories_count = sum(1 for item in EXPENSE_DATA_STORE if item.get("category", "").lower() in ["snacks", "fast food", "late night"])
    
    if junk_categories_count >= 3:
        lifestyle_warnings.append("HEALTH WARNING: Your transaction log shows multiple consecutive fast food entries. Reallocate some discretionary funds to the campus juice bar to re-balance your wellness profile.")
    else:
        lifestyle_warnings.append("HEALTH PROFILE: Nutrient allocation index is normal. Minimal junk rows detected in your ledger sequence.")

    # 4. Return the structured, contextual prompt engineering context model
    return {
        "student_node": u_clean,
        "burn_status_evaluation": burn_status,
        "days_to_broke_countdown": days_left,
        "active_campus_deals_today": matched_saving_deals,
        "ai_financial_advisor_output": advisory_insights,
        "ai_lifestyle_health_output": lifestyle_warnings
    }