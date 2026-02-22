from pathlib import Path

from backend.database import engine
from backend.models import Base
from backend.seed_loads import seed_loads
from backend.seed_calls import seed_calls
from backend.seed_bookings import seed_bookings


SEED_DIR = Path(__file__).resolve().parent / "seed_data"


def reset_db() -> None:
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)

    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)

    print("Seeding loads...")
    load_count = seed_loads(SEED_DIR / "loads_rows.csv")

    print("Seeding calls...")
    call_count = seed_calls(SEED_DIR / "calls_rows.csv")

    print("Seeding bookings...")
    booking_count = seed_bookings(SEED_DIR / "bookings_rows.csv")

    print(
        f"Done. Seeded loads={load_count}, calls={call_count}, bookings={booking_count}"
    )


if __name__ == "__main__":
    reset_db()
