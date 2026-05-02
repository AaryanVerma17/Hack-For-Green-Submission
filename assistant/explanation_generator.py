"""Generate simple natural-language risk explanations.

Updated to work with Pathway streaming functions.
"""
import os
from dotenv import load_dotenv

load_dotenv()
os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)

from __future__ import annotations


def generate_explanation_pathway(
    amount: float, 
    rolling_avg: float, 
    txn_count: int, 
    location_changed: bool
) -> str:
    """Generate explanation based on individual feature values.
    
    This version is designed to work with Pathway's pw.apply function.
    """
    reasons: list[str] = []
    
    if amount > rolling_avg * 3:
        reasons.append("transaction amount is much higher than the user's normal pattern")
    
    if txn_count >= 3:
        reasons.append("multiple transactions arrived in a short time window")
    
    if location_changed:
        reasons.append("transaction location changed compared to the previous event")
    
    if not reasons:
        return "Risk is low because no strong fraud signals were detected."
    
    return "Potential fraud flagged because " + ", ".join(reasons) + "."


def generate_explanation(transaction_data: dict) -> str:
    """Legacy function for backward compatibility."""
    reasons: list[str] = []

    if transaction_data.get("amount", 0) > transaction_data.get("rolling_avg_amount", 0) * 3:
        reasons.append("transaction amount is much higher than the user's normal pattern")

    if transaction_data.get("txn_count_in_window", 0) >= 3:
        reasons.append("multiple transactions arrived in a short time window")

    if transaction_data.get("location_changed"):
        reasons.append("transaction location changed compared to the previous event")

    if not reasons:
        return "Risk is low because no strong fraud signals were detected."

    return "Potential fraud flagged because " + ", ".join(reasons) + "."
