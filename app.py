import streamlit as st
import pandas as pd
from datetime import datetime

# ---------- CONFIG ----------
st.set_page_config(page_title="AnalyticsBot", page_icon="👩‍💻")
st.title("📊 AnalyticsAssistant – KPI Tracker & Report")

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

# ---------- STEP 0: GREETING ----------
if st.session_state.step == 0:
    st.write("👋 Hey there! Ready to log this month’s KPIs?")
    if st.button("Yes, let's do it"):
        st.session_state.step += 1

# ---------- STEP 1: INPUT ----------
elif st.session_state.step == 1:
    st.subheader("📥 Enter Monthly KPIs")

    DAU = st.number_input("👥 DAU (Daily Active Users)", min_value=0)
    MAU = st.number_input("👥 MAU (Monthly Active Users)", min_value=0)
    Churn = st.number_input("📉 Churn Rate (%)", min_value=0.0)
    Insights = st.text_area("🧠 Monthly Insights", placeholder="What happened this month?")

    if st.button("Save This Month’s Data"):
        now = datetime.now()
        Month = now.strftime("%B")
        Year = now.year

        save_data(Month, Year, DAU, MAU, Churn, Insights)

        st.success(f"✅ Saved data for {Month} {Year}")
        st.session_state.step += 1

# ---------- STEP 2: REPORT OPTIONS ----------
elif st.session_state.step == 2:
    st.subheader("📊 View KPI Reports")

    if st.button("📅 View This Month’s Summary"):
        df = pd.read_csv(DATA_FILE)
        now = datetime.now()
        month = now.strftime("%B")
        year = now.year

        current = df[(df["Month"] == Month) & (df["Year"] == Year)]

        if not current.empty:
            st.write(f"📅 **{Month} {Year} Summary**")
            st.write(current[["DAU", "MAU", "Churn"]])
            st.write("📝 **Insights:**")
            st.info(current["Insights"].values[0] if current["Insights"].values[0] else "_No insights provided._")
        else:
            st.warning("No data found for this month.")

    if st.button("📈 View Last 12 Months Summary"):
        df = pd.read_csv(DATA_FILE)
        df["Date"] = pd.to_datetime(df["Month"] + " " + df["Year"].astype(str))
        df = df.sort_values("Date", ascending=True).tail(12)

        st.write("📅 **KPI Trends – Last 12 Months**")
        st.bar_chart(df.set_index("Date")[["DAU", "MAU", "Churn"]])

    st.button("Start Over", on_click=lambda: st.session_state.update(step=0, kpi_data={}, insights=""))
