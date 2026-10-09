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
    /* Dark Teal Base Background */
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
    
    rev2027 = st.slider("2027F Revenue ($)", 1_000_000, 2_500_000, 1_626_975, step=25_000, format="$%,d")
    rev2028 = st.slider("2028F Revenue ($)", 2_000_000, 8_000_000, 5_241_736, step=50_000, format="$%,d")
    rev2029 = st.slider("2029F Revenue ($)", 5_000_000, 25_000_000, 16_887_843, step=100_000, format="$%,d")
    
    gm = st.slider("Gross Margin (%)", 20.0, 45.0, 25.43475, step=0.5, format="%.2f%%") / 100.0
    mult = st.slider("Exit Multiple (x)", 2.0, 8.0, 3.0, step=0.25, format="%.2fx")
    
    st.markdown("<h4 style='color: #F6C344;'>Capital & Working Capital Structure</h4>", unsafe_allow_html=True)
    ar_days = st.slider("Collection Period (AR Days)", 30, 120, 60, step=5)
    equity_mode = st.radio("Equity Commitment Mode", ["Auto-Sized (Dynamic)", "Fixed Manual Cap"])
    
    if equity_mode == "Auto-Sized (Dynamic)":
        safety_buffer_pct = st.slider("Safety Buffer (%)", 0.0, 30.0, 10.0, step=5.0, format="%.1f%%") / 100.0
        manual_equity = 0.0
    else:
        manual_equity = st.slider("Manual Equity ($)", 500_000, 2_500_000, 1_000_000, step=50_000, format="$%,d")
        safety_buffer_pct = 0.0

# ---------------------------------------------------------
# CORE DYNAMIC MODEL CALCULATIONS
# ---------------------------------------------------------
rev2026 = 505000.0
ebitda2026 = -100525.51

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

# Dynamic Working Capital & Cash Burn Engine
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
# EXECUTIVE TOP SUMMARY CARDS
# ---------------------------------------------------------
st.markdown("---")
st.markdown("<h4 style='color: #FFFFFF;'>Executive Key Metrics (Live)</h4>", unsafe_allow_html=True)

m_col1, m_col2 = st.columns(2)
with m_col1:
    st.markdown(f"""
    <div class="top-summary-container">
        <div class="top-label">Terminal Valuation</div>
        <div class="top-value">${tv/1e6:.2f}M</div>
        <div class="top-sub">Exit @ {mult:.2f}x Multiple</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="top-summary-container">
        <div class="top-label">Projected IRR</div>
        <div class="top-value">{calculated_irr:.1f}%</div>
        <div class="top-sub">Output Return</div>
    </div>
    """, unsafe_allow_html=True)

with m_col2:
    st.markdown(f"""
    <div class="top-summary-container">
        <div class="top-label">2029F EBITDA</div>
        <div class="top-value">${ebitda2029/1e6:.2f}M</div>
        <div class="top-sub">{ebitda_margin_2029:.1f}% Margin</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="top-summary-container">
        <div class="top-label">Funding Needed</div>
        <div class="top-value">${peak_cash_deficit/1e6:.2f}M</div>
        <div class="top-sub">Peak Deficit</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 2: FINANCIAL TRAJECTORY & BREAKEVEN COMBO CHART
# ---------------------------------------------------------
with tab_pnl:
    st.markdown("<h4 style='color: #1CDAC5;'>3-Year Financial Trajectory</h4>", unsafe_allow_html=True)
    
    # 2027F Card
    st.markdown(f"""
    <div class="pnl-card">
        <div class="pnl-year">Year 1 (2027F)</div>
        <div class="pnl-row"><span class="pnl-title">Revenue:</span><span class="pnl-val">${rev2027:,.0f}</span></div>
        <div class="pnl-row"><span class="pnl-title">Gross Profit ({gm*100:.1f}%):</span><span class="pnl-val">${gp2027:,.0f}</span></div>
        <div class="pnl-row"><span class="pnl-title">Overheads:</span><span class="pnl-val">${oh2027:,.0f}</span></div>
        <div class="pnl-row"><span class="pnl-title">EBITDA ({ebitda_margin_2027:.1f}%):</span><span class="pnl-val">${ebitda2027:,.0f}</span></div>
    </div>
    """, unsafe_allow_html=True)

    # 2028F Card
    st.markdown(f"""
    <div class="pnl-card">
        <div class="pnl-year">Year 2 (2028F)</div>
        <div class="pnl-row"><span class="pnl-title">Revenue:</span><span class="pnl-val">${rev2028:,.0f}</span></div>
        <div class="pnl-row"><span class="pnl-title">Gross Profit ({gm*100:.1f}%):</span><span class="pnl-val">${gp2028:,.0f}</span></div>
        <div class="pnl-row"><span class="pnl-title">Overheads:</span><span class="pnl-val">${oh2028:,.0f}</span></div>
        <div class="pnl-row"><span class="pnl-title">EBITDA ({ebitda_margin_2028:.1f}%):</span><span class="pnl-val">${ebitda2028:,.0f}</span></div>
    </div>
    """, unsafe_allow_html=True)

    # 2029F Card
    st.markdown(f"""
    <div class="pnl-card">
        <div class="pnl-year">Year 3 (2029F)</div>
        <div class="pnl-row"><span class="pnl-title">Revenue:</span><span class="pnl-val">${rev2029:,.0f}</span></div>
        <div class="pnl-row"><span class="pnl-title">Gross Profit ({gm*100:.1f}%):</span><span class="pnl-val">${gp2029:,.0f}</span></div>
        <div class="pnl-row"><span class="pnl-title">Overheads:</span><span class="pnl-val">${oh2029:,.0f}</span></div>
        <div class="pnl-row"><span class="pnl-title">EBITDA ({ebitda_margin_2029:.1f}%):</span><span class="pnl-val">${ebitda2029:,.0f}</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<h4 style='color: #1CDAC5;'>Financial Trajectory & Breakeven Curve</h4>", unsafe_allow_html=True)
    
    years = ['FY2026', 'FY2027', 'FY2028', 'FY2029']
    rev_series = [rev2026 / 1e6, rev2027 / 1e6, rev2028 / 1e6, rev2029 / 1e6]
    ebitda_series = [ebitda2026 / 1e6, ebitda2027 / 1e6, ebitda2028 / 1e6, ebitda2029 / 1e6]

    fig, ax = plt.subplots(figsize=(10, 4.8))
    fig.patch.set_facecolor('#082C33')
    ax.set_facecolor('#082C33')

    # Revenue Light Teal Bars
    bars = ax.bar(years, rev_series, color='#B2E3DE', width=0.45, label='Revenue', alpha=0.9)

    # EBITDA Gold Line
    x_coords = np.arange(len(years))
    ax.plot(x_coords, ebitda_series, color='#D4AF37', linewidth=2.5, marker='o', markersize=7, label='EBITDA')

    # Breakeven Crossover Line
    be_rev_active = be_rev_2028 / 1e6
    ax.axhline(0, color='#FFFFFF', linestyle='--', linewidth=1.0, alpha=0.6)
    
    if ebitda2027 < 0 and ebitda2028 > 0:
        frac = abs(ebitda2027) / (abs(ebitda2027) + ebitda2028)
        be_x = 1.0 + frac
    else:
        be_x = 2.0

    ax.axvline(be_x, color='#FFFFFF', linestyle=':', linewidth=1.2, alpha=0.7)
    ax.plot(be_x, 0, marker='o', markersize=8, color='#FFFFFF', markeredgecolor='#082C33', markeredgewidth=2)

    # Bre
