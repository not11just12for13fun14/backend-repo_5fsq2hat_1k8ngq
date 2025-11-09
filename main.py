import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AIRequest(BaseModel):
    message: str
    context: Optional[str] = None


class AIResponse(BaseModel):
    reply: str


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


@app.post("/ai/assist", response_model=AIResponse)
async def ai_assist(payload: AIRequest):
    """Lightweight AI stub for the assistant UI.
    This provides deterministic, helpful replies without external dependencies.
    """
    user_msg = (payload.message or "").strip().lower()

    # Simple intent heuristics
    if any(k in user_msg for k in ["mri", "scan", "imaging"]):
        reply = (
            "Next MRI availability: Today 3:30 PM, 5:10 PM; Tomorrow 9:20 AM, 10:40 AM. "
            "Technician on duty: Patel. Prep: remove metal, NPO 4h if contrast. "
            "Would you like me to book a 30‑minute slot and notify radiology?"
        )
    elif any(k in user_msg for k in ["summarize", "summary", "chart", "visit"]):
        reply = (
            "Here’s a concise chart summary: 3 recent visits, HTN well‑controlled, HbA1c 6.7%, "
            "last creatinine 1.0 mg/dL, no med allergies. Current meds: lisinopril 10 mg QD, metformin 500 mg BID. "
            "Flagged: follow‑up A1c in 6 weeks. Need a discharge note template?"
        )
    elif any(k in user_msg for k in ["bed", "icu", "occupancy", "forecast"]):
        reply = (
            "ICU occupancy forecast (next 24h): 78% ±6%. 2 step‑downs free by 18:00. "
            "Recommend deferring elective post‑op ICU holds until tomorrow AM. Want a resource plan?"
        )
    elif any(k in user_msg for k in ["schedule", "appointment", "book", "slot"]):
        reply = (
            "I can propose optimal slots based on clinician load and patient preferences. "
            "Please share patient ID, preferred day, and department."
        )
    else:
        reply = (
            "I can help with scheduling, bed forecasts, and quick chart summaries. "
            "Ask me things like: ‘Find next MRI slot for Jane Doe’ or ‘Summarize patient ABC123 last 3 visits.’"
        )

    return AIResponse(reply=reply)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
