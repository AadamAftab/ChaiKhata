# app/main.py
from fastapi import FastAPI, status
from app.routes import expense, social, radar

app = FastAPI(
    title="ChaiKhata Core Modular Engine",
    description="Refactored enterprise-ready campus fintech backend architecture.",
    version="1.3.0"
)

# Mount all single-responsibility sub-routers natively onto the engine tree
app.include_router(expense.router)
app.include_router(social.router)
app.include_router(radar.router)

@app.get("/", status_code=status.HTTP_200_OK, tags=["System Health"])
def read_root():
    return {
        "status": "online", 
        "architecture": "Modular Domain-Driven Layout",
        "campus_node": "IIIT-Bangalore"
    }