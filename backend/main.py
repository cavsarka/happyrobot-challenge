# main.py
from fastapi import FastAPI, HTTPException, Header, Depends
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import Load, Call, Booking
import os
import httpx

app = FastAPI()

# Simple API key authentication
API_KEY = os.getenv("API_KEY", "test_api_key_12345")
FMCSA_API_KEY = os.getenv("FMCSA_API_KEY", "")

def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return True

def load_to_dict(load: Load) -> dict:
    return {
        "load_id": load.load_id,
        "origin": load.origin,
        "destination": load.destination,
        "pickup_datetime": load.pickup_datetime.isoformat() if load.pickup_datetime else None,
        "delivery_datetime": load.delivery_datetime.isoformat() if load.delivery_datetime else None,
        "equipment_type": load.equipment_type,
        "loadboard_rate": float(load.loadboard_rate),
        "notes": load.notes,
        "weight": load.weight,
        "commodity_type": load.commodity_type,
        "num_of_pieces": load.num_of_pieces,
        "miles": load.miles,
        "dimensions": load.dimensions,
        "status": load.status
    }

# ENDPOINT 1: Search for available loads
@app.get("/api/v1/loads")
def search_loads(
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    equipment_type: Optional[str] = None,
    pickup_date: Optional[str] = None,
    db: Session = Depends(get_db),
    _auth: bool = Depends(verify_api_key)
):
    """
    HappyRobot calls this when the AI agent needs to find loads
    """
    query = db.query(Load)

    if origin:
        query = query.filter(Load.origin.ilike(f"%{origin}%"))

    if destination:
        query = query.filter(Load.destination.ilike(f"%{destination}%"))

    if equipment_type:
        query = query.filter(Load.equipment_type.ilike(f"%{equipment_type}%"))

    if pickup_date:
        query = query.filter(Load.pickup_datetime >= pickup_date)

    total = query.count()
    results = query.limit(3).all()

    return {
        "statusCode": 200,
        "body": {
            "loads": [load_to_dict(l) for l in results],
            "total": total
        }
    }

# ENDPOINT 2: Get specific load details
@app.get("/api/v1/loads/{load_id}")
def get_load(load_id: str, db: Session = Depends(get_db), _auth: bool = Depends(verify_api_key)):
    """
    Get detailed info about a specific load
    """
    load = db.query(Load).filter(Load.load_id == load_id).first()

    if not load:
        return {
            "statusCode": 404,
            "body": {"error": "Load not found"}
        }

    return {
        "statusCode": 200,
        "body": {"load": load_to_dict(load)}
    }


# ENDPOINT 5: Record final call outcome
@app.post("/api/v1/calls/complete")
def complete_call(request: dict, db: Session = Depends(get_db), _auth: bool = Depends(verify_api_key)):
    """
    Called at the end of each call to store the outcome
    """
    print(f"[CALL COMPLETE] {request}")

    # Save call record
    call = Call(
        call_id=request.get("call_id"),
        mc_number=request.get("mc_number"),
        carrier_name=request.get("carrier_name"),
        duration_seconds=request.get("duration_seconds"),
        outcome=request.get("outcome"),
        sentiment=request.get("sentiment"),
        negotiation_rounds=request.get("negotiation_rounds", 0)
    )
    db.add(call)

    # If booked, save booking record
    if request.get("outcome") == "booked" and request.get("load_id"):
        booking = Booking(
            call_id=request.get("call_id"),
            load_id=request.get("load_id"),
            mc_number=request.get("mc_number"),
            agreed_rate=request.get("final_rate", 0),
            loadboard_rate=request.get("loadboard_rate", 0),
            negotiation_rounds=request.get("negotiation_rounds", 0)
        )
        # Calculate margin
        if booking.loadboard_rate and booking.agreed_rate:
            booking.margin_percentage = round(
                ((float(booking.loadboard_rate) - float(booking.agreed_rate)) / float(booking.loadboard_rate)) * 100, 2
            )
        db.add(booking)

    db.commit()

    return {
        "statusCode": 200,
        "body": {
            "saved": True,
            "call_id": call.call_id
        }
    }

# ENDPOINT 6: Get call analytics (for your dashboard)
@app.get("/api/v1/analytics/calls")
def get_call_analytics(db: Session = Depends(get_db), _auth: bool = Depends(verify_api_key)):
    """
    Returns aggregated metrics for your custom dashboard
    """
    total_calls = db.query(Call).count()
    total_bookings = db.query(Booking).count()
    conversion_rate = round((total_bookings / total_calls * 100), 1) if total_calls > 0 else 0

    avg_rounds = db.query(func.avg(Call.negotiation_rounds)).scalar() or 0

    # Outcome distribution
    outcomes = {}
    outcome_rows = db.query(Call.outcome, func.count(Call.id)).group_by(Call.outcome).all()
    for outcome, count in outcome_rows:
        outcomes[outcome or "unknown"] = count

    # Sentiment distribution
    sentiments = {}
    sentiment_rows = db.query(Call.sentiment, func.count(Call.id)).group_by(Call.sentiment).all()
    for sentiment, count in sentiment_rows:
        sentiments[sentiment or "unknown"] = count

    # Average rate reduction
    avg_margin = db.query(func.avg(Booking.margin_percentage)).scalar() or 0

    return {
        "statusCode": 200,
        "body": {
            "total_calls": total_calls,
            "bookings": total_bookings,
            "conversion_rate": round(float(conversion_rate), 1),
            "avg_negotiation_rounds": round(float(avg_rounds), 1),
            "outcomes": outcomes,
            "sentiment_distribution": sentiments,
            "avg_rate_reduction": round(float(avg_margin), 1)
        }
    }

# ENDPOINT 7: Lookup carrier info by MC number via FMCSA API
@app.get("/api/v1/carriers/{mc_number}")
async def lookup_carrier(mc_number: str, _auth: bool = Depends(verify_api_key)):
    """
    Takes an MC number and queries the FMCSA API to get
    the carrier's business name and whether they're allowed to operate.
    """
    if not FMCSA_API_KEY:
        raise HTTPException(status_code=500, detail="FMCSA API key is not configured")

    fmcsa_url = f"https://mobile.fmcsa.dot.gov/qc/services/carriers/docket-number/{mc_number}?webKey={FMCSA_API_KEY}"

    async with httpx.AsyncClient() as client:
        response = await client.get(fmcsa_url, timeout=10.0)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail="Failed to fetch data from FMCSA API"
        )

    data = response.json()
    content = data.get("content", [])
    if not content:
        return {
            "statusCode": 404,
            "body": {"error": "No carrier found for the given MC number"}
        }

    carrier = content[0].get("carrier", {})

    return {
        "statusCode": 200,
        "body": {
            "legal_name": carrier.get("legalName"),
            "dba_name": carrier.get("dbaName"),
            "allowed_to_operate": carrier.get("allowedToOperate"),
            "dot_number": carrier.get("dotNumber"),
            "status_code": carrier.get("statusCode"),
            "phy_city": carrier.get("phyCity"),
            "phy_state": carrier.get("phyState"),
        }
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "freight-broker-api"}
