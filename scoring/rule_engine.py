"""Rule-based scoring with Pathway transformations."""
import os
from dotenv import load_dotenv

load_dotenv()
os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)

from __future__ import annotations

import pathway as pw
from config.settings import LARGE_TXN_MULTIPLIER, RAPID_FIRE_TXN_COUNT


def apply_rule_scoring(table: pw.Table) -> pw.Table:
    """Apply rule-based fraud scoring with breakdown tracking."""
    
    # Detect triggers
    table = table.with_columns(
        triggered_large_amount=(
            pw.this.amount > (pw.this.rolling_avg_amount * LARGE_TXN_MULTIPLIER)
        ),
        triggered_rapid_fire=(
            pw.this.txn_count_in_window >= RAPID_FIRE_TXN_COUNT
        ),
        triggered_location_change=pw.this.location_changed,
    )
    
    # Calculate risk score
    table = table.with_columns(
        large_score=pw.if_else(pw.this.triggered_large_amount, 0.5, 0.0),
        rapid_score=pw.if_else(pw.this.triggered_rapid_fire, 0.3, 0.0),
        location_score=pw.if_else(pw.this.triggered_location_change, 0.25, 0.0),
    )
    
    table = table.with_columns(
        risk_score=pw.this.large_score + pw.this.rapid_score + pw.this.location_score
    )
    
    # Add explanation
    table = table.with_columns(
        explanation=pw.apply(
            lambda large, rapid, location: (
                "Potential fraud flagged because " + 
                ", ".join([
                    reason for reason, triggered in [
                        ("transaction amount is much higher than normal", large),
                        ("multiple rapid transactions detected", rapid),
                        ("location changed from previous transaction", location),
                    ] if triggered
                ]) + "." if any([large, rapid, location]) else "Low risk - no strong signals"
            ),
            pw.this.triggered_large_amount,
            pw.this.triggered_rapid_fire,
            pw.this.triggered_location_change,
        )
    )
    
    return table
