import random
import time
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from database import SessionLocal
from models import Call, Booking, Load
from loads_data import LOADS

geolocator = Nominatim(user_agent="acme_seed")

def geocode_city(city: dtr):
    try:
        location = geolocator.geocode(city)
        if location:
            return float(location.latitude), float(location.longitude)
    except GeocoderTimedOut:
        print(f"Geocoding timed out for {city}. Retrying...")
        return geocode_city(city)
    except Exception as e:
        print(f"Error geocoding {city}: {e}")
    return None, None

CARRIERS = [
    ("MC-482911", "Sunrise Transport LLC"),
    ("MC-391847", "Blue Ridge Hauling"),
    ("MC-284756", "Midway Freight Co"),
    ("MC-193847", "Lone Star Carriers"),
    ("MC-847291", "Great Lakes Logistics"),
    ("MC-573829", "Coastal Express Inc"),
    ("MC-629384", "Heartland Trucking"),
    ("MC-748291", "Apex Freight Solutions"),
    ("MC-918273", "Swift Arrow Logistics"),
    ("MC-364729", "Iron Road Transport"),
    ("MC-556612", "Prairie Wind Carriers"),
    ("MC-771234", "Redwood Freight Inc"),
]

CALLER_NAMES = ["Mike", "James", "Carlos", "Dave", "Rick", "Tom", "Luis", "Steve", "Brian", "Jason"]

OUTCOMES = ["booked", "no_deal_rate", "no_deal_no_load", "unverified", "error_escalation"]
OUTCOME_WEIGHTS = [40, 25, 15, 12, 8]

SENTIMENTS = ["positive", "neutral", "negative"]
SENTIMENT_WEIGHTS = [55, 30, 15]

TRANSCRIPTS = {
    "booked": [
        "Alex: Hey, thanks for calling ACME Logistics! Can I get your name?\nCaller: Yeah it's Mike.\nAlex: Hey Mike! Can I get your MC number?\nCaller: MC 4 8 2 9 1 1.\nAlex: Got it — 4, 8, 2, 9, 1, 1. Is that right?\nCaller: Correct.\nAlex: Perfect, one moment. Great — and you're calling from Sunrise Transport LLC, is that right?\nCaller: Yep.\nAlex: Awesome. Where are you empty and looking to pick up?\nCaller: Chicago.\nAlex: Chicago, Illinois — and where are you looking to go?\nCaller: Dallas.\nAlex: Any specific part of Dallas?\nCaller: Dallas is fine.\nAlex: Got it. What equipment are you running?\nCaller: Dry van, fifty-three foot.\nAlex: And when are you available?\nCaller: Tomorrow morning.\nAlex: Let me check what we've got. I have a Dry Van load from Chicago, Illinois to Dallas, Texas. Pickup tomorrow morning, thirty-five thousand pounds of electronics. We're at twenty-five hundred dollars — does that work?\nCaller: Can you do twenty-seven hundred?\nAlex: I can work with you a little — how about twenty-six hundred?\nCaller: Deal.\nAlex: Perfect — Chicago to Dallas, Dry Van, twenty-six hundred dollars. Let me get you over to our team to lock this in.",
        "Alex: Thanks for calling ACME Logistics, can I get your name?\nCaller: James.\nAlex: Hey James! MC number?\nCaller: Three nine one eight four seven.\nAlex: Got it — 3, 9, 1, 8, 4, 7. Correct?\nCaller: That's it.\nAlex: One moment. Great, you're with Blue Ridge Hauling — is that right?\nCaller: Yes sir.\nAlex: Where are you looking to pick up?\nCaller: Atlanta, Georgia.\nAlex: And where are you headed?\nCaller: Miami.\nAlex: What equipment?\nCaller: Reefer.\nAlex: When are you available?\nCaller: Today afternoon.\nAlex: I've got a refrigerated load Atlanta to Miami, twenty-eight thousand pounds of produce, eighteen hundred dollars. Work for you?\nCaller: Yeah that works.\nAlex: Perfect — let me get you to our team to finalize.",
    ],
    "no_deal_rate": [
        "Alex: Thanks for calling ACME Logistics! Can I get your name?\nCaller: Dave.\nAlex: Hey Dave! MC number?\nCaller: Two eight four seven five six.\nAlex: Got it — 2, 8, 4, 7, 5, 6. Right?\nCaller: Yes.\nAlex: One moment. Great, you're with Midway Freight Co — correct?\nCaller: That's right.\nAlex: Where are you looking to pick up?\nCaller: Los Angeles.\nAlex: And going to?\nCaller: Phoenix.\nAlex: Equipment?\nCaller: Flatbed.\nAlex: Pickup timing?\nCaller: Tomorrow.\nAlex: I've got a Flatbed load LA to Phoenix, twelve hundred dollars.\nCaller: I need at least sixteen hundred on that lane.\nAlex: I can go to thirteen fifty.\nCaller: Nope, sixteen hundred or I'm moving on.\nAlex: Best I can do is thirteen fifty — I'm not able to get to sixteen hundred on this one.\nCaller: Then we're done. Thanks anyway.\nAlex: Understood — I'll keep you in mind for future loads. Safe travels.",
    ],
    "no_deal_no_load": [
        "Alex: Thanks for calling ACME Logistics! Can I get your name?\nCaller: Rick.\nAlex: Hey Rick! MC number?\nCaller: Eight four seven two nine one.\nAlex: 8, 4, 7, 2, 9, 1 — correct?\nCaller: Yep.\nAlex: One moment. Great, you're with Great Lakes Logistics?\nCaller: That's us.\nAlex: Where are you empty?\nCaller: Fargo, North Dakota.\nAlex: And where are you looking to go?\nCaller: Seattle.\nAlex: Equipment?\nCaller: Dry Van.\nAlex: When are you available?\nCaller: Today.\nAlex: Let me check — unfortunately I don't have anything matching that lane right now. Things change fast though — worth calling back later today.\nCaller: Alright, thanks.\nAlex: Thanks for calling, safe travels.",
    ],
    "unverified": [
        "Alex: Thanks for calling ACME Logistics! Can I get your name?\nCaller: Tom.\nAlex: Hey Tom! MC number?\nCaller: One two three four five six.\nAlex: 1, 2, 3, 4, 5, 6 — is that right?\nCaller: Yes.\nAlex: One moment while I look that up. I'm sorry Tom — it looks like we're not able to process loads with your carrier profile at this time. You may want to check your authority status with the FMCSA. I hope we can work together in the future.\nCaller: Oh okay, I'll check on that.\nAlex: Thanks for calling.",
    ],
    "error_escalation": [
        "Alex: Thanks for calling ACME Logistics! Can I get your name?\nCaller: Carlos.\nAlex: Hey Carlos! MC number?\nCaller: Five seven three eight two nine.\nAlex: 5, 7, 3, 8, 2, 9 — correct?\nCaller: That's right.\nAlex: Bear with me one moment. I'm running into a technical issue on my end — let me get you to someone on our team who can help.\nCaller: Sure.\nAlex: Connecting you now.",
    ],
}

def seed_calls(n=60):
    db = SessionLocal()
    
    # Load all loads from DB
    loads = db.query(Load).all()
    if not loads:
        print("No loads found in database. Please seed loads before seeding calls.")
        db.close()
        return
    
    # Pre-geocode all unique cities to minimize geocoding calls
    print("Pre-geocoding cities...")
    geocache = {}
    unique_cities = set()
    for load in loads:
        unique_cities.add(load.origin)
        unique_cities.add(load.destination)
    
    for city in unique_cities:
        lat, lng = geocode_city(city)
        geocache[city] = (lat, lng)
        print(f"Geocoded {city}: {lat}, {lng}")
        time.sleep(1)  # To respect geocoding service rate limits

    print(f"Geocoded {len(unique_cities)} unique cities. Seeding {n} calls...")

    booked_load_ids = set()

    for i in range(n):
        mc, carrier = random.choice(CARRIERS)
        outcome = random.choices(OUTCOMES, weights=OUTCOME_WEIGHTS)[0]
        sentiment = random.choices(SENTIMENTS, weights=SENTIMENT_WEIGHTS)[0]

        created_at = datetime.utcnow() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23), minutes=random.randint(0, 59))

        call_id = f"call_{i+1:04d}"
        rounds = random.randint(1,3) if outcome == "booked" else random.randint(0,2)
        trasncript = random.choice(TRANSCRIPTS.get(outcome, TRANSCRIPTS['booked']))

        call = Call(
            call_id=call_id,
            mc_number=mc,
            carrier_name=carrier,
            caller_name=random.choice(CALLER_NAMES),
            duration_seconds=random.randint(60, 480),
            outcome=outcome,
            sentiment=sentiment,
            negotiation_rounds=rounds,
            transcription=trasncript,
            created_at=created_at
        )
        db.add(call)
        db.flush()

        if outcome == "booked":
            #Pick a random load that hasn't been booked yet
            available_loads = [l for l in loads if l.load_id not in booked_load_ids]
            if not available_loads:
                print("No more available loads to book.")
                db.commit()
                break

            load = random.choice(available_loads)
            booked_load_ids.add(load.load_id)

            loadboard_rate = float(load.loadboard_rate)
            agreed_rate = round(random.uniform(loadboard_rate, loadboard_rate * 1.12), 2)
            margin = round(((agreed_rate - loadboard_rate) / loadboard_rate) * 100, 2)

            origin_lat, origin_lng = geocache.get(load.origin, (None, None))
            dest_lat, dest_lng = geocache.get(load.destination, (None, None))

            booking = Booking(
                call_id=call_id,
                load_id=load.load_id,
                mc_number=mc,
                agreed_rate=agreed_rate,
                loadboard_rate=loadboard_rate,
                margin_percentage=margin,
                negotiation_rounds=rounds,
                origin=load.origin,
                destination=load.destination,
                origin_lat=origin_lat,
                origin_lng=origin_lng,
                destination_lat=dest_lat,
                destination_lng=dest_lng,
                created_at=created_at
            )
            db.add(booking)
        
        db.commit()
        print(f"Seeded call {i+1}/{n}with outcome '{outcome}'")
    
    db.close()
    print(f"\nDone. Seeded {n} calls.")

if __name__ == "__main__":
    seed_calls(60)

