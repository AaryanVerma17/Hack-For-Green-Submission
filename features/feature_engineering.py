"""Feature engineering with Pathway transformations.

Uses Pathway's groupby and reduce for stateful incremental computation.
"""
import os
from dotenv import load_dotenv

load_dotenv()
os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)

from __future__ import annotations

import pathway as pw


# feature_engineering.py
def add_features(table: pw.Table) -> pw.Table:
    """
    Add fraud detection features using Pathway operations.

    This demonstrates:
    - Stateful computation (per-user aggregations)
    - Incremental updates (reducers update as new data arrives)
    - Window-based operations (implicit in groupby)
    """

    table = table.select(
        transaction_id=pw.this.transaction_id,
        user_id=pw.this.user_id,
        amount=pw.cast(float, pw.this.amount),
        currency=pw.this.currency,
        location=pw.this.location,
        merchant=pw.this.merchant,
        timestamp=pw.this.timestamp,
    )

    # Per-user stateful aggregations
    user_aggregates = table.groupby(pw.this.user_id).reduce(
        pw.this.user_id,
        rolling_avg_amount=pw.reducers.avg(pw.this.amount),
        txn_count_in_window=pw.reducers.count(),
    )

    enriched = table.join(
        user_aggregates,
        pw.left.user_id == pw.right.user_id,
    ).select(
        transaction_id=pw.left.transaction_id,
        user_id=pw.left.user_id,
        amount=pw.left.amount,
        currency=pw.left.currency,
        location=pw.left.location,
        merchant=pw.left.merchant,
        timestamp=pw.left.timestamp,
        rolling_avg_amount=pw.right.rolling_avg_amount,
        txn_count_in_window=pw.right.txn_count_in_window,
    )

    # Add previous location and timestamp
    prev_location = (
        table
        .select(
            user_id=pw.this.user_id,
            timestamp=pw.this.timestamp,
            location=pw.this.location,
        )
        .groupby(pw.this.user_id)
        .reduce(
            pw.this.user_id,
            prev_location=pw.reducers.last(pw.this.location, order_by=pw.this.timestamp, skip=1),
            prev_timestamp=pw.reducers.last(pw.this.timestamp, order_by=pw.this.timestamp, skip=1),
        )
    )

    enriched = enriched.join(
        prev_location,
        pw.left.user_id == pw.right.user_id,
        how="left"
    ).select(
        **{col: getattr(pw.left, col) for col in enriched.schema.keys()},
        prev_location=pw.right.prev_location,
        prev_timestamp=pw.right.prev_timestamp,
    )

    # Compute location_changed
    enriched = enriched.with_columns(
        location_changed=(pw.this.location != pw.this.prev_location) & (pw.this.prev_location.is_not_none())
    )

    return enriched