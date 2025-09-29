from libsql.db import SessionLocal
from libsql import crud

import json
from pathlib import Path

def main():
    ROOT        = Path(__file__).resolve().parents[1]
    DUMP_PATH   = ROOT / "app" / "data" / "fighters.json"

    session = SessionLocal()
    data = {"fighters": crud.get_all_fighter_names(session)}

    with open(DUMP_PATH, "w+", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

if __name__ == "__main__":
    main()