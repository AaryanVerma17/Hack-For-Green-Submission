"""Pathway-based streaming ingestion with practical implementation.

Uses Pathway's CSV connector in streaming mode for automatic data updates.
"""
import os
from dotenv import load_dotenv

load_dotenv()
os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)

from __future__ import annotations

import pathway as pw


class TransactionSchema(pw.Schema):
    transaction_id: str
    user_id: str
    amount: str  # Will be converted to float in processing
    currency: str
    location: str
    merchant: str
    timestamp: str


def create_streaming_source(path: str) -> pw.Table:
    """Create a Pathway streaming data source.
    
    This uses Pathway's CSV reader in streaming mode with autocommit.
    New rows in the CSV are automatically detected and processed.
    """
    return pw.io.csv.read(
        path,
        schema=TransactionSchema,
        mode="streaming",
        autocommit_duration_ms=500,
    )
