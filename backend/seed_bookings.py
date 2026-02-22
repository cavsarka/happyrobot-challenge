import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional

from database import SessionLocal
from models import Booking


DEFAULT_CSV_PATH = Path(__file__).resolve().parent / "seed_data" / "bookings_rows.csv"


def _clean(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned if cleaned else None


def _to_int(value: Optional[str]) -> Optional[int]:
    cleaned = _clean(value)
    return int(cleaned) if cleaned is not None else None


def _to_decimal(value: Optional[str]) -> Optional[Decimal]:
    cleaned = _clean(value)
    return Decimal(cleaned) if cleaned is not None else None


def _to_datetime(value: Optional[str]) -> Optional[datetime]:
    cleaned = _clean(value)
    return datetime.fromisoformat(cleaned) if cleaned is not None else None


def seed_bookings(csv_path: Optional[Path] = None) -> int:
    path = csv_path or DEFAULT_CSV_PATH
    db = SessionLocal()

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        inserted = 0
        for row in rows:
            booking = Booking(
                call_id=_clean(row.get("call_id")),
                load_id=_clean(row.get("load_id")),
                mc_number=_clean(row.get("mc_number")) or "",
                agreed_rate=_to_decimal(row.get("agreed_rate")) or Decimal("0"),
                loadboard_rate=_to_decimal(row.get("loadboard_rate")) or Decimal("0"),
                margin_percentage=_to_decimal(row.get("margin_percentage")),
                negotiation_rounds=_to_int(row.get("negotiation_rounds")) or 0,
                origin=_clean(row.get("origin")) or "",
                destination=_clean(row.get("destination")) or "",
                origin_lat=_to_decimal(row.get("origin_lat")),
                origin_lng=_to_decimal(row.get("origin_lng")),
                destination_lat=_to_decimal(row.get("destination_lat")),
                destination_lng=_to_decimal(row.get("destination_lng")),
                created_at=_to_datetime(row.get("created_at")),
            )
            db.add(booking)
            inserted += 1

        db.commit()
        print(f"Seeded {inserted} bookings from {path.name}")
        return inserted
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_bookings()
