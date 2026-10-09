import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------
# PAGE CONFIGURATION & DARK TEAL + GOLD THEME CSS
# ---------------------------------------------------------
st.set_page_config(
    page_title="GBS Acquisition Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dark Teal Aesthetic CSS with Gold Sliders & White Labels
st.markdown("""
<style>
    .stApp {
        background-color: #082C33;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #FFFFFF;
    }
    
    .main-header {
        color: #FFFFFF;
        font-size: 1.4rem;
        font-weight: 800;
        margin-bottom: 2px;
        letter-spacing: -0.5px;
    }
    .sub-header {
        color: #E2E8F0;
        font-size: 0.82rem;
        font-weight: 500;
        margin-bottom: 12px;
    }
    
    .stCaption, p, span, label {
        color: #FFFFFF !important;
    }
    
    /* Streamlit Sliders in Gold (#F6C344) */
    div[data-baseweb="slider"] div[role="slider"] {
        background-color: #F6C344 !important;
        border-color: #F6C344 !important;
        box-shadow: 0 0 8px rgba(246, 195, 68, 0.6) !important;
    }
    div[data-baseweb="slider"] div {
        background: linear-gradient(to right, #F6C344, #1CDAC5) !important;
    }
    
    /* Top Sticky Metric Cards */
    .top-summary-container {
        background-color: #0E424D;
        border: 1px solid #1A5A67;
        border-radius: 10px;
        padding: 10px 12px;
        margin-bottom: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    }
    .top-label {
        color: #FFFFFF !important;
        font-size: 0.70rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .top-value {
        color: #1CDAC5;
        font-size: 1.25rem;
        font-weight: 800;
    }
    .top-sub {
        color: #F6C344;
        font-size: 0.72rem;
        font-weight: 600;
    }

    /* Financial Mobile Cards */
    .pnl-card {
        background-color: #0E424D;
        border-left: 4px solid #F6C344;
        border-radius: 8px;
        padding: 10px 12px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.25);
    }
    .pnl-year {
        color: #FFFFFF;
        font-size: 0.9rem;
        font-weight: 800;
        margin-bottom: 6px;
    }
    .pnl-row {
        display: flex;
        justify-content: space-between;
        font-size: 0.82rem;
        padding: 4px 0;
        border-bottom: 1px dashed #1E515C;
    }
    .pnl-title { color: #FFFFFF !important; font-weight: 600; }
    .pnl-val { color: #1CDAC5; font-weight: 700; }

    /* Dark Mode Tab Customization */
    button[data-baseweb="tab"] {
        font-size: 0.88rem !important;
        font-weight: 700 !important;
        color: #E2E8F0 !important;
        padding: 8px 12px !important;
        background-color: transparent !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #F6C344 !important;
        border-bottom-color: #F6C344 !important;
    }
    
    /* Dataframe Container Dark Theme */
    div[data-testid="stDataFrame"] {
        background-color: #0E424D;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Helper Function: Pure Python IRR Solver
def calculate_irr(cash_flows, iterations=1000, tol=1e-5):
    rate_low, rate_high = -0.99, 10.0
    for _ in range(iterations):
        mid_rate = (rate_low + rate_high) / 2.0
        npv = sum(cf / ((1.0 + mid_rate) ** i) for i, cf in enumerate(cash_flows))
        if abs(npv) < tol:
            return mid_rate
        if npv > 0:
            rate_low = mid_rate
        else:
            rate_high = mid_rate
    return (rate_low + rate_high) / 2.0

# ---------------------------------------------------------
# TITLE & SUBTITLE
# ---------------------------------------------------------
st.markdown("<div class='main-header'>GBS Acquisition Dashboard</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Standalone Asset Level • Dynamic Sensitivity Simulator</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# INPUT CONTROLS (WITH FINANCIAL COMMA FORMATTING)
# ---------------------------------------------------------
tab_inputs, tab_pnl, tab_breakeven = st.tabs(["🎛️ 1. Inputs", "📋 2. Financials", "⚖️ 3. Sensitivity & Matrix"])

with tab_inputs:
    st.markdown("<h4 style='color: #F6C344;'>Operating Drivers</h4>", unsafe_allow_html=True)
    
    rev2027 = st
