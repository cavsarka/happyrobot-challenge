# main.py
from fastapi import FastAPI, HTTPException, Header, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date, Integer, case
try:
    from .database import get_db
    from .models import Load, Call, Booking
except ImportError:
    from database import get_db
    from models import Load, Call, Booking
from datetime import datetime
import os
import re
import httpx
from geopy.geocoders import Nominatim
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple API key authentication
API_KEY = os.getenv("API_KEY", "")
FMCSA_API_KEY = os.getenv("FMCSA_API_KEY", "")

def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return True

def calculate_friction(avg_rounds: float, acceptance_rate: float) -> int:
    # Blend negotiation complexity (rounds) with non-acceptance behavior.
    rounds_score = max(0.0, min(100.0, (float(avg_rounds or 0.0) / 3.0) * 100.0))
    non_acceptance_rate = max(0.0, min(100.0, 100.0 - float(acceptance_rate or 0.0)))
    return round((0.6 * rounds_score) + (0.4 * non_acceptance_rate))

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

geolocator = Nominatim(user_agent="Acme Logistics")

def _normalize_city_key(city: Optional[str]) -> Optional[str]:
    if not city:
        return None
    normalized = re.sub(r"\s+", " ", city.strip())
    normalized = re.sub(r"\s*,\s*", ", ", normalized)
    return normalized.lower()

PRESET_GEOCODE_COORDS: Dict[str, Tuple[float, float]] = {
    "Chicago, IL": (41.8781, -87.6298),
    "Tuscaloosa, AL": (33.2098, -87.5692),
    "Dallas, TX": (32.7767, -96.7970),
    "Atlanta, GA": (33.7490, -84.3880),
    "Miami, FL": (25.7617, -80.1918),
    "Los Angeles, CA": (34.0522, -118.2437),
    "Phoenix, AZ": (33.4484, -112.0740),
    "Seattle, WA": (47.6062, -122.3321),
    "Portland, OR": (45.5152, -122.6784),
    "Denver, CO": (39.7392, -104.9903),
    "Salt Lake City, UT": (40.7608, -111.8910),
    "Houston, TX": (29.7604, -95.3698),
    "New Orleans, LA": (29.9511, -90.0715),
    "Boston, MA": (42.3601, -71.0589),
    "New York, NY": (40.7128, -74.0060),
    "Memphis, TN": (35.1495, -90.0490),
    "St. Louis, MO": (38.6270, -90.1994),
    "St Louis, MO": (38.6270, -90.1994),
    "Detroit, MI": (42.3314, -83.0458),
    "Columbus, OH": (39.9612, -82.9988),
    "Minneapolis, MN": (44.9778, -93.2650),
    "Kansas City, MO": (39.0997, -94.5786),
    "Kansas City, KS": (39.1142, -94.6275),
    "San Diego, CA": (32.7157, -117.1611),
    "Las Vegas, NV": (36.1699, -115.1398),
    "Charlotte, NC": (35.2271, -80.8431),
    "Jacksonville, FL": (30.3322, -81.6557),
    "San Antonio, TX": (29.4241, -98.4936),
    "Oklahoma City, OK": (35.4676, -97.5164),
    "Nashville, TN": (36.1627, -86.7816),
    "Birmingham, AL": (33.5186, -86.8104),
    "Cleveland, OH": (41.4993, -81.6944),
    "Pittsburgh, PA": (40.4406, -79.9959),
    "Raleigh, NC": (35.7796, -78.6382),
    "Richmond, VA": (37.5407, -77.4360),
    "Orlando, FL": (28.5383, -81.3792),
    "Tampa, FL": (27.9506, -82.4572),
    "Albuquerque, NM": (35.0844, -106.6504),
    "Indianapolis, IN": (39.7684, -86.1581),
    "Louisville, KY": (38.2527, -85.7585),
    "Omaha, NE": (41.2565, -95.9345),
    "Sacramento, CA": (38.5816, -121.4944),
    "Reno, NV": (39.5296, -119.8138),
    "Buffalo, NY": (42.8864, -78.8784),
    "Baltimore, MD": (39.2904, -76.6122),
    "Philadelphia, PA": (39.9526, -75.1652),
    "Milwaukee, WI": (43.0389, -87.9065),
    "Boise, ID": (43.6150, -116.2023),
    "Spokane, WA": (47.6588, -117.4260),
    "El Paso, TX": (31.7619, -106.4850),
    "Providence, RI": (41.8240, -71.4128),
    "Hartford, CT": (41.7658, -72.6734),
    "Tulsa, OK": (36.1540, -95.9928),
    "Little Rock, AR": (34.7465, -92.2896),
    "Anchorage, AK": (61.2181, -149.9003),
    "Fairbanks, AK": (64.8378, -147.7164),
    "Albany, NY": (42.6526, -73.7562),
    "Newark, NJ": (40.7357, -74.1724),
    "Des Moines, IA": (41.5868, -93.6250),
    "Sioux Falls, SD": (43.5446, -96.7311),
    "Baton Rouge, LA": (30.4515, -91.1871),
    "Mobile, AL": (30.6954, -88.0399),
    "Greensboro, NC": (36.0726, -79.7920),
    "Charleston, SC": (32.7765, -79.9311),
    "Fresno, CA": (36.7378, -119.7871),
    "Grand Rapids, MI": (42.9634, -85.6681),
    "Lexington, KY": (38.0406, -84.5037),
    "Cincinnati, OH": (39.1031, -84.5120),
    "Wichita, KS": (37.6872, -97.3301),
    "San Francisco, CA": (37.7749, -122.4194),
    "Austin, TX": (30.2672, -97.7431),
    "Nashua, NH": (42.7654, -71.4676),
    "Madison, WI": (43.0731, -89.4012),
    "Norfolk, VA": (36.8508, -76.2859),
    "Bismarck, ND": (46.8083, -100.7837),
}

GEOCODE_CACHE: Dict[str, Tuple[float, float]] = {}
for city_name, coords in PRESET_GEOCODE_COORDS.items():
    key = _normalize_city_key(city_name)
    if key:
        GEOCODE_CACHE[key] = coords

def geocode_city(city: str, retries=3):
    cache_key = _normalize_city_key(city)
    if not cache_key:
        return None, None

    if cache_key in GEOCODE_CACHE:
        lat, lng = GEOCODE_CACHE[cache_key]
        print(f"[GEOCODE] Cache hit for {city} → {lat}, {lng}")
        return lat, lng

    query = re.sub(r"\s+", " ", city.strip())
    query_variants = [query]
    if ", usa" not in cache_key:
        query_variants.append(f"{query}, USA")

    for attempt in range(retries):
        if attempt > 0:
            time.sleep(2 * attempt)
        try:
            active_queries = query_variants if attempt == retries - 1 else query_variants[:1]
            for candidate in active_queries:
                location = geolocator.geocode(candidate, timeout=10, country_codes="us")
                if location:
                    coords = (float(location.latitude), float(location.longitude))
                    GEOCODE_CACHE[cache_key] = coords
                    print(f"[GEOCODE] {city} → {coords[0]}, {coords[1]}")
                    return coords
        except Exception as e:
            print(f"[GEOCODE] Attempt {attempt+1} failed for {city}: {e}")
    print(f"[GEOCODE] All attempts failed for {city}, returning None")
    return None, None

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
    base_query = db.query(Load)

    if equipment_type:
        base_query = base_query.filter(Load.equipment_type.ilike(f"%{equipment_type}%"))
    if pickup_date:
        base_query = base_query.filter(Load.pickup_datetime >= pickup_date)

    origin_city = origin.split(",")[0].strip() if origin else None
    origin_state = origin.split(",")[1].strip() if origin and "," in origin else None
    destination_city = destination.split(",")[0].strip() if destination else None
    destination_state = destination.split(",")[1].strip() if destination and "," in destination else None

    # Strategy 1: Match full origin and full destination
    query = base_query
    if origin:
        query = query.filter(Load.origin.ilike(f"%{origin}%"))
    if destination:
        query = query.filter(Load.destination.ilike(f"%{destination}%"))
    results = query.limit(3).all()

    # Strategy 2: Origin city + destination state
    if not results and (origin_city or destination_state):
        query = base_query
        if origin_city:
            query = query.filter(Load.origin.ilike(f"%{origin_city}%"))
        if destination_state:
            query = query.filter(Load.destination.ilike(f"%{destination_state}%"))
        results = query.limit(3).all()

    # Strategy 3: Origin state + destination city
    if not results and (origin_state or destination_city):
        query = base_query
        if origin_state:
            query = query.filter(Load.origin.ilike(f"%{origin_state}%"))
        if destination_city:
            query = query.filter(Load.destination.ilike(f"%{destination_city}%"))
        results = query.limit(3).all()

    # Strategy 4: Origin state + destination state
    if not results and (origin_state or destination_state):
        query = base_query
        if origin_state:
            query = query.filter(Load.origin.ilike(f"%{origin_state}%"))
        if destination_state:
            query = query.filter(Load.destination.ilike(f"%{destination_state}%"))
        results = query.limit(3).all()

    total = len(results)

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

    backup_call_id = f"call_{int(datetime.utcnow().timestamp())}"

    # Save call record
    call = Call(
        call_id=request.get("call_id") or backup_call_id,
        mc_number=request.get("mc_number"),
        carrier_name=request.get("carrier_name"),
        duration_seconds=int(request.get("duration_seconds") or 0),
        outcome=request.get("outcome"),
        sentiment=request.get("sentiment"),
        negotiation_rounds=int(request.get("negotiation_rounds", 0) or 0),
        transcription=request.get("transcription", " "),
        caller_name=request.get("caller_name", "Unknown")
    )
    db.add(call)
    db.flush()  # Flush to get call_id if it was generated

    # If booked, save booking record
    if request.get("outcome") == "booked" and request.get("load_id"):

        load = db.query(Load).filter(Load.load_id == request.get("load_id")).first()
        if not load:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid load_id for booked call: {request.get('load_id')}"
            )

        origin_lat, origin_lng = geocode_city(load.origin)
        dest_lat, dest_lng = geocode_city(load.destination)

        booking = Booking(
            call_id=request.get("call_id") or backup_call_id,
            load_id=request.get("load_id") or None,
            mc_number=request.get("mc_number"),
            agreed_rate=float(request.get("final_rate") or 0),
            loadboard_rate=float(request.get("loadboard_rate", 0)),
            negotiation_rounds=int(request.get("negotiation_rounds") or 0),
            origin = load.origin,
            destination = load.destination,
            origin_lat = origin_lat,
            origin_lng = origin_lng,
            destination_lat = dest_lat,
            destination_lng = dest_lng
        )

        # Calculate margin
        if booking.loadboard_rate and booking.agreed_rate:
            booking.margin_percentage = round(
                ((float(load.true_cost) - float(booking.agreed_rate)) / float(load.true_cost)) * 100, 2)
        db.add(booking)

        # Update the load's status to "booked"
        load = db.query(Load).filter(Load.load_id == request.get("load_id")).first()
        if load:
            load.status = "booked"

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


# ── Dashboard Endpoints ──────────────────────────────────────────────

@app.get("/api/v1/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db), _auth: bool = Depends(verify_api_key)):
    total_calls = db.query(Call).count()
    total_bookings = db.query(Booking).count()
    booking_rate = round((total_bookings / total_calls * 100), 2) if total_calls > 0 else 0

    avg_efficiency = db.query(func.avg(
        (Booking.agreed_rate / Booking.loadboard_rate) * 100
    )).scalar() or 0

    avg_duration = db.query(func.avg(Call.duration_seconds)).filter(
        Call.outcome == "booked"
    ).scalar() or 0

    # Avg Premium Over Loadboard: (agreed - loadboard) / loadboard * 100
    avg_premium = db.query(func.avg(
        (Booking.agreed_rate - Booking.loadboard_rate) / Booking.loadboard_rate * 100
    )).filter(Booking.loadboard_rate > 0).scalar() or 0

    # Total Revenue Booked: sum of agreed_rate for all bookings
    total_revenue_booked = db.query(func.sum(Booking.agreed_rate)).scalar() or 0

    return {
        "total_calls": total_calls,
        "booking_rate": round(float(booking_rate), 2),
        "avg_rate_efficiency": round(float(avg_efficiency), 2),
        "avg_duration_seconds": round(float(avg_duration), 1),
        "avg_premium_over_loadboard": round(float(avg_premium), 2),
        "total_revenue_booked": round(float(total_revenue_booked), 2),
        "total_bookings_count": total_bookings,
    }


@app.get("/api/v1/dashboard/charts")
def dashboard_charts(db: Session = Depends(get_db), _auth: bool = Depends(verify_api_key)):
    # Volume by day
    volume_rows = (
        db.query(cast(Call.created_at, Date).label("day"), func.count(Call.id))
        .group_by("day")
        .order_by("day")
        .all()
    )
    volume_by_day = [{"date": str(d), "count": c} for d, c in volume_rows]

    # Outcome breakdown
    outcome_rows = db.query(Call.outcome, func.count(Call.id)).group_by(Call.outcome).all()
    outcome_breakdown = [{"outcome": o or "unknown", "count": c} for o, c in outcome_rows]

    # Funnel
    total = db.query(Call).count()
    verified = db.query(Call).filter(Call.outcome != "unverified").count()
    load_matched = db.query(Call).filter(Call.outcome.in_(["booked", "no_deal_rate"])).count()
    negotiation = db.query(Call).filter(
        Call.outcome.in_(["booked", "no_deal_rate"]),
        Call.negotiation_rounds > 0
    ).count()
    booked = db.query(Call).filter(Call.outcome == "booked").count()
    funnel = [
        {"stage": "Calls Received", "count": total},
        {"stage": "Verified", "count": verified},
        {"stage": "Load Matched", "count": load_matched},
        {"stage": "Negotiation", "count": negotiation},
        {"stage": "Booked", "count": booked},
    ]

    # Negotiation Premium Distribution: (agreed - loadboard) / loadboard * 100
    bookings = db.query(Booking.agreed_rate, Booking.loadboard_rate).all()
    premium_buckets = {"0-2": 0, "2-4": 0, "4-6": 0, "6-8": 0, "8-10": 0, "10-12": 0, "12+": 0}
    for agreed, loadboard in bookings:
        if loadboard and float(loadboard) > 0:
            premium = (float(agreed) - float(loadboard)) / float(loadboard) * 100
            if premium < 0:
                premium = 0
            if premium >= 12:
                premium_buckets["12+"] += 1
            else:
                bucket_start = int(premium // 2) * 2
                label = f"{bucket_start}-{bucket_start+2}"
                if label in premium_buckets:
                    premium_buckets[label] += 1
    negotiation_premium_distribution = [
        {"bucket": f"{k}%", "count": v, "start": int(k.split("-")[0]) if "-" in k else 12}
        for k, v in premium_buckets.items()
    ]

    # Sentiment breakdown by outcome
    sentiment_rows = (
        db.query(Call.outcome, Call.sentiment, func.count(Call.id))
        .group_by(Call.outcome, Call.sentiment)
        .all()
    )
    sentiment_map = {}
    for outcome, sentiment, count in sentiment_rows:
        o = outcome or "unknown"
        if o not in sentiment_map:
            sentiment_map[o] = {"outcome": o, "positive": 0, "neutral": 0, "negative": 0}
        sentiment_map[o][sentiment or "neutral"] = count
    sentiment_breakdown = list(sentiment_map.values())

    return {
        "volume_by_day": volume_by_day,
        "outcome_breakdown": outcome_breakdown,
        "funnel": funnel,
        "negotiation_premium_distribution": negotiation_premium_distribution,
        "sentiment_breakdown": sentiment_breakdown,
    }


@app.get("/api/v1/dashboard/calls")
def dashboard_calls(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    outcome: Optional[str] = None,
    sentiment: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    _auth: bool = Depends(verify_api_key),
):
    query = db.query(Call)

    if outcome and outcome != "all":
        query = query.filter(Call.outcome == outcome)
    if sentiment and sentiment != "all":
        query = query.filter(Call.sentiment == sentiment)
    if search:
        query = query.filter(
            (Call.carrier_name.ilike(f"%{search}%")) | (Call.mc_number.ilike(f"%{search}%"))
        )

    total = query.count()
    calls = query.order_by(Call.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    results = []
    for c in calls:
        booking = db.query(Booking).filter(Booking.call_id == c.call_id).first()
        load = None
        if booking:
            load = db.query(Load).filter(Load.load_id == booking.load_id).first()

        results.append({
            "call_id": c.call_id,
            "carrier_name": c.carrier_name,
            "mc_number": c.mc_number,
            "duration_seconds": c.duration_seconds,
            "outcome": c.outcome,
            "sentiment": c.sentiment,
            "negotiation_rounds": c.negotiation_rounds,
            "transcription": c.transcription,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "load_id": booking.load_id if booking else None,
            "lane": f"{load.origin} → {load.destination}" if load else None,
            "loadboard_rate": float(booking.loadboard_rate) if booking else None,
            "agreed_rate": float(booking.agreed_rate) if booking else None,
        })

    return {
        "calls": results,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
    }


@app.get("/api/v1/dashboard/loads/map")
def dashboard_loads_map(db: Session = Depends(get_db), _auth: bool = Depends(verify_api_key)):
    bookings = db.query(Booking).filter(
        Booking.origin_lat.isnot(None),
        Booking.origin_lng.isnot(None),
        Booking.destination_lat.isnot(None),
        Booking.destination_lng.isnot(None),
    ).all()

    return [
        {
            "load_id": b.load_id,
            "origin": b.origin,
            "destination": b.destination,
            "origin_lat": float(b.origin_lat),
            "origin_lng": float(b.origin_lng),
            "destination_lat": float(b.destination_lat),
            "destination_lng": float(b.destination_lng),
            "agreed_rate": float(b.agreed_rate),
            "loadboard_rate": float(b.loadboard_rate),
            "margin_percentage": float(b.margin_percentage) if b.margin_percentage else 0,
        }
        for b in bookings
    ]


@app.get("/api/v1/dashboard/loads/detail")
def dashboard_loads_detail(db: Session = Depends(get_db), _auth: bool = Depends(verify_api_key)):
    bookings = db.query(Booking).all()
    results = []
    for b in bookings:
        call = db.query(Call).filter(Call.call_id == b.call_id).first()
        load = db.query(Load).filter(Load.load_id == b.load_id).first()
        revenue = float(load.true_cost) if load and load.true_cost is not None else None
        agreed = float(b.agreed_rate)
        margin = round(((revenue - agreed) / revenue) * 100, 2) if revenue and revenue > 0 else 0

        results.append({
            "load_id": b.load_id,
            "lane": f"{b.origin} → {b.destination}",
            "carrier_name": call.carrier_name if call else None,
            "mc_number": b.mc_number,
            "revenue": revenue,
            "loadboard_rate": float(b.loadboard_rate),
            "agreed_rate": agreed,
            "margin_percentage": margin,
            "miles": load.miles if load else None,
            "created_at": b.created_at.isoformat() if b.created_at else None,
        })
    return results


@app.get("/api/v1/dashboard/carriers")
def dashboard_carriers(db: Session = Depends(get_db), _auth: bool = Depends(verify_api_key)):
    carriers_raw = (
        db.query(
            Call.mc_number,
            Call.carrier_name,
            func.count(Call.id).label("total_calls"),
            func.sum(case((Call.outcome == "booked", 1), else_=0)).label("bookings"),
            func.avg(Call.negotiation_rounds).label("avg_rounds"),
            func.avg(Call.duration_seconds).label("avg_duration"),
            func.max(Call.created_at).label("last_call"),
        )
        .filter(
            Call.mc_number.isnot(None),
            Call.carrier_name.isnot(None),
            func.length(func.trim(Call.mc_number)) > 0,
            func.length(func.trim(Call.carrier_name)) > 0,
        )
        .group_by(Call.mc_number, Call.carrier_name)
        .all()
    )
    results = []
    for mc, name, total, bookings, avg_rounds, avg_dur, last_call in carriers_raw:
        acceptance_rate = round((bookings or 0) / total * 100, 1) if total > 0 else 0
        # Get avg margin for this carrier's bookings
        avg_margin = db.query(func.avg(Booking.margin_percentage)).filter(
            Booking.mc_number == mc
        ).scalar()
        results.append({
            "mc_number": mc,
            "carrier_name": name,
            "total_calls": total,
            "bookings": bookings or 0,
            "acceptance_rate": acceptance_rate,
            "avg_rounds": round(float(avg_rounds or 0), 1),
            "avg_duration": round(float(avg_dur or 0), 0),
            "avg_margin": round(float(avg_margin or 0), 2),
            "last_call": last_call.isoformat() if last_call else None,
            "friction": calculate_friction(avg_rounds or 0, acceptance_rate),
        })
    return results


@app.get("/api/v1/dashboard/carriers/{mc_number}")
def dashboard_carrier_detail(mc_number: str, db: Session = Depends(get_db), _auth: bool = Depends(verify_api_key)):
    calls = db.query(Call).filter(Call.mc_number == mc_number).order_by(Call.created_at.desc()).limit(10).all()
    if not calls:
        raise HTTPException(status_code=404, detail="Carrier not found")

    carrier_name = calls[0].carrier_name
    total = len(calls)
    all_calls = db.query(Call).filter(Call.mc_number == mc_number).all()
    total_all = len(all_calls)
    booked_count = sum(1 for c in all_calls if c.outcome == "booked")
    acceptance_rate = round(booked_count / total_all * 100, 1) if total_all > 0 else 0
    avg_duration = sum(c.duration_seconds or 0 for c in all_calls if c.outcome == "booked")
    booked_calls = [c for c in all_calls if c.outcome == "booked"]
    avg_dur = avg_duration / len(booked_calls) if booked_calls else 0
    avg_rounds = sum(c.negotiation_rounds or 0 for c in all_calls) / total_all if total_all > 0 else 0

    carrier_bookings = db.query(Booking).filter(Booking.mc_number == mc_number).all()
    avg_margin = (
        sum(float(b.margin_percentage or 0) for b in carrier_bookings) / len(carrier_bookings)
        if carrier_bookings else 0
    )

    avg_margin_dollars = 0.0
    if carrier_bookings:
        load_ids = list({b.load_id for b in carrier_bookings if b.load_id})
        loads = db.query(Load.load_id, Load.true_cost).filter(Load.load_id.in_(load_ids)).all() if load_ids else []
        true_cost_by_load_id = {load_id: float(true_cost) for load_id, true_cost in loads if true_cost is not None}
        margins = [
            (true_cost_by_load_id.get(b.load_id, 0) - float(b.agreed_rate or 0))
            for b in carrier_bookings
            if b.load_id in true_cost_by_load_id
        ]
        avg_margin_dollars = (sum(margins) / len(margins)) if margins else 0.0

    history = []
    for c in calls:
        booking = db.query(Booking).filter(Booking.call_id == c.call_id).first()
        history.append({
            "call_id": c.call_id,
            "load_id": booking.load_id if booking else None,
            "lane": f"{booking.origin} → {booking.destination}" if booking else None,
            "loadboard_rate": float(booking.loadboard_rate) if booking else None,
            "agreed_rate": float(booking.agreed_rate) if booking else None,
            "outcome": c.outcome,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        })

    return {
        "mc_number": mc_number,
        "carrier_name": carrier_name,
        "total_calls": total_all,
        "bookings": booked_count,
        "acceptance_rate": acceptance_rate,
        "avg_negotiation_time": round(avg_dur, 0),
        "avg_margin": round(float(avg_margin or 0), 2),
        "avg_margin_dollars": round(float(avg_margin_dollars or 0), 2),
        "friction": calculate_friction(avg_rounds, acceptance_rate),
        "history": history,
    }


# ── Serve Frontend ──────────────────────────────────────────────────
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"

if FRONTEND_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="static-assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        file_path = FRONTEND_DIR / full_path
        if full_path and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIR / "index.html")
