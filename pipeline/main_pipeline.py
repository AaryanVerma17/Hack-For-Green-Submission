from __future__ import annotations
"""Main Pathway streaming pipeline.

Demonstrates:
- Continuous data ingestion (auto-detects new CSV rows)
- Stateful transformations (per-user aggregations)  
- Incremental computation (Pathway reducers)
- Continuous output (CSV updates automatically)
"""
import os
from dotenv import load_dotenv

load_dotenv()
os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pathway as pw
from ingestion.stream_ingestion import create_streaming_source
from features.feature_engineering import add_features
from scoring.rule_engine import apply_rule_scoring
from config.settings import STREAM_FILE_PATH, RISK_THRESHOLD
from utils.logger import get_logger

logger = get_logger(__name__)


def run_pipeline() -> None:
    """Run the Pathway streaming fraud detection pipeline.
    
    This pipeline:
    1. Streams data from CSV (auto-detects new rows)
    2. Applies stateful feature engineering
    3. Scores transactions with rule engine
    4. Outputs results continuously
    
    No restart needed when new data arrives!
    """
    
    logger.info("=" * 60)
    logger.info("PATHWAY STREAMING FRAUD DETECTION PIPELINE")
    logger.info("=" * 60)
    
    # Step 1: Create streaming source (MANDATORY: streaming ingestion)
    logger.info("📥 Setting up streaming CSV connector...")
    raw_stream = create_streaming_source(STREAM_FILE_PATH)
    logger.info("✓ Streaming ingestion configured")
    logger.info("  • Mode: streaming")
    logger.info("  • Auto-commit: 500ms")
    logger.info("  • File: %s", STREAM_FILE_PATH)
    
    # Step 2: Feature engineering (MANDATORY: Pathway transformations)
    logger.info("\n🔧 Configuring feature engineering...")
    enriched = add_features(raw_stream)
    logger.info("✓ Stateful feature computation configured")
    logger.info("  • Rolling averages per user")
    logger.info("  • Transaction counts (incremental)")
    logger.info("  • Location change detection")
    
    # Step 3: Risk scoring (MANDATORY: streaming transformations)
    logger.info("\n🎯 Configuring risk scoring engine...")
    scored = apply_rule_scoring(enriched)
    logger.info("✓ Rule-based scoring configured")
    logger.info("  • Large amount detection")
    logger.info("  • Rapid fire detection")
    logger.info("  • Location anomalies")
    
    # Step 4: Filter high-risk alerts
    logger.info("\n🚨 Configuring alert extraction...")
    alerts = scored.filter(pw.this.risk_score >= RISK_THRESHOLD)
    logger.info("✓ Alert filtering configured (threshold: %.2f)", RISK_THRESHOLD)
    
    # Step 5: Continuous output (MANDATORY: auto-updating output)
    logger.info("\n📤 Setting up continuous output streams...")
    
    # Output all scored transactions for dashboard
    pw.io.csv.write(scored, "data/scored_transactions.csv")
    logger.info("✓ Scored transactions → data/scored_transactions.csv")
    
    # Output high-risk alerts
    pw.io.csv.write(alerts, "data/alerts.csv")
    logger.info("✓ High-risk alerts → data/alerts.csv")
    
    # Step 6: Run continuously (MANDATORY: continuous execution)
    logger.info("\n" + "=" * 60)
    logger.info("🚀 STARTING CONTINUOUS PROCESSING")
    logger.info("=" * 60)
    logger.info("Pipeline is now running...")
    logger.info("• New transactions will be processed automatically")
    logger.info("• Output files update in real-time")
    logger.info("• Dashboard will show live updates")
    logger.info("• Press Ctrl+C to stop")
    logger.info("=" * 60 + "\n")
    
    # Run the Pathway computation graph
    pw.run()


if __name__ == "__main__":
    try:
        run_pipeline()
    except KeyboardInterrupt:
        logger.info("\n\n⏹️  Pipeline stopped by user")
    except Exception as e:
        logger.error("❌ Pipeline error: %s", e, exc_info=True)
        raise
