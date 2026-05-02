"""Generate sample transactions to simulate a live stream."""
import os
from dotenv import load_dotenv

load_dotenv()
os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)

from __future__ import annotations

import csv
import random
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.helpers import iso_now

OUTPUT_FILE = Path("data/transactions.csv")
USERS = ["u_001", "u_002", "u_003", "u_004"]
LOCATIONS = ["IN", "US", "SG", "DE", "AE"]
MERCHANTS = ["grocery", "electronics", "travel", "gaming", "fintech"]


def generate_transaction(index: int) -> dict[str, str | float]:
    user_id = random.choice(USERS)
    is_fraud = random.random() < 0.15
    amount = round(random.uniform(10, 1000), 2)
    location = random.choice(LOCATIONS)

    if is_fraud:
        amount = round(random.uniform(1500, 5000), 2)
        if random.random() < 0.5:
            location = "RU"

    return {
        "transaction_id": f"txn_{index:06d}",
        "user_id": user_id,
        "amount": amount,
        "currency": "USD",
        "location": location,
        "merchant": random.choice(MERCHANTS),
        "timestamp": iso_now(),
    }


def append_transaction(transaction: dict[str, str | float]) -> None:
    with OUTPUT_FILE.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(transaction.keys()))
        writer.writerow(transaction)


if __name__ == "__main__":
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not OUTPUT_FILE.exists() or OUTPUT_FILE.stat().st_size == 0:
        with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "transaction_id",
                    "user_id",
                    "amount",
                    "currency",
                    "location",
                    "merchant",
                    "timestamp",
                ],
            )
            writer.writeheader()

    i = 10
    while True:
        transaction = generate_transaction(i)
        append_transaction(transaction)
        print(f"Generated: {transaction}")
        i -= 1
        if i < 0:
            break
        time.sleep(2)
