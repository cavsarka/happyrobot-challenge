import csv
from datetime import datetime
from pathlib import Path
from typing import Optional

from database import SessionLocal
from models import Call


DEFAULT_CSV_PATH = Path(__file__).resolve().parent / "seed_data" / "calls_rows.csv"


def _clean(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned if cleaned else None


def _to_int(value: Optional[str]) -> Optional[int]:
    cleaned = _clean(value)
    return int(cleaned) if cleaned is not None else None


def _to_datetime(value: Optional[str]) -> Optional[datetime]:
    cleaned = _clean(value)
    return datetime.fromisoformat(cleaned) if cleaned is not None else None


def seed_calls(csv_path: Optional[Path] = None) -> int:
    path = csv_path or DEFAULT_CSV_PATH
    db = SessionLocal()

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        inserted = 0
        for row in rows:
            call = Call(
                call_id=_clean(row.get("call_id")),
                mc_number=_clean(row.get("mc_number")),
                carrier_name=_clean(row.get("carrier_name")),
                caller_name=_clean(row.get("caller_name")),
                duration_seconds=_to_int(row.get("duration_seconds")),
                outcome=_clean(row.get("outcome")),
                sentiment=_clean(row.get("sentiment")),
                negotiation_rounds=_to_int(row.get("negotiation_rounds")) or 0,
                transcription=_clean(row.get("transcription")) or " ",
                created_at=_to_datetime(row.get("created_at")),
            )
            db.add(call)
            inserted += 1

        db.commit()
        print(f"Seeded {inserted} calls from {path.name}")
        return inserted
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_calls()
