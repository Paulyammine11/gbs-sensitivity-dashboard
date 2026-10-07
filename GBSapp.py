import streamlit as st

st.set_page_config(page_title="GBS Acquisition Dashboard", layout="centered")

st.title("GBS Acquisition — Dynamic Sensitivity Simulator")
st.caption("Standalone Asset Level (Excludes Holdco Overheads & External Debt)")

# 3 Slider Controls
st.subheader("1. Input Driver Selectors")
rev2027 = st.slider("Year 1 (2027F) Revenue Target ($)", 1000000, 2500000, 1626975, step=25000)
gm = st.slider("Gross Margin % Target", 20.0, 45.0, 25.43, step=0.5) / 100.0
mult = st.slider("Exit EV / EBITDA Valuation Multiple", 2.0, 6.0, 3.0, step=0.25)

# Calculations
rev2029 = rev2027 * 10.379904
gp2029 = rev2029 * gm
ebitda2029 = gp2029 - 421959.80
ebitda_margin = (ebitda2029 / rev2029) * 100.0
tv = max(0.0, ebitda2029 * mult)

st.divider()

# Live Cards
st.subheader("2. Live Recalculated Outputs")
col1, col2 = st.columns(2)
col1.metric("Year 3 (2029F) Revenue", f"${rev2029:,.0f}")
col2.metric("Year 3 Gross Profit", f"${gp2029:,.0f}")

col3, col4 = st.columns(2)
col3.metric("Year 3 EBITDA", f"${ebitda2029:,.0f}", f"{ebitda_margin:.1f}% Margin")
col4.metric("Terminal Enterprise Value (@ Exit)", f"${tv:,.0f}")
