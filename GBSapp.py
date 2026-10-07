import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="GBS Acquisition Dashboard", layout="centered")

st.markdown("<h2 style='color: #0A3841;'>GBS Acquisition — Dynamic Sensitivity Simulator</h2>", unsafe_allow_html=True)
st.caption("Standalone Asset Level (Excludes Holdco Overheads & External Debt)")

# ---------------------------------------------------------
# 1. INPUT DRIVER SELECTORS (With Comma-Formatted Display)
# ---------------------------------------------------------
st.subheader("1. Input Driver Selectors")

col_s1, col_s2, col_s3 = st.columns(3)

with col_s1:
    rev2027 = st.slider("Year 1 (2027F) Revenue ($)", 1000000, 2500000, 1626975, step=25000)
    st.markdown(f"<p style='color: #0A3841; font-weight: bold;'>Target: ${rev2027:,.0f}</p>", unsafe_allow_html=True)

with col_s2:
    gm = st.slider("Gross Margin % Target", 20.0, 45.0, 25.43, step=0.5) / 100.0
    st.markdown(f"<p style='color: #0A3841; font-weight: bold;'>Margin: {gm*100:.1f}%</p>", unsafe_allow_html=True)

with col_s3:
    mult = st.slider("Exit EV/EBITDA Multiple", 2.0, 6.0, 3.0, step=0.25)
    st.markdown(f"<p style='color: #0A3841; font-weight: bold;'>Multiple: {mult:.2f}x</p>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. MODEL CALCULATIONS
# ---------------------------------------------------------
rev2029 = rev2027 * 10.379904
gp2029 = rev2029 * gm
ebitda2029 = gp2029 - 421959.80
ebitda_margin = (ebitda2029 / rev2029) * 100.0
tv = max(0.0, ebitda2029 * mult)

st.divider()

# ---------------------------------------------------------
# 2. LIVE RECALCULATED OUTPUTS (Financial Formatting)
# ---------------------------------------------------------
st.subheader("2. Live Recalculated Outputs")
col1, col2 = st.columns(2)
col1.metric("Year 3 (2029F) Revenue", f"${rev2029:,.0f}")
col2.metric("Year 3 Gross Profit", f"${gp2029:,.0f}")

col3, col4 = st.columns(2)
col3.metric("Year 3 EBITDA", f"${ebitda2029:,.0f}", f"{ebitda_margin:.1f}% Margin")
col4.metric("Terminal Enterprise Value (@ Exit)", f"${tv:,.0f}")

st.divider()

# ---------------------------------------------------------
# 3. INTERACTIVE FLUCTUATION VISUAL (Live Reacting Bar Chart)
# ---------------------------------------------------------
st.subheader("3. Live Model Financial Fluctuation")

# Financial trajectory components
labels = ['2027F Revenue', '2029F Revenue', '2029F Gross Profit', '2029F EBITDA', 'Terminal EV (@ Exit)']
values = [rev2027, rev2029, gp2029, ebitda2029, tv]
values_m = [v / 1e6 for v in values] # Convert to Millions for clean scale

colors = ['#0A3841', '#12525D', '#1CDAC5', '#0E8074', '#F6C344']

fig, ax = plt.subplots(figsize=(10, 4.5))
fig.patch.set_facecolor('#FFFFFF')
ax.set_facecolor('#F8FAFC')

bars = ax.bar(labels, values_m, color=colors, width=0.55, edgecolor='#0A3841', linewidth=1.2)

ax.set_ylabel('USD ($ Millions)', fontsize=11, fontweight='bold', color='#0A3841')
ax.set_title('Live Standalone Financial Trajectory & Exit Valuation ($ Millions)', 
             fontsize=12, fontweight='bold', color='#0A3841', pad=15)
ax.tick_params(axis='x', colors='#0A3841', labelsize=10)
ax.tick_params(axis='y', colors='#0A3841', labelsize=10)
ax.grid(axis='y', linestyle='--', alpha=0.5, color='#CBD5E1')

# Add live data labels on top of each bar
for bar, val in zip(bars, values):
    height = bar.get_height()
    ax.annotate(f"${val:,.0f}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 5),  # 5 points vertical offset
                textcoords="offset points",
                ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#0A3841')

# Adjust Y-axis limit dynamically
max_val = max(values_m) if max(values_m) > 0 else 1.0
ax.set_ylim(0, max_val * 1.22)

plt.xticks(fontweight='bold')
plt.tight_layout()

st.pyplot(fig)
