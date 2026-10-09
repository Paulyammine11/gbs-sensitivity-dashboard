import streamlit as st
import numpy as np

# ---------------------------------------------------------
# PAGE CONFIGURATION & MOBILE CSS
# ---------------------------------------------------------
st.set_page_config(
    page_title="GBS Acquisition Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Responsive Mobile-First CSS
st.markdown("""
<style>
    .stApp {
        background-color: #F8FAFC;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Executive Top Sticky Header Cards */
    .top-summary-container {
        background-color: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 12px;
        padding: 12px 14px;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    .top-label {
        color: #64748B;
        font-size: 0.70rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .top-value {
        color: #0A3841;
        font-size: 1.25rem;
        font-weight: 800;
    }
    .top-sub {
        color: #0E8074;
        font-size: 0.72rem;
        font-weight: 600;
    }

    /* Mobile Table Card Styling */
    .pnl-card {
        background-color: #FFFFFF;
        border-left: 4px solid #0A3841;
        border-radius: 8px;
        padding: 10px 12px;
        margin-bottom: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .pnl-year {
        color: #0A3841;
        font-size: 0.9rem;
        font-weight: 800;
        margin-bottom: 4px;
    }
    .pnl-row {
        display: flex;
        justify-content: space-between;
        font-size: 0.82rem;
        padding: 2px 0;
        border-bottom: 1px dashed #F1F5F9;
    }
    .pnl-title { color: #475569; font-weight: 500; }
    .pnl-val { color: #0F172A; font-weight: 700; }

    /* Custom Streamlit Tab Styling */
    button[data-baseweb="tab"] {
        font-size: 0.88rem !important;
        font-weight: 700 !important;
        padding: 8px 12px !important;
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
st.markdown("<h3 style='color: #0A3841; margin-bottom:0px; font-weight:800;'>GBS Acquisition Dashboard</h3>", unsafe_allow_html=True)
st.caption("Standalone Asset Level • Dynamic Mobile Sensitivity Simulator")

# ---------------------------------------------------------
# INPUT CONTROLS (TABS FOR INPUTS VS DETAILED BREAKDOWNS)
# ---------------------------------------------------------
tab_inputs, tab_pnl, tab_breakeven = st.tabs(["🎛️ 1. Inputs", "📋 2. Financials", "⚖️ 3. Breakeven"])

with tab_inputs:
    st.markdown("#### **Operating Drivers**")
    
    rev2027 = st.slider("2027F Revenue ($)", 1_000_000, 2_500_000, 1_626_975, step=25_000)
    rev2028 = st.slider("2028F Revenue ($)", 2_000_000, 8_000_000, 5_241_736, step=50_000)
    rev2029 = st.slider("2029F Revenue ($)", 5_000_000, 25_000_000, 16_887_843, step=100_000)
    
    gm = st.slider("Gross Margin (%)", 20.0, 45.0, 25.43475, step=0.5) / 100.0
    mult = st.slider("Exit Multiple (x)", 2.0, 8.0, 3.0, step=0.25)
    
    st.markdown("#### **Capital Structure**")
    equity_mode = st.radio("Equity Commitment Mode", ["Auto-Sized (Dynamic)", "Fixed Manual Cap"])
    
    if equity_mode == "Auto-Sized (Dynamic)":
        safety_buffer_pct = st.slider("Safety Buffer (%)", 0.0, 30.0, 10.0, step=5.0) / 100.0
        manual_equity = 0.0
    else:
        manual_equity = st.slider("Manual Equity ($)", 500_000, 2_500_000, 1_000_000, step=50_000)
        safety_buffer_pct = 0.0

# ---------------------------------------------------------
# CORE MODEL CALCULATIONS
# ---------------------------------------------------------
gp2027 = rev2027 * gm
gp2028 = rev2028 * gm
gp2029 = rev2029 * gm

oh2027, oh2028, oh2029 = 682410.60, 418605.33, 421959.80

ebitda2027 = gp2027 - oh2027
ebitda2028 = gp2028 - oh2028
ebitda2029 = gp2029 - oh2029

ebitda_margin_2027 = (ebitda2027 / rev2027) * 100.0 if rev2027 > 0 else 0
ebitda_margin_2028 = (ebitda2028 / rev2028) * 100.0 if rev2028 > 0 else 0
ebitda_margin_2029 = (ebitda2029 / rev2029) * 100.0 if rev2029 > 0 else 0

tv = max(0.0, ebitda2029 * mult)

# Working Capital & Peak Deficit
ar_days = 60
ar_2027 = rev2027 * (ar_days / 365.0)
ar_2028 = rev2028 * (ar_days / 365.0)
ar_2029 = rev2029 * (ar_days / 365.0)

cf_2026_ops = -521764.85
cf_2027_ops = ebitda2027 - (ar_2027 - 252500.0)
cf_2028_ops = ebitda2028 - (ar_2028 - ar_2027)
cf_2029_ops = ebitda2029 - (ar_2029 - ar_2028)

cum_cash_2026 = cf_2026_ops
cum_cash_2027 = cum_cash_2026 + cf_2027_ops
cum_cash_2028 = cum_cash_2027 + cf_2028_ops

peak_cash_deficit = abs(min(0.0, cum_cash_2026, cum_cash_2027, cum_cash_2028))

if equity_mode == "Auto-Sized (Dynamic)":
    dynamic_committed_equity = peak_cash_deficit * (1.0 + safety_buffer_pct)
else:
    dynamic_committed_equity = manual_equity

funding_cushion = dynamic_committed_equity - peak_cash_deficit

cash_flows = [-dynamic_committed_equity + cf_2026_ops, cf_2027_ops, cf_2028_ops, cf_2029_ops + tv]
calculated_irr = calculate_irr(cash_flows) * 100.0

be_rev_2027 = oh2027 / gm if gm > 0 else 0
be_rev_2028 = oh2028 / gm if gm > 0 else 0
be_rev_2029 = oh2029 / gm if gm > 0 else 0

# ---------------------------------------------------------
# ALWAYS-VISIBLE TOP EXECUTIVE SUMMARY (MOBILE OPTIMIZED)
# ---------------------------------------------------------
st.markdown("---")
st.markdown("#### **Executive Key Metrics (Live)**")

m_col1, m_col2 = st.columns(2)
with m_col1:
    st.markdown(f"""
    <div class='top-summary-container'>
        <div class='top-label'>Terminal Valuation</div>
        <div class='top-value'>${tv/1e6:.2f}M</div>
        <div class='top-sub'>Exit @ {mult:.2f}x Multiple</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class='top-summary-container'>
        <div class='top-label'>Projected IRR</div>
        <div class='top-value'>{calculated_irr:.1f}%</div>
        <div class='top-sub'>Output Return</div>
    </div>
    """, unsafe_allow_html=True)

with m_col2:
    st.markdown(f"""
    <div class='top-summary-container'>
        <div class='top-label'>2029F EBITDA</div>
        <div class='top-value'>${ebitda2029/1e6:.2f}M</div>
        <div class='top-sub'>{ebitda_margin_2029:.1f}% Margin</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='top-summary-container'>
        <div class='top-label'>Funding Needed</div>
        <div class='top-value'>${peak_cash_deficit/1e6:.2f}M</div>
        <div class='top-sub'>Peak Deficit</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 2: MOBILE FINANCIAL CARDS (NO HIDDEN COLUMNS)
# ---------------------------------------------------------
with tab_pnl:
    st.markdown("#### **3-Year Financial Trajectory**")
    
    # 2027F Card
    st.markdown(f"""
    <div class='pnl-card'>
        <div class='pnl-year'>Year 1 (2027F)</div>
        <div class='pnl-row'><span class='pnl-title'>Revenue:</span><span class='pnl-val'>${rev2027:,.0f}</span></div>
        <div class='pnl-row'><span class='pnl-title'>Gross Profit ({gm*100:.1f}%):</span><span class='pnl-val'>${gp2027:,.0f}</span></div>
        <div class='pnl-row'><span class='pnl-title'>Overheads:</span><span class='pnl-val'>${oh2027:,.0f}</span></div>
        <div class='pnl-row'><span class='pnl-title'>EBITDA ({ebitda_margin_2027:.1f}%):</span><span class='pnl-val'>${ebitda2027:,.0f}</span></div>
    </div>
    """, unsafe_allow_html=True)

    # 2028F Card
    st.markdown(f"""
    <div class='pnl-card'>
        <div class='pnl-year'>Year 2 (2028F)</div>
        <div class='pnl-row'><span class='pnl-title'>Revenue:</span><span class='pnl-val'>${rev
