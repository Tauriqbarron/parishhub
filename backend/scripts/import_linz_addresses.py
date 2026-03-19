#!/usr/bin/env python3
"""Import LINZ NZ Addresses dataset into the nz_addresses table.

Usage:
    # From a local CSV file:
    python scripts/import_linz_addresses.py /path/to/nz-addresses.csv

    # Download from LINZ Data Service (requires LINZ_API_KEY env var):
    python scripts/import_linz_addresses.py --download

Download the CSV manually from:
    https://data.linz.govt.nz/layer/105689-nz-addresses/
    Export as CSV, select columns:
    address_id, full_address, full_address_ascii, address_number,
    road_name, road_type_name, suburb_locality, town_city, postcode
"""

import argparse
import csv
import os
import sys
import time
from pathlib import Path

# Add backend to path so we can import app modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text

from app.database import SessionLocal

LINZ_LAYER_ID = 105689
BATCH_SIZE = 10000

# Column mapping: CSV column name -> DB column name
COLUMN_MAP = {
    "address_id": "id",
    "full_address": "full_address",
    "full_address_ascii": "full_address_ascii",
    "address_number": "address_number",
    "road_name": "road_name",
    "road_type_name": "road_type_name",
    "suburb_locality": "suburb_locality",
    "town_city": "town_city",
    "postcode": "postcode",
}


def download_csv(api_key: str) -> str:
    """Download the LINZ NZ Addresses CSV and return the file path."""
    import urllib.request

    print("Requesting export from LINZ Data Service...")
    url = (
        f"https://data.linz.govt.nz/services/api/v1/exports/"
        f"?key={api_key}&layer={LINZ_LAYER_ID}&format=csv"
    )

    req = urllib.request.Request(url, method="POST")
    req.add_header("Content-Type", "application/json")

    # Request only the columns we need
    body = (
        '{"items": [{"item": "' + str(LINZ_LAYER_ID) + '"}], '
        '"crs": "EPSG:4326", "format": "text/csv"}'
    )
    req.data = body.encode()

    print("NOTE: LINZ exports can take several minutes for the full dataset.")
    print(
        "For faster setup, download the CSV manually from "
        "https://data.linz.govt.nz/layer/105689-nz-addresses/ "
        "and run: python scripts/import_linz_addresses.py /path/to/file.csv"
    )

    # For now, just provide instructions - the LINZ export API is async
    # and requires polling. Manual download is more reliable.
    raise SystemExit(
        "\nAutomatic download not yet implemented. "
        "Please download the CSV manually from:\n"
        "  https://data.linz.govt.nz/layer/105689-nz-addresses/\n"
        "Then run:\n"
        "  python scripts/import_linz_addresses.py /path/to/nz-addresses.csv"
    )


def normalize_csv_headers(headers: list[str]) -> dict[str, int]:
    """Map CSV headers to column indices, handling LINZ column name variations."""
    header_map = {}
    for i, h in enumerate(headers):
        # Normalize: lowercase, strip whitespace, remove quotes
        clean = h.strip().lower().strip('"').strip("'")
        # Handle common LINZ variations
        if clean in ("address_id", "id", "gid"):
            header_map["address_id"] = i
        elif clean == "full_address":
            header_map["full_address"] = i
        elif clean in ("full_address_ascii", "full_address_ascii_for_sorting"):
            header_map["full_address_ascii"] = i
        elif clean in ("address_number", "address_number_high", "unit_value"):
            if "address_number" not in header_map:
                header_map["address_number"] = i
        elif clean in ("road_name", "road_name_ascii"):
            if "road_name" not in header_map:
                header_map["road_name"] = i
        elif clean in ("road_type_name",):
            header_map["road_type_name"] = i
        elif clean in ("suburb_locality", "suburb_locality_ascii"):
            if "suburb_locality" not in header_map:
                header_map["suburb_locality"] = i
        elif clean in ("town_city", "town_city_ascii"):
            if "town_city" not in header_map:
                header_map["town_city"] = i
        elif clean in ("postcode",):
            header_map["postcode"] = i
    return header_map


def import_csv(csv_path: str) -> None:
    """Import a LINZ CSV file into the nz_addresses table."""
    db = SessionLocal()

    try:
        # Truncate existing data
        print("Clearing existing address data...")
        db.execute(text("TRUNCATE TABLE nz_addresses"))
        db.commit()

        print(f"Reading {csv_path}...")

        # Detect encoding - LINZ files are sometimes UTF-8 with BOM
        with open(csv_path, "rb") as f:
            raw = f.read(4)
        encoding = "utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"

        with open(csv_path, "r", encoding=encoding) as f:
            reader = csv.reader(f)
            headers = next(reader)
            header_map = normalize_csv_headers(headers)

            # Validate required columns
            required = ["address_id", "full_address"]
            missing = [c for c in required if c not in header_map]
            if missing:
                print(f"ERROR: Missing required columns: {missing}")
                print(f"Found columns: {list(header_map.keys())}")
                print(f"Raw headers: {headers}")
                sys.exit(1)

            print(f"Mapped columns: {list(header_map.keys())}")

            batch = []
            total = 0
            start = time.time()

            for row in reader:
                try:
                    addr_id = row[header_map["address_id"]].strip()
                    if not addr_id:
                        continue

                    record = {
                        "id": int(addr_id),
                        "full_address": row[header_map["full_address"]].strip(),
                    }

                    # Optional columns
                    for csv_col, db_col in COLUMN_MAP.items():
                        if csv_col in ("address_id", "full_address"):
                            continue
                        if csv_col in header_map:
                            val = row[header_map[csv_col]].strip()
                            record[db_col] = val if val else None
                        else:
                            record[db_col] = None

                    batch.append(record)

                    if len(batch) >= BATCH_SIZE:
                        db.execute(
                            text(
                                "INSERT INTO nz_addresses "
                                "(id, full_address, full_address_ascii, address_number, "
                                "road_name, road_type_name, suburb_locality, town_city, postcode) "
                                "VALUES (:id, :full_address, :full_address_ascii, :address_number, "
                                ":road_name, :road_type_name, :suburb_locality, :town_city, :postcode)"
                            ),
                            batch,
                        )
                        db.commit()
                        total += len(batch)
                        elapsed = time.time() - start
                        rate = total / elapsed if elapsed > 0 else 0
                        print(
                            f"  Imported {total:,} rows ({rate:,.0f} rows/sec)...",
                            end="\r",
                        )
                        batch = []

                except (ValueError, IndexError):
                    # Skip malformed rows
                    continue

            # Final batch
            if batch:
                db.execute(
                    text(
                        "INSERT INTO nz_addresses "
                        "(id, full_address, full_address_ascii, address_number, "
                        "road_name, road_type_name, suburb_locality, town_city, postcode) "
                        "VALUES (:id, :full_address, :full_address_ascii, :address_number, "
                        ":road_name, :road_type_name, :suburb_locality, :town_city, :postcode)"
                    ),
                    batch,
                )
                db.commit()
                total += len(batch)

        elapsed = time.time() - start
        print(f"\nImported {total:,} addresses in {elapsed:.1f}s")

        # Verify
        count = db.execute(text("SELECT COUNT(*) FROM nz_addresses")).scalar()
        print(f"Total rows in nz_addresses: {count:,}")

    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        description="Import LINZ NZ Addresses into the database"
    )
    parser.add_argument(
        "csv_file",
        nargs="?",
        help="Path to the LINZ NZ Addresses CSV file",
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Download from LINZ Data Service (requires LINZ_API_KEY env var)",
    )

    args = parser.parse_args()

    if args.download:
        api_key = os.environ.get("LINZ_API_KEY")
        if not api_key:
            print("ERROR: Set LINZ_API_KEY environment variable")
            print("Get a free API key at https://data.linz.govt.nz/")
            sys.exit(1)
        csv_path = download_csv(api_key)
    elif args.csv_file:
        csv_path = args.csv_file
        if not os.path.exists(csv_path):
            print(f"ERROR: File not found: {csv_path}")
            sys.exit(1)
    else:
        parser.print_help()
        print(
            "\nDownload the CSV from: "
            "https://data.linz.govt.nz/layer/105689-nz-addresses/"
        )
        sys.exit(1)

    import_csv(csv_path)


if __name__ == "__main__":
    main()
