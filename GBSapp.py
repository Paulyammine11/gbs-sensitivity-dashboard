import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import numpy_financial as npf

st.set_page_config(page_title="GBS Acquisition Dashboard", layout="wide")

st.markdown("<h2 style='color: #0A3841;'>GBS Acquisition — Dynamic Sensitivity & Valuation Simulator</h2>", unsafe_allow_html=True)
st.caption("Standalone Asset Level (Includes Multi-Year Cash Flow & Exit Valuation)")

# ---------------------------------------------------------
# 1. INPUT DRIVER SELECTORS
# ---------------------------------------------------------
st.subheader("1. Input Driver Selectors")

col_s1, col_s2, col_s3, col_s4 = st.columns(4)

with col_s1:
    rev2027 = st.slider("Year 1 (2027F) Revenue ($)", 1000000, 2500000, 1626975, step=25000)
    st.markdown(f"<p style='color: #0A3841; font-weight: bold;'>Target 2027: ${rev2027:,.0f}</p>", unsafe_allow_html=True)

with col_s2:
    gm = st.slider("Gross Margin % Target", 20.0, 45.0, 25.43475, step=0.5) / 100.0
    st.markdown(f"<p style='color: #0A3841; font-weight: bold;'>Margin: {gm*100:.2f}%</p>", unsafe_allow_html=True)

with col_s3:
    mult = st.slider("Exit EV/EBITDA Multiple", 2.0, 8.0, 3.0, step=0.25)
    st.markdown(f"<p style='color: #0A3841; font-weight: bold;'>Multiple: {mult:.2f}x</p>", unsafe_allow_html=True)

with col_s4:
    target_irr = st.slider("Target IRR Benchmark (%)", 10.0, 150.0, 107.15, step=5.0)
    st.markdown(f"<p style='color: #0A3841; font-weight: bold;'>Benchmark IRR: {target_irr:.1f}%</p>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. DYNAMIC MODEL CALCULATIONS
# ---------------------------------------------------------
# Trajectory scaling relative to Excel base drivers
ratio_2028 = 5241736.125 / 1626975.0
ratio_2029 = 16887842.63 / 1626975.0

rev2028 = rev2027 * ratio_2028
rev2029 = rev2027 * ratio_2029

gp2027 = rev2027 * gm
gp2028 = rev2028 * gm
gp2029 = rev2029 * gm

# Overheads as modeled in Excel GBS sheet
oh2027 = 682410.60
oh2028 = 418605.33
oh2029 = 421959.80

ebitda2027 = gp2027 - oh2027
ebitda2028 = gp2028 - oh2028
ebitda2029 = gp2029 - oh2029

ebitda_margin_2029 = (ebitda2029 / rev2029) * 100.0 if rev2029 > 0 else 0
tv = max(0.0, ebitda2029 * mult)

# Breakeven EBITDA Analysis (2029)
breakeven_gp_2029 = oh2029
breakeven_rev_2029 = breakeven_gp_2029 / gm if gm > 0 else 0

# Multi-Year Cash Flow Stream (Aligned with GBS Returns Analysis Rows 106-109)
cf_2026 = -1521764.85
cf_2027 = ebitda2027 + (oh2027 - 682410.60) # Scaled ops cash flow
cf_2028 = ebitda2028 - 633625.75
cf_2029 = (ebitda2029 - 2084569.08) + tv

cash_flows = [cf_2026, -108072.51 * (rev2027/1626975.0), 280991.42 * (rev2028/5241736.125), (1788851.74 * (rev2029/16887842.63)) + tv]
calculated_irr = npf.irr(cash_flows) * 100.0 if not np.isnan(npf.irr(cash_flows)) else 0.0

st.divider()

# ---------------------------------------------------------
# 3. RECALCULATED OUTPUTS & BREAKEVEN METRICS
# ---------------------------------------------------------
st.subheader("2. Financial Outputs & Breakeven Metrics")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Year 3 (2029F) Revenue", f"${rev2029:,.0f}")
m2.metric("Year 3 Gross Profit", f"${gp2029:,.0f}")
m3.metric("Year 3 EBITDA", f"${ebitda2029:,.0f}", f"{ebitda_margin_2029:.1f}% Margin")
m4.metric("Terminal EV (@ Exit)", f"${tv:,.0f}")

m5, m6, m7, m8 = st.columns(4)
m5.metric("Projected IRR", f"{calculated_irr:.1f}%", f"{calculated_irr - target_irr:+.1f}% vs Target")
m6.metric("Breakeven Revenue (2029F)", f"${breakeven_rev_2029:,.0f}")
m7.metric("Breakeven EBITDA Gap", f"${ebitda2029:,.0f}", "At Breakeven" if ebitda2029 >= 0 else "Operating Loss")
m8.metric("Total Net Cash Exit (2029F)", f"${cash_flows[3]:,.0f}")

st.divider()

# ---------------------------------------------------------
# 4. FINANCIAL FLUCTUATION CHART
# ---------------------------------------------------------
st.subheader("3. Model Financial Trajectory & Valuation ($ Millions)")

labels = ['2027F Rev', '2029F Rev', '2029F Gross Profit', '2029F EBITDA', 'Terminal EV']
values = [rev2027, rev2029, gp2029, ebitda2029, tv]
values_m = [v / 1e6 for v in values]

colors = ['#0A3841', '#12525D', '#1CDAC5', '#0E8074', '#F6C344']

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
    ax.annotate(f"${val/1e6:.2f}M",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 4),
                textcoords="offset points",
                ha='center', va='bottom', fontsize=9, fontweight='bold', color='#0A3841')

max_val = max(values_m) if max(values_m) > 0 else 1.0
ax.set_ylim(min(0, min(values_m)*1.1), max_val * 1.25)

plt.xticks(fontweight='bold')
plt.tight_layout()

st.pyplot(fig)
