from __future__ import annotations
"""Enhanced Streamlit dashboard with real-time fraud detection visualizations.

Features:
1. Live Risk Score Meter (Gauge Chart)
2. Risk Score Breakdown Table (Feature Triggers)
3. Real-Time Fraud Trend Graph (Time Series)
"""
import os
from dotenv import load_dotenv

load_dotenv()
os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)

port = int(os.environ.get("PORT", 8501))
# ...existing code...

import json
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ...existing code...
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=2000, key="auto-refresh")
# ...existing code...

from config.settings import ALERTS_OUTPUT_PATH, STREAM_FILE_PATH

st.set_page_config(page_title="Fraud AI Assistant", layout="wide", page_icon="🛡️")
st.title("🛡️ Real-Time Financial Fraud Detection + AI Risk Assistant")

# Auto-refresh every 2 seconds
st.markdown(
    """
    <style>
    [data-testid="stMetricValue"] {
        font-size: 32px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# File paths
transactions_path = Path(STREAM_FILE_PATH)
alerts_path = Path("data/alerts.csv")
scored_path = Path("data/scored_transactions.csv")

# ============================================================================
# SECTION 1: KEY METRICS
# ============================================================================
st.subheader("📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

# Load data
transactions_df = None
alerts_df = None
scored_df = None

if transactions_path.exists() and transactions_path.stat().st_size > 0:
    try:
        transactions_df = pd.read_csv(transactions_path)
    except Exception:
        pass

if alerts_path.exists() and alerts_path.stat().st_size > 0:
    try:
        alerts_df = pd.read_csv(alerts_path)
    except Exception:
        pass

if scored_path.exists() and scored_path.stat().st_size > 0:
    try:
        scored_df = pd.read_csv(scored_path)
    except Exception:
        pass

# Display metrics
with col1:
    total_txns = len(transactions_df) if transactions_df is not None else 0
    st.metric("Total Transactions", total_txns)

with col2:
    total_alerts = len(alerts_df) if alerts_df is not None else 0
    st.metric("High-Risk Alerts", total_alerts, delta=None if total_alerts == 0 else "⚠️")

with col3:
    avg_risk = 0.0
    if scored_df is not None and "risk_score" in scored_df.columns:
        avg_risk = scored_df["risk_score"].mean()
    st.metric("Avg Risk Score", f"{avg_risk:.2f}")

with col4:
    fraud_rate = 0.0
    if total_txns > 0 and total_alerts > 0:
        fraud_rate = (total_alerts / total_txns) * 100
    st.metric("Fraud Rate", f"{fraud_rate:.1f}%")

st.divider()

# ============================================================================
# SECTION 2: LIVE RISK SCORE METER (Feature 1)
# ============================================================================
st.subheader("🎯 Live Risk Score Meter")

if scored_df is not None and len(scored_df) > 0:
    latest_risk_score = scored_df["risk_score"].iloc[-1]
    
    # Determine color based on risk level
    if latest_risk_score < 0.4:
        color = "green"
        status = "Low Risk"
    elif latest_risk_score < 0.7:
        color = "yellow"
        status = "Medium Risk"
    else:
        color = "red"
        status = "High Risk"
    
    # Create gauge chart using Plotly
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=latest_risk_score,
        title={'text': f"Latest Transaction Risk Score<br><span style='font-size:0.8em'>{status}</span>"},
        delta={'reference': 0.5},
        gauge={
            'axis': {'range': [None, 1.0], 'tickwidth': 1, 'tickcolor': "darkgray"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 0.4], 'color': 'lightgreen'},
                {'range': [0.4, 0.7], 'color': 'lightyellow'},
                {'range': [0.7, 1.0], 'color': 'lightcoral'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 0.7
            }
        }
    ))
    
    fig_gauge.update_layout(height=300, margin=dict(l=20, r=20, t=80, b=20))
    st.plotly_chart(fig_gauge, use_container_width=True)
else:
    st.info("⏳ Waiting for transaction data...")

st.divider()

# ============================================================================
# SECTION 3: RISK SCORE BREAKDOWN TABLE (Feature 2)
# ============================================================================
st.subheader("🔍 Risk Score Breakdown - Latest Transaction")

if scored_df is not None and len(scored_df) > 0:
    latest_row = scored_df.iloc[-1]
    
    # Parse breakdown if available
    breakdown_data = []
    
    # Build breakdown table
    breakdown_data.append({
        "Feature": "Large Amount",
        "Triggered": "✅" if latest_row.get("triggered_large_amount", False) else "❌",
        "Weight": 0.5,
        "Description": "Transaction amount > 3x rolling average"
    })
    
    breakdown_data.append({
        "Feature": "Rapid Transactions",
        "Triggered": "✅" if latest_row.get("triggered_rapid_fire", False) else "❌",
        "Weight": 0.3,
        "Description": "≥3 transactions in 120 seconds"
    })
    
    breakdown_data.append({
        "Feature": "Location Change",
        "Triggered": "✅" if latest_row.get("triggered_location_change", False) else "❌",
        "Weight": 0.25,
        "Description": "Location different from previous transaction"
    })
    
    breakdown_df = pd.DataFrame(breakdown_data)
    
    # Color code the table
    st.dataframe(
        breakdown_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Feature": st.column_config.TextColumn("Feature", width="medium"),
            "Triggered": st.column_config.TextColumn("Triggered", width="small"),
            "Weight": st.column_config.NumberColumn("Weight", format="%.2f", width="small"),
            "Description": st.column_config.TextColumn("Description", width="large"),
        }
    )
    
    # Show explanation
    if "explanation" in latest_row:
        st.info(f"**Explanation:** {latest_row['explanation']}")
else:
    st.info("⏳ Waiting for scored transaction data...")

st.divider()

# ============================================================================
# SECTION 4: REAL-TIME FRAUD TREND GRAPH (Feature 3)
# ============================================================================
st.subheader("📈 Real-Time Fraud Trend Graph")

if scored_df is not None and len(scored_df) > 0:
    # Create two trend charts side by side
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("**Risk Score Over Time**")
        
        # Prepare data for time series
        trend_df = scored_df.copy()
        if "timestamp" in trend_df.columns:
            trend_df["timestamp"] = pd.to_datetime(trend_df["timestamp"])
            trend_df = trend_df.sort_values("timestamp")
        
        # Create line chart with color gradient
        fig_trend = go.Figure()
        
        fig_trend.add_trace(go.Scatter(
            x=trend_df.index if "timestamp" not in trend_df.columns else trend_df["timestamp"],
            y=trend_df["risk_score"],
            mode='lines+markers',
            name='Risk Score',
            line=dict(color='rgb(255, 127, 14)', width=2),
            marker=dict(size=6, color=trend_df["risk_score"], 
                       colorscale=[[0, 'green'], [0.4, 'yellow'], [0.7, 'red']],
                       showscale=True,
                       colorbar=dict(title="Risk")),
        ))
        
        # Add threshold line
        fig_trend.add_hline(y=0.7, line_dash="dash", line_color="red", 
                           annotation_text="High Risk Threshold")
        
        fig_trend.update_layout(
            xaxis_title="Transaction Index" if "timestamp" not in trend_df.columns else "Time",
            yaxis_title="Risk Score",
            height=350,
            showlegend=True,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with col_right:
        st.markdown("**Fraud Count Per Minute**")
        
        # Calculate fraud count per minute
        if "timestamp" in scored_df.columns and "risk_score" in scored_df.columns:
            fraud_trend = scored_df.copy()
            fraud_trend["timestamp"] = pd.to_datetime(fraud_trend["timestamp"])
            fraud_trend["minute"] = fraud_trend["timestamp"].dt.floor("1min")
            fraud_trend["is_fraud"] = fraud_trend["risk_score"] >= 0.7
            
            fraud_per_minute = fraud_trend.groupby("minute").agg({
                "is_fraud": "sum",
                "risk_score": "count"
            }).reset_index()
            fraud_per_minute.columns = ["minute", "fraud_count", "total_count"]
            
            fig_fraud_count = go.Figure()
            
            fig_fraud_count.add_trace(go.Bar(
                x=fraud_per_minute["minute"],
                y=fraud_per_minute["fraud_count"],
                name="Fraud Count",
                marker_color='crimson'
            ))
            
            fig_fraud_count.update_layout(
                xaxis_title="Time (1-minute intervals)",
                yaxis_title="Fraud Count",
                height=350,
                showlegend=True
            )
            
            st.plotly_chart(fig_fraud_count, use_container_width=True)
        else:
            st.info("Insufficient data for fraud trend analysis")
else:
    st.info("⏳ Waiting for trend data...")

st.divider()

# ============================================================================
# SECTION 5: LIVE TRANSACTIONS TABLE
# ============================================================================
st.subheader("📋 Live Transactions (Last 20)")

if transactions_df is not None and len(transactions_df) > 0:
    display_df = transactions_df.tail(20).copy()
    st.dataframe(display_df, use_container_width=True, hide_index=True)
else:
    st.info("⏳ No transactions available yet.")

st.divider()

# ============================================================================
# SECTION 6: HIGH-RISK ALERTS
# ============================================================================
st.subheader("🚨 High-Risk Alerts")

if alerts_df is not None and len(alerts_df) > 0:
    st.metric("Total High-Risk Alerts", len(alerts_df))
    
    display_cols = ["transaction_id", "user_id", "amount", "location", "risk_score", "explanation"]
    available_cols = [col for col in display_cols if col in alerts_df.columns]
    
    st.dataframe(
        alerts_df[available_cols],
        use_container_width=True,
        hide_index=True,
        column_config={
            "risk_score": st.column_config.NumberColumn("Risk Score", format="%.2f"),
            "amount": st.column_config.NumberColumn("Amount", format="$%.2f"),
        }
    )
else:
    st.success("✅ No high-risk alerts at the moment.")

# Auto-refresh
st.markdown("---")
st.markdown("🔄 *Dashboard auto-refreshes every 2 seconds*")

# Add refresh button
if st.button("🔄 Refresh Now"):
    st.rerun()

# Auto-refresh configuration
st.markdown(
    """
    <script>
    setTimeout(function() {
        window.location.reload();
    }, 2000);
    </script>
    """,
    unsafe_allow_html=True
)
