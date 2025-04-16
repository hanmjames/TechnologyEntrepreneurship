import streamlit as st
from PIL import Image
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

st.set_page_config(page_title="PensionIQ - Fee Analysis", layout="wide")

logo = Image.open("logo.png")

col1, col2 = st.columns([1, 10])
with col1:
    st.image(logo, width=70)
with col2:
    st.markdown(
        """
        <div style='display: flex; align-items: center; height: 100%; white-space: nowrap; overflow: hidden;'>
            <h1 style='margin: 0; padding: 0; color: #1E9E6B; font-size: 30px;'>
                PensionIQ: Fee Breakdown & AI Insights
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

st.markdown("See how fees impact your retirement and explore smarter fund options.")

if "pension_data" in st.session_state:
    pensionDf = st.session_state["pension_data"]

    st.subheader("Fund Details")
    st.dataframe(pensionDf)

    pensionDf["Fee Cost (20Y)"] = pensionDf["Fund Value"] * ((pensionDf["Annual Fee %"] / 100) * 20)

    st.subheader("Estimated Fee Cost Over 20 Years")
    st.dataframe(pensionDf[["Fund Name", "Annual Fee %", "Fund Value", "Fee Cost (20Y)"]])

    feeFigure = px.bar(pensionDf, x="Fund Name", y="Fee Cost (20Y)",
                     title="Projected 20-Year Cost of Fees per Fund",
                     color="Fund Name", text="Fee Cost (20Y)")
    st.plotly_chart(feeFigure)

    st.subheader("Growth vs. Fees")
    fig_bubble = px.scatter(pensionDf, x="Annual Fee %", y="Growth %", size="Fund Value",
                            color="Fund Name", hover_name="Fund Name",
                            title="Fund Growth vs. Fees")
    st.plotly_chart(fig_bubble)

    st.subheader("Fund Clustering (AI Insight)")
    features = pensionDf[["Annual Fee %", "Growth %", "Fund Value"]]
    X_scaled = StandardScaler().fit_transform(features)

    kmeans = KMeans(n_clusters=3, random_state=0)
    pensionDf["Cluster"] = kmeans.fit_predict(X_scaled)

    fig_cluster = px.scatter(pensionDf, x="Annual Fee %", y="Growth %",
                             color=pensionDf["Cluster"].astype(str), size="Fund Value",
                             hover_name="Fund Name",
                             title="AI-Identified Clusters of Funds")
    st.plotly_chart(fig_cluster)

else:
    st.warning("⚠️ Please upload your CSV file on the homepage before visiting this page.")
    st.stop()

st.markdown("---")
if st.button("Get Recommendations"):
    st.switch_page("pages/Recommendations.py")
