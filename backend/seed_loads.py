# seed.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database import Base, engine, SessionLocal
from models import Load, Call, Booking
from loads_data import LOADS
from datetime import datetime

def seed_loads(reseed=False):

    # Seed loads data
    db = SessionLocal()
    try:
        existing = db.query(Load).count()

        if reseed and existing > 0:
            print(f"Clearing {existing} existing loads...")
            db.query(Load).delete()
            db.commit()
            existing = 0

        if existing > 0:
            print(f"Loads table already has {existing} records. Skipping seed.")
            return

        print("Seeding loads data...")
        for load_data in LOADS:
            load = Load(
                load_id=load_data["load_id"],
                origin=load_data["origin"],
                destination=load_data["destination"],
                pickup_datetime=datetime.fromisoformat(load_data["pickup_datetime"]),
                delivery_datetime=datetime.fromisoformat(load_data["delivery_datetime"]),
                equipment_type=load_data["equipment_type"],
                loadboard_rate=load_data["loadboard_rate"],
                notes=load_data.get("notes"),
                weight=load_data.get("weight"),
                commodity_type=load_data.get("commodity_type"),
                num_of_pieces=load_data.get("num_of_pieces"),
                miles=load_data.get("miles"),
                dimensions=load_data.get("dimensions"),
                status="available"
            )
            db.add(load)

        db.commit()
        print(f"Seeded {len(LOADS)} loads successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    reseed = "--reseed" in sys.argv
    seed(reseed=reseed)
