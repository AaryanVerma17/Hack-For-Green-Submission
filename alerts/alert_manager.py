"""Alert creation and persistence for Pathway streaming.

Filters high-risk transactions and outputs them continuously.
"""
import os
from dotenv import load_dotenv

load_dotenv()
os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)

from __future__ import annotations

import pathway as pw
from config.settings import ALERTS_OUTPUT_PATH, RISK_THRESHOLD
from assistant.explanation_generator import generate_explanation_pathway


def extract_and_persist_alerts(table: pw.Table) -> pw.Table:
    """Filter high-risk transactions and prepare for output.
    
    Returns a table of alerts that can be written to CSV/JSONL continuously.
    """
    
    # Filter for high-risk transactions
    alerts = table.filter(pw.this.risk_score >= RISK_THRESHOLD)
    
    # Add explanation using Pathway's apply
    alerts = alerts.with_columns(
        explanation=pw.apply(
            generate_explanation_pathway,
            pw.this.amount,
            pw.this.rolling_avg_amount,
            pw.this.txn_count_in_window,
            pw.this.location_changed,
        )
    )
    
    # Select relevant columns for output
    alerts = alerts.select(
        pw.this.transaction_id,
        pw.this.user_id,
        pw.this.amount,
        pw.this.currency,
        pw.this.location,
        pw.this.merchant,
        pw.this.timestamp,
        pw.this.risk_score,
        pw.this.triggered_large_amount,
        pw.this.triggered_rapid_fire,
        pw.this.triggered_location_change,
        pw.this.breakdown_json,
        pw.this.explanation,
    )
    
    # Write alerts continuously to CSV
    pw.io.csv.write(alerts, ALERTS_OUTPUT_PATH)
    
    return alerts
