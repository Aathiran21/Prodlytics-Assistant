import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ---------- CONFIG ----------
st.set_page_config(page_title="Prod-Pop!", page_icon="✨")
st.markdown("<h1 style='text-align: center;'>📊 Prod-Pop!</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: grey;'>Track KPIs monthly, view trends, and download reports easily.</p>", unsafe_allow_html=True)

DATA_FILE = "kpi_data.csv"

# ---------- INIT ----------
if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.kpi_data = {}
    st.session_state.insights = ""

# ---------- FUNCTION: SAVE DATA ----------
def save_data(Month, Year, DAU, MAU, Churn, Insights):
    new_row = {
        "Month": Month,
        "Year": Year,
        "DAU": DAU,
        "MAU": MAU,
        "Churn": Churn,
        "Insights": Insights
    }
    try:
        df = pd.read_csv(DATA_FILE)
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    except FileNotFoundError:
        df = pd.DataFrame([new_row])
    df.to_csv(DATA_FILE, index=False)

# ---------- STEP 0: WELCOME ----------
if st.session_state.step == 0:
    st.success("👋 Welcome to Prod-Pop! 👩‍💻 I am Clarity  your assistant and I am here to help you log KPIs and generate insights monthly.")
    if st.button("Start Logging"):
        st.session_state.step += 1

# ---------- STEP 1: INPUT ----------
elif st.session_state.step == 1:
    st.subheader("📥 Enter Monthly KPIs")
    DAU = st.number_input("👥 DAU (Daily Active Users)", min_value=0)
    MAU = st.number_input("👥 MAU (Monthly Active Users)", min_value=0)
    Churn = st.number_input("📉 Churn Rate (%)", min_value=0.0)
    Insights = st.text_area("🧠 Monthly Insights", placeholder="What was this month like?")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back"):
            st.session_state.step = 0
    with col2:
        if st.button("💾 Save This Month’s Data"):
            now = datetime.now()
            Month = now.strftime("%B")
            Year = now.year
            save_data(Month, Year, DAU, MAU, Churn, Insights)
            st.success(f"✅ Saved data for {Month} {Year}")
            st.session_state.step += 1

# ---------- STEP 2: VIEW REPORTS ----------
elif st.session_state.step == 2:
    st.subheader("📊 View KPI Reports")

    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📅 View This Month’s Summary"):
                now = datetime.now()
                Month = now.strftime("%B")
                Year = now.year
                current = df[(df["Month"] == Month) & (df["Year"] == Year)]
                if not current.empty:
                    st.write(f"📅 **{Month} {Year} Summary**")
                    st.write(current[["DAU", "MAU", "Churn"]])
                    st.markdown("📝 **Insights:**")
                    st.info(current["Insights"].values[0] if current["Insights"].values[0] else "_No insights provided._")
                else:
                    st.warning("⚠️ No data found for this month.")

        with col2:
            if st.button("📈 View Last 12 Months Summary"):
                df["Date"] = pd.to_datetime(df["Month"] + " " + df["Year"].astype(str))
                df = df.sort_values("Date", ascending=True).tail(12)
                st.write("📅 **KPI Trends – Last 12 Months**")
                st.bar_chart(df.set_index("Date")[["DAU", "MAU", "Churn"]])

        # Download and Clear Buttons
        st.markdown("---")
        col3, col4, col5 = st.columns(3)
        with col3:
            if st.download_button("⬇️ Download Report", data=df.to_csv(index=False), file_name="kpi_report.csv"):
                st.success("📥 Report downloaded!")
        with col4:
            if st.button("🗑️ Clear All Data"):
                os.remove(DATA_FILE)
                st.warning("🚨 All KPI data cleared.")
                st.session_state.step = 0
        with col5:
            if st.button("⬅️ Back"):
                st.session_state.step = 1
    else:
        st.warning("No data available. Please log KPIs first.")
        if st.button("⬅️ Back"):
            st.session_state.step = 1
