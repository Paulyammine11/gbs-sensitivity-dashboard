import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------
# PAGE CONFIGURATION & CUSTOM INSTITUTIONAL CSS
# ---------------------------------------------------------
st.set_page_config(
    page_title="GBS Acquisition Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional Mobile-Optimized Styling
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background-color: #F8FAFC;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Header Styling */
    .main-title {
        color: #0A3841;
        font-size: 1.6rem;
        font-weight: 800;
        margin-bottom: 2px;
        letter-spacing: -0.5px;
    }
    .sub-title {
        color: #64748B;
        font-size: 0.85rem;
        margin-bottom: 15px;
    }
    
    /* Custom Card Containers */
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-label {
        color: #64748B;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        color: #0A3841;
        font-size: 1.3rem;
        font-weight: 700;
    }
    .metric-subtitle {
        color: #0E8074;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    /* Streamlit Tab Customization */
    button[data-baseweb="tab"] {
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        color: #64748B !important;
        padding: 10px 16px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #0A3841 !important;
        border-bottom-color: #0A3841 !important;
    }
    
    /* Mobile-specific adjustments */
    @media (max-width: 640px) {
        .main-title { font-size: 1.3rem; }
        .metric-value { font-size: 1.15rem; }
        div[data-testid="stColumn"] { width: 100% !important; margin-bottom: 8px; }
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
# HEADER
# ---------------------------------------------------------
st.markdown("<div class='main-title'>GBS Acquisition — Valuation & Sensitivity</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Standalone Asset Level • Financial Model & Sensitivity Simulator</div>", unsafe_allow_html=True)

# Define Main Sections via Mobile-Friendly Tabs
tab_inputs, tab_tables, tab_outputs = st.tabs(["1. Inputs", "2. Tables", "3. Outputs"])

# =========================================================
# SECTION 1: MODEL INPUTS
# =========================================================
with tab_inputs:
    st.markdown("### 🎛️ Input Drivers")
    
    with st.expander("📊 **Revenue Targets (Years 1–3)**", expanded=True):
        rev2027 = st.slider("Year 1 (2027F) Revenue ($)", 1_000_000, 2_500_000, 1_626_975, step=25_000)
        st.caption(f"Active 2027F Revenue: **${rev2027:,.0f}**")
        
        rev2028 = st.slider("Year 2 (2028F) Revenue ($)", 2_000_000, 8_000_000, 5_241_736, step=50_000)
        st.caption(f"Active 2028F Revenue: **${rev2028:,.0f}**")
        
        rev2029 = st.slider("Year 3 (2029F) Revenue ($)", 5_000_000, 25_000_000, 16_887_843, step=100_000)
        st.caption(f"Active 2029F Revenue: **${rev2029:,.0f}**")

    with st.expander("📈 **Margin & Exit Multiple Drivers**", expanded=True):
        gm = st.slider("Gross Margin Target (%)", 20.0, 45.0, 25.43475, step=0.5) / 100.0
        st.caption(f"Active Gross Margin: **{gm*100:.2f}%**")
        
        mult = st.slider("Exit EV/EBITDA Multiple (x)", 2.0, 8.0, 3.0, step=0.25)
        st.caption(f"Active Exit Multiple: **{mult:.2f}x**")

    with st.expander("💰 **Capital & Dynamic Equity Structure**", expanded=True):
        equity_mode = st.radio("Equity Commitment Sizing Mode", ["Auto-Sized (Dynamic)", "Fixed Manual Cap"])
        
        if equity_mode == "Auto-Sized (Dynamic)":
            safety_buffer_pct = st.slider("Equity Safety Buffer (%)", 0.0, 30.0, 10.0, step=5.0) / 100.0
            manual_equity = 0.0
        else:
            manual_equity = st.slider("Manual Equity Injection ($)", 500_000, 2_500_000, 1_000_000, step=50_000)
            safety_buffer_pct = 0.0

# ---------------------------------------------------------
# CORE MODEL ENGINE CALCULATIONS
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

# Working Capital & Cash Burn Engine
ar_days = 60
ar_2027 = rev2027 * (ar_days / 365.0)
ar_2028 = rev2028 * (ar_days / 365.0)
ar_2029 = rev2029 * (ar_days / 365.0)

cf_2026_ops = -521764.85
cf_2027_ops = ebitda2027 - (ar_2027 - 252500.0)
cf_2028_ops = ebitda2028 - (ar_2028 - ar_2027)
cf_2029_ops = ebitda2029 - (ar_2029 - ar_2028)

# Peak Deficit & Dynamic Equity Sizing
cum_cash_2026 = cf_2026_ops
cum_cash_2027 = cum_cash_2026 + cf_2027_ops
cum_cash_2028 = cum_cash_2027 + cf_2028_ops

peak_cash_deficit = abs(min(0.0, cum_cash_2026, cum_cash_2027, cum_cash_2028))

if equity_mode == "Auto-Sized (Dynamic)":
    dynamic_committed_equity = peak_cash_deficit * (1.0 + safety_buffer_pct)
else:
    dynamic_committed_equity = manual_equity

funding_cushion = dynamic_committed_equity - peak_cash_deficit

# IRR Solver
cash_flows = [-dynamic_committed_equity + cf_2026_ops, cf_2027_ops, cf_2028_ops, cf_2029_ops + tv]
calculated_irr = calculate_irr(cash_flows) * 100.0

# EBITDA Breakeven Revenues
be_rev_2027 = oh2027 / gm if gm > 0 else 0
be_rev_2028 = oh2028 / gm if gm > 0 else 0
be_rev_2029 = oh2029 / gm if gm > 0 else 0


# =========================================================
# SECTION 2: FINANCIAL TABLES
# =========================================================
with tab_tables:
    st.markdown("### 📋 Model Financial Tables")
    
    st.markdown("##### **1. 3-Year P&L Forecast Summary ($)**")
    pnl_data = [
        {"Metric": "Revenue", "2027F (Yr 1)": f"${rev2027:,.0f}", "2028F (Yr 2)": f"${rev2028:,.0f}", "2029F (Yr 3)": f"${rev2029:,.0f}"},
        {"Metric": "Gross Profit", "2027F (Yr 1)": f"${gp2027:,.0f}", "2028F (Yr 2)": f"${gp2028:,.0f}", "2029F (Yr 3)": f"${gp2029:,.0f}"},
        {"Metric": "Gross Margin %", "2027F (Yr 1)": f"{gm*100:.2f}%", "2028F (Yr 2)": f"{gm*100:.2f}%", "2029F (Yr 3)": f"{gm*100:.2f}%"},
        {"Metric": "Fixed Overheads", "2027F (Yr 1)": f"${oh2027:,.0f}", "2028F (Yr 2)": f"${oh2028:,.0f}", "2029F (Yr 3)": f"${oh2029:,.0f}"},
        {"Metric": "EBITDA", "2027F (Yr 1)": f"${ebitda2027:,.0f}", "2028F (Yr 2)": f"${ebitda2028:,.0f}", "2029F (Yr 3)": f"${ebitda2029:,.0f}"},
        {"Metric": "EBITDA Margin %", "2027F (Yr 1)": f"{ebitda_margin_2027:.1f}%", "2028F (Yr 2)": f"{ebitda_margin_2028:.1f}%", "2029F (Yr 3)": f"{ebitda_margin_2029:.1f}%"},
    ]
    st.dataframe(pnl_data, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.markdown("##### **2. EBITDA Breakeven Revenue Matrix ($)**")
    st.caption("Sales revenue levels required to achieve Breakeven EBITDA ($0) at varying gross margins.")
    
    margin_steps = [0.20, 0.25, 0.30, 0.35, 0.40]
    if gm not in margin_steps:
        margin_steps.append(gm)
    margin_steps = sorted(margin_steps)

    be_table_data = []
    for m in margin_steps:
        be_table_data.append({
            "Gross Margin %": f"{m*100:.2f}%" + (" (Active)" if abs(m - gm) < 1e-4 else ""),
            "2027F Breakeven": f"${oh2027/m:,.0f}",
            "2028F Breakeven": f"${oh2028/m:,.0f}",
            "2029F Breakeven": f"${oh2029/m:,.0f}"
        })
    st.dataframe(be_table_data, use_container_width=True, hide_index=True)


# =========================================================
# SECTION 3: EXECUTIVE OUTPUTS
# =========================================================
with tab_outputs:
    st.markdown("### 📊 Executive Summary & Returns")
    
    # Financial Output Cards
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>2029F Exit Revenue</div>
            <div class='metric-value'>${rev2029:,.0f}</div>
            <div class='metric-subtitle'>3-Year Horizon Target</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>2029F EBITDA</div>
            <div class='metric-value'>${ebitda2029:,.0f}</div>
            <div class='metric-subtitle'>{ebitda_margin_2029:.1f}% EBITDA Margin</div>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Terminal Enterprise Value</div>
            <div class='metric-value'>${tv:,.0f}</div>
            <div class='metric-subtitle'>Exit @ {mult:.2f}x Multiple</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Projected Asset IRR</div>
            <div class='metric-value'>{calculated_irr:.2f}%</div>
            <div class='metric-subtitle'>Output Rate of Return</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("##### **Capital Sizing & Funding Needs**")
    
    col_c, col_d = st.columns(2)
    with col_c:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Peak Cash Deficit</div>
            <div class='metric-value'>${peak_cash_deficit:,.0f}</div>
            <div class='metric-subtitle'>Max Cash Burn Requirement</div>
        </div>
        """, unsafe_allow_html=True)

    with col_d:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Committed Base Equity</div>
            <div class='metric-value'>${dynamic_committed_equity:,.0f}</div>
            <div class='metric-subtitle'>Mode: {equity_mode}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("##### **3-Year Revenue & EBITDA Trajectory ($ Millions)**")

    # Mobile Charting Engine
    labels = ['27 Rev', '27 EBITDA', '28 Rev', '28 EBITDA', '29 Rev', '29 EBITDA']
    values = [rev2027, ebitda2027, rev2028, ebitda2028, rev2029, ebitda2029]
    values_m = [v / 1e6 for v in values]

    colors = ['#0A3841', '#0E8074', '#12525D', '#1CDAC5', '#0A3841', '#F6C344']

    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')

    bars = ax.bar(labels, values_m, color=colors, width=0.55, edgecolor='#0A3841', linewidth=1.0)

    ax.set_ylabel('USD ($ Millions)', fontsize=9, fontweight='bold', color='#0A3841')
    ax.tick_params(axis='x', colors='#0A3841', labelsize=8.5)
    ax.tick_params(axis='y', colors='#0A3841', labelsize=8.5)
    ax.grid(axis='y', linestyle='--', alpha=0.3, color='#CBD5E1')

    for bar, val in zip(bars, values):
        height = bar.get_height()
        offset = 4 if height >= 0 else -10
        va_align = 'bottom' if height >= 0 else 'top'
        
        ax.annotate(f"${val/1e6:.2f}M",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, offset),
                    textcoords="offset points",
                    ha='center', va=va_align, fontsize=8, fontweight='bold', color='#0A3841')

    max_val = max(values_m) if max(values_m) > 0 else 1.0
    min_val = min(values_m) if min(values_m) < 0 else 0.0
    ax.set_ylim(min_val * 1.3, max_val * 1.25)

    plt.xticks(fontweight='bold')
    plt.tight_layout()

    st.pyplot(fig)
