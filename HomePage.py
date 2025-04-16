import streamlit as st
import pandas as pd
from PIL import Image

st.set_page_config(page_title="PensionIQ", layout="centered")

logo = Image.open("logo.png")

col1, col2 = st.columns([1, 6])
with col1:
    st.image(logo, width=100)
with col2:
    st.markdown(
        """<div style='display: flex; align-items: center; height: 100%;'>
               <h2 style='margin: 0; padding: 0; color: #1E9E6B;'>PensionIQ: Smart AI For A Secure Retirement</h2>
           </div>""",
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

with st.container():
    st.markdown("""
    <div style="padding: 20px; background-color: #0F2E2E; border-radius: 10px;">
        <h2>Smarter Pension Insights, Powered by AI.</h2>
        <p>Upload your pension data and get transparent, personalized analysis in seconds.</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload your pension statement (.csv)", type="csv")

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.session_state["pension_data"] = df
        st.success("File uploaded successfully!")
        st.dataframe(df.head())
        st.markdown("Use the sidebar or click below to continue.")
        if st.button("Get Fee Analysis"):
            st.switch_page("pages/FeeAnalysis.py")
    else:
        st.markdown("""
        <div style="padding: 10px; background-color: #A58B00; color: white; border-radius: 6px;">
            Please upload a .csv file to get started.
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.caption("© 2025 PensionIQ | Prototype Version")
