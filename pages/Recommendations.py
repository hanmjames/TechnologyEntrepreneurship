import streamlit as st
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from fpdf import FPDF
from io import BytesIO
import plotly.express as px
import yfinance as yf
from PIL import Image

st.set_page_config(page_title="PensionIQ - Recommendations", layout="wide")

logo = Image.open("logo.png")
col1, col2 = st.columns([1, 10])
with col1:
    st.image(logo, width=70)
with col2:
    st.markdown(
        """
        <div style='display: flex; align-items: center; height: 100%; white-space: nowrap; overflow: hidden;'>
            <h1 style='margin: 0; padding: 0; color: #1E9E6B; font-size: 30px;'>
                PensionIQ: Personalized AI Fund Recommendations
            </h1>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("""
    <style>
    h2, h3 {
        color: #22B573;
    }
    .stButton>button {
        background-color: #22B573;
        color: white;
        border-radius: 8px;
        padding: 8px 16px;
        font-size: 16px;
        font-weight: 600;
    }
    .stMarkdown, .stDataFrame {
        background-color: #0F2E2E !important;
        padding: 10px;
        border-radius: 10px;
        color: #E6FFF8 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("Using AI to find better-performing, lower-cost pension fund alternatives.")

if "pension_data" in st.session_state:
    df = st.session_state["pension_data"]
else:
    st.warning("⚠️ Please upload your CSV file on the homepage before visiting this page.")
    st.stop()

features = df[["Annual Fee %", "Growth %"]]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(features)
model = NearestNeighbors(n_neighbors=2)
model.fit(X_scaled)

internalFundRecs = []
for idx, row in df.iterrows():
    distances, indices = model.kneighbors([X_scaled[idx]])
    for neighborIdx in indices[0][1:]:
        rec = df.iloc[neighborIdx]
        if rec["Annual Fee %"] < row["Annual Fee %"] and rec["Growth %"] >= row["Growth %"]:
            internalFundRecs.append({
                "Fund Name": row["Fund Name"], "Suggested Internal Fund": rec["Fund Name"], "Alt. Fee % (Internal)": rec["Annual Fee %"], "Alt. Growth % (Internal)": rec["Growth %"]
            })

internalDataFrama = pd.DataFrame(internalFundRecs)

tickers = ["VWRL.L", "VUSA.L", "AGBP.L", "BNDX", "SSAC.L", "ESGE", "IWDA.AS", "ARKK", "VIG", "AOR"]
realFunds = []

for ticker in tickers:
    try:
        fund = yf.Ticker(ticker)
        info = fund.info
        name = info.get("longName", ticker)
        fee = info.get("netExpenseRatio")
        hist = fund.history(period="3y")
        if fee is not None and not hist.empty:
            fee_percent = round(fee, 2)
            start_price = hist["Close"].iloc[0]
            end_price = hist["Close"].iloc[-1]
            growth = ((end_price - start_price) / start_price) / 3
            realFunds.append({
                "Fund Name": name, "Ticker": ticker, "Annual Fee %": fee_percent, "Growth %": round(growth * 100, 2)})
    except Exception:
        continue

realDataFrame = pd.DataFrame(realFunds)
realFundRecs = []

for x, row in df.iterrows():
    matches = []
    for x, real in realDataFrame.iterrows():
        feeDiff = row["Annual Fee %"] - real["Annual Fee %"]
        growthDiff = real["Growth %"] - row["Growth %"]
        score = (growthDiff * 2) + (feeDiff * 1)
        matches.append((score, real))
    matches.sort(reverse=True, key=lambda x: x[0])
    bestScore, best = matches[0]
    if bestScore > 1:
        realFundRecs.append({
            "Fund Name": row["Fund Name"], "Suggested Real Fund": best["Fund Name"], "Alt. Fee % (Real)": best["Annual Fee %"], "Alt. Growth % (Real)": best["Growth %"]})

realDataFrame_rec = pd.DataFrame(realFundRecs)
merged = df[["Fund Name", "Annual Fee %", "Growth %", "Fund Value"]].copy()
merged = pd.merge(merged, internalDataFrama, on="Fund Name", how="left")
merged = pd.merge(merged, realDataFrame_rec, on="Fund Name", how="left")
merged = merged.dropna(subset=["Suggested Internal Fund", "Suggested Real Fund"], how="all")
st.subheader("Combined Fund Recommendations")
st.dataframe(merged)

chartData = []

for x, row in merged.iterrows():
    baseFundValue = row["Fund Value"]
    chartData.append({"Fund": row["Fund Name"], "Type": "Current", "Annual Fee %": row["Annual Fee %"], "Growth %": row["Growth %"], "20Y Fee Cost": row["Annual Fee %"] * baseFundValue * 20 / 100})
    if pd.notna(row["Suggested Internal Fund"]):
        chartData.append({"Fund": row["Fund Name"], "Type": "Internal", "Annual Fee %": row["Alt. Fee % (Internal)"], "Growth %": row["Alt. Growth % (Internal)"], "20Y Fee Cost": row["Alt. Fee % (Internal)"] * baseFundValue * 20 / 100})
    if pd.notna(row["Suggested Real Fund"]):
        chartData.append({"Fund": row["Fund Name"], "Type": "Real", "Annual Fee %": row["Alt. Fee % (Real)"], "Growth %": row["Alt. Growth % (Real)"],"20Y Fee Cost": row["Alt. Fee % (Real)"] * baseFundValue * 20 / 100})

viz = pd.DataFrame(chartData)
st.subheader("Visual Comparison of Recommendations")
st.plotly_chart(px.bar(viz, x="Fund", y="Annual Fee %", color="Type", barmode="group", title="Annual Fee Comparison"))
st.plotly_chart(px.bar(viz, x="Fund", y="Growth %", color="Type", barmode="group", title="Growth Rate Comparison"))
st.plotly_chart(px.bar(viz, x="Fund", y="20Y Fee Cost", color="Type", barmode="group", title="Projected 20-Year Fee Cost"))

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", "B", 14)
pdf.cell(0, 10, "PensionIQ Recommendation Summary", ln=True, align="C")
pdf.ln(10)
pdf.set_font("Arial", "", 12)
for x, row in merged.iterrows():
    int_rec = row["Suggested Internal Fund"] if pd.notna(row["Suggested Internal Fund"]) else "None"
    ext_rec = row["Suggested Real Fund"] if pd.notna(row["Suggested Real Fund"]) else "None"
    pdf.multi_cell(0, 10, f"Fund: {row['Fund Name']}\n"
                          f"Internal Recommendation: {int_rec}\n"
                          f"Real-World Recommendation: {ext_rec}\n")
    pdf.ln(1)

buffer = BytesIO()
buffer.write(pdf.output(dest='S').encode('latin1'))
buffer.seek(0)
st.download_button("Download Recommendation Report (PDF)", buffer, "PensionIQ_Recommendation_Summary.pdf", mime="application/pdf")

csv = merged.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Recommendation Report (CSV)",
    data=csv,
    file_name="PensionIQ_Recommendation_Summary.csv",
    mime="text/csv"
)

