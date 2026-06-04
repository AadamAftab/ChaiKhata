# backend/app/main.py
from fastapi import FastAPI, status
from datetime import datetime

app = FastAPI(
    title="ChaiKhata Core Engine",
    description="The foundational API engine for individual portfolio analytics, social debt ledgers, and campus guide pipelines.",
    version="1.0.0"
)

@app.get("/", status_code=status.HTTP_200_OK)
def read_root():
    """
    Root verification endpoint confirming active system health state.
    """
    return {
        "status": "online",
        "system_node": "ChaiKhata_API_V1",
        "timestamp": datetime.now().isoformat(),
        "message": "Workspace initialization completely successful. Core engine spinning up smoothly."
    }