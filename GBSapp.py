import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="GBS Acquisition Dashboard", layout="wide")

st.markdown("<h2 style='color: #0A3841;'>GBS Acquisition — Dynamic Sensitivity & Funding Simulator</h2>", unsafe_allow_html=True)
st.caption("Standalone Asset Level — Fully Dynamic Working Capital & Capital Deficit Engine")

# Pure Python IRR solver
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
# 1. INPUT DRIVER SELECTORS (Operational & Capital Controls)
# ---------------------------------------------------------
st.subheader("1. Input Driver Selectors")

st.markdown("##### **Revenue Trajectory Inputs (Years 1–3)**")
col_r1, col_r2, col_r3 = st.columns(3)

with col_r1:
    rev2027 = st.slider("Year 1 (2027F) Revenue ($)", 1_000_000, 2_500_000, 1_626_975, step=25_000)
    st.markdown(f"<p style='color: #0A3841; font-weight: bold;'>2027 Target: ${rev2027:,.0f}</p>", unsafe_allow_html=True)

with col_r2:
    rev2028 = st.slider("Year 2 (2028F) Revenue ($)", 2_000_000, 8_000_000, 5_241_736, step=50_000)
    st.markdown(f"<p style='color: #0A3841; font-weight: bold;'>2028 Target: ${rev2028:,.0f}</p>", unsafe_allow_html=True)

with col_r3:
    rev2029 = st.slider("Year 3 (2029F) Revenue ($)", 5_000_000, 25_000_000, 16_887_843, step=100_000)
    st.markdown(f"<p style='color: #0A3841; font-weight: bold;'>2029 Target: ${rev2029:,.0f}</p>", unsafe_allow_html=True)

st.markdown("##### **Margin, Valuation & Funding Controls**")
col_m1, col_m2, col_m3, col_m4 = st.columns(4)

with col_m1:
    gm = st.slider("Gross Margin % Target", 20.0, 45.0, 25.43475, step=0.5) / 100.0
    st.markdown(f"<p style='color: #0A3841; font-weight: bold;'>Margin: {gm*100:.2f}%</p>", unsafe_allow_html=True)

with col_m2:
    mult = st.slider("Exit EV/EBITDA Multiple", 2.0, 8.0, 3.0, step=0.25)
    st.markdown(f"<p style='color: #0A3841; font-weight: bold;'>Multiple: {mult:.2f}x</p>", unsafe_allow_html=True)

with col_m3:
    initial_equity = st.slider("Base Equity Commitment ($)", 500_000, 2_500_000, 1_000_000, step=50_000)
    st.markdown(f"<p style='color: #0A3841; font-weight: bold;'>Commitment: ${initial_equity:,.0f}</p>", unsafe_allow_html=True)

with col_m4:
    ar_days = st.slider("Accounts Receivable Days", 30, 120, 60, step=5)
    st.markdown(f"<p style='color: #0A3841; font-weight: bold;'>Collection Terms: {ar_days} Days</p>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. DYNAMIC P&L & WORKING CAPITAL CALCULATIONS
# ---------------------------------------------------------
gp2027 = rev2027 * gm
gp2028 = rev2028 * gm
gp2029 = rev2029 * gm

# Fixed Overheads
oh2027 = 682410.60
oh2028 = 418605.33
oh2029 = 421959.80

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

# Operating Cash Flow Modeling
cf_2026_ops = -521764.85 # Pre-launch 2026 setup burn
cf_2027_ops = ebitda2027 - (ar_2027 - 252500.0) # Adjust for AR working capital building
cf_2028_ops = ebitda2028 - (ar_2028 - ar_2027)
cf_2029_ops = ebitda2029 - (ar_2029 - ar_2028)

# Cumulative Dynamic Cash Deficit (Funding Needs)
cum_cash_2026 = cf_2026_ops
cum_cash_2027 = cum_cash_2026 + cf_2027_ops
cum_cash_2028 = cum_cash_2027 + cf_2028_ops

peak_cash_deficit = min(0.0, cum_cash_2026, cum_cash_2027, cum_cash_2028)
dynamic_funding_needed = abs(peak_cash_deficit)
funding_buffer = initial_equity - dynamic_funding_needed

# Returns & IRR
cash_flows = [-initial_equity + cf_2026_ops, cf_2027_ops, cf_2028_ops, cf_2029_ops + tv]
calculated_irr = calculate_irr(cash_flows) * 100.0

# EBITDA Breakeven Revenues
be_rev_2027 = oh2027 / gm if gm > 0 else 0
be_rev_2028 = oh2028 / gm if gm > 0 else 0
be_rev_2029 = oh2029 / gm if gm > 0 else 0

st.divider()

# ---------------------------------------------------------
# 3. LIVE OUTPUTS & DYNAMIC FUNDING DASHBOARD
# ---------------------------------------------------------
st.subheader("2. Live Financial Outputs & Returns")

col1, col2, col3, col4 = st.columns(4)
col1.metric("2027F Revenue (Yr 1)", f"${rev2027:,.0f}")
col2.metric("2028F Revenue (Yr 2)", f"${rev2028:,.0f}")
col3.metric("2029F Revenue (Yr 3)", f"${rev2029:,.0f}")
col4.metric("Terminal EV (@ Exit)", f"${tv:,.0f}")

col5, col6, col7, col8 = st.columns(4)
col5.metric("2027F EBITDA", f"${ebitda2027:,.0f}", f"{ebitda_margin_2027:.1f}% Margin")
col6.metric("2028F EBITDA", f"${ebitda2028:,.0f}", f"{ebitda_margin_2028:.1f}% Margin")
col7.metric("2029F EBITDA", f"${ebitda2029:,.0f}", f"{ebitda_margin_2029:.1f}% Margin")
col8.metric("Projected IRR (Output)", f"{calculated_irr:.2f}%")

st.markdown("##### **Dynamic Capital & Funding Dashboard**")
f1, f2, f3, f4 = st.columns(4)
f1.metric("Peak Cash Deficit (Funding Need)", f"${dynamic_funding_needed:,.0f}", help="Maximum cash burn across startup phase & operations.")
f2.metric("Committed Base Equity", f"${initial_equity:,.0f}")
f3.metric("Funding Cushion / (Shortfall)", f"${funding_buffer:,.0f}", delta=f"{funding_buffer:,.0f}")
f4.metric("AR Working Capital Lockup (Yr 1)", f"${ar_2027:,.0f}", f"{ar_days} Days AR")

st.divider()

# ---------------------------------------------------------
# 4. EBITDA BREAKEVEN ANALYSIS AT GROSS MARGIN LEVEL
# ---------------------------------------------------------
st.subheader("3. EBITDA Breakeven Analysis")
st.caption("Sales revenue levels required to achieve Breakeven EBITDA ($0) across operating years.")

b1, b2, b3 = st.columns(3)
b1.metric("2027F Breakeven Revenue", f"${be_rev_2027:,.0f}", f"Current: ${rev2027:,.0f}")
b2.metric("2028F Breakeven Revenue", f"${be_rev_2028:,.0f}", f"Current: ${rev2028:,.0f}")
b3.metric("2029F Breakeven Revenue", f"${be_rev_2029:,.0f}", f"Current: ${rev2029:,.0f}")

st.markdown("**Breakeven Revenue Matrix at Varying Gross Margins:**")

margin_steps = [0.20, 0.25, 0.30, 0.35, 0.40]
if gm not in margin_steps:
    margin_steps.append(gm)
margin_steps = sorted(margin_steps)

table_data = []
for m in margin_steps:
    table_data.append({
        "Gross Margin %": f"{m*100:.2f}%" + (" (Active Target)" if abs(m - gm) < 1e-4 else ""),
        "2027F Breakeven Sales ($)": f"${oh2027/m:,.0f}",
        "2028F Breakeven Sales ($)": f"${oh2028/m:,.0f}",
        "2029F Breakeven Sales ($)": f"${oh2029/m:,.0f}"
    })

st.table(table_data)

st.divider()

# ---------------------------------------------------------
# 5. REVENUES & EBITDA CHART
# ---------------------------------------------------------
st.subheader("4. 3-Year Trajectory: Revenue & EBITDA Comparison ($ Millions)")

labels = ['2027F Rev', '2027F EBITDA', '2028F Rev', '2028F EBITDA', '2029F Rev', '2029F EBITDA']
values = [rev2027, ebitda2027, rev2028, ebitda2028, rev2029, ebitda2029]
values_m = [v / 1e6 for v in values]

colors = ['#0A3841', '#0E8074', '#12525D', '#1CDAC5', '#0A3841', '#F6C344']

fig, ax = plt.subplots(figsize=(10, 4.2))
fig.patch.set_facecolor('#FFFFFF')
ax.set_facecolor('#F8FAFC')

bars = ax.bar(labels, values_m, color=colors, width=0.5, edgecolor='#0A3841', linewidth=1.2)

ax.set_ylabel('USD ($ Millions)', fontsize=10, fontweight='bold', color='#0A3841')
ax.tick_params(axis='x', colors='#0A3841', labelsize=10)
ax.tick_params(axis='y', colors='#0A3841', labelsize=10)
ax.grid(axis='y', linestyle='--', alpha=0.4, color='#CBD5E1')

for bar, val in zip(bars, values):
    height = bar.get_height()
    offset = 4 if height >= 0 else -12
    va_align = 'bottom' if height >= 0 else 'top'
    
    ax.annotate(f"${val/1e6:.2f}M",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, offset),
                textcoords="offset points",
                ha='center', va=va_align, fontsize=9, fontweight='bold', color='#0A3841')

max_val = max(values_m) if max(values_m) > 0 else 1.0
min_val = min(values_m) if min(values_m) < 0 else 0.0
ax.set_ylim(min_val * 1.3, max_val * 1.25)

plt.xticks(fontweight='bold')
plt.tight_layout()

st.pyplot(fig)
