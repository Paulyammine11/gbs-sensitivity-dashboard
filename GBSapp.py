import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="GBS Acquisition Dashboard", layout="centered")

st.markdown("<h2 style='color: #0A3841;'>GBS Acquisition — Dynamic Sensitivity Simulator</h2>", unsafe_allow_html=True)
st.caption("Standalone Asset Level (Excludes Holdco Overheads & External Debt)")

# 1. Slider Controls
st.subheader("1. Input Driver Selectors")
col_s1, col_s2, col_s3 = st.columns(3)

with col_s1:
    rev2027 = st.slider("Year 1 (2027F) Revenue ($)", 1000000, 2500000, 1626975, step=25000)
with col_s2:
    gm = st.slider("Gross Margin %", 20.0, 45.0, 25.43, step=0.5) / 100.0
with col_s3:
    mult = st.slider("Exit EV/EBITDA Multiple", 2.0, 6.0, 3.0, step=0.25)

# 2. Model Calculations
rev2029 = rev2027 * 10.379904
gp2029 = rev2029 * gm
ebitda2029 = gp2029 - 421959.80
ebitda_margin = (ebitda2029 / rev2029) * 100.0
tv = max(0.0, ebitda2029 * mult)

st.divider()

# 3. Live Recalculated Output Cards
st.subheader("2. Live Recalculated Outputs")
col1, col2 = st.columns(2)
col1.metric("Year 3 (2029F) Revenue", f"${rev2029:,.0f}")
col2.metric("Year 3 Gross Profit", f"${gp2029:,.0f}")

col3, col4 = st.columns(2)
col3.metric("Year 3 EBITDA", f"${ebitda2029:,.0f}", f"{ebitda_margin:.1f}% Margin")
col4.metric("Terminal Enterprise Value (@ Exit)", f"${tv:,.0f}")

st.divider()

# 4. Dynamic Sensitivity Chart Output
st.subheader("3. Dynamic Sensitivity Matrix Chart")

# Generate 2D Matrix for Heatmap Chart
multiples = [2.0, 3.0, 4.0, 5.0, 6.0]
rev_targets = [1000000, 1300000, 1626975, 2000000, 2500000]

ebitda_grid = np.zeros((len(multiples), len(rev_targets)))
for i, m in enumerate(multiples):
    for j, r in enumerate(rev_targets):
        r29_c = r * 10.379904
        gp29_c = r29_c * gm
        eb29_c = gp29_c - 421959.80
        ebitda_grid[i, j] = eb29_c / 1e6

fig, ax = plt.subplots(figsize=(10, 5))
fig.patch.set_facecolor('#FFFFFF')
ax.set_facecolor('#FFFFFF')

im = ax.imshow(ebitda_grid, cmap='YlGnBu', aspect='auto')

rev_labels = ['$1.00M', '$1.30M', '$1.63M\n(Base)', '$2.00M', '$2.50M']
mult_labels = ['2.0x EV', '3.0x (Base)', '4.0x EV', '5.0x EV', '6.0x EV']

ax.set_xticks(np.arange(len(rev_labels)))
ax.set_yticks(np.arange(len(mult_labels)))
ax.set_xticklabels(rev_labels, color='#0A3841', fontweight='bold')
ax.set_yticklabels(mult_labels, color='#0A3841', fontweight='bold')

ax.set_xlabel('Year 1 (2027F) Revenue Target', color='#0A3841', fontweight='bold')
ax.set_ylabel('Exit EV/EBITDA Multiple', color='#0A3841', fontweight='bold')

for i in range(len(multiples)):
    for j in range(len(rev_targets)):
        val = ebitda_grid[i, j]
        ax.text(j, i, f"${val:.2f}M", ha="center", va="center", 
                color='#0A3841' if val < 5 else '#FFFFFF', fontweight='bold')

cbar = plt.colorbar(im, ax=ax)
cbar.set_label('Year 3 EBITDA ($M)', color='#0A3841', fontweight='bold')

st.pyplot(fig)
