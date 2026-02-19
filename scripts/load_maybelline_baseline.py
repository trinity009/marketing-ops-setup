#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.database import Base, SessionLocal, engine
from backend.app.seed_data import bootstrap_maybelline_baseline


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        result = bootstrap_maybelline_baseline(db)
    finally:
        db.close()
    print(result)


if __name__ == "__main__":
    main()
