import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ---------- CONFIG ----------
st.set_page_config(page_title="Prod-Pop!", page_icon="✨")
st.markdown("<h1 style='text-align: center;'>✨ Prod-Pop!</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: grey;'>Hi, I'm Clarity – your assistant to help log KPIs and generate reports with clarity and ease.</p>", unsafe_allow_html=True)

DATA_FILE = "kpi_data.csv"

# ---------- INIT ----------
if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.kpi_data = {}

# ---------- SAVE FUNCTION ----------
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
    st.markdown("### What would you like to do?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Log New Month Data"):
            st.session_state.step = 1
    with col2:
        if st.button("📊 View Reports"):
            st.session_state.step = 5

# ---------- STEP 1: INPUT DATA ----------
elif st.session_state.step == 1:
    st.subheader("📥 Enter Monthly KPIs")
    month = st.selectbox("📆 Select Month", [datetime(2000, m, 1).strftime('%B') for m in range(1, 13)])
    year = st.number_input("📅 Enter Year", min_value=2000, max_value=datetime.now().year, value=datetime.now().year)
    DAU = st.number_input("👥 DAU (Daily Active Users)", min_value=0)
    MAU = st.number_input("👥 MAU (Monthly Active Users)", min_value=0)
    Churn = st.number_input("📉 Churn Rate (%)", min_value=0.0)
    Insights = st.text_area("🧠 Monthly Insights", placeholder="What was this month like?")

    if st.button("💾 Save Data"):
        save_data(month, year, DAU, MAU, Churn, Insights)
        st.success(f"✅ Saved data for {month} {year}")
        st.session_state.last_saved_month = month
        st.session_state.last_saved_year = year
        st.session_state.step = "saved"  # Temporary step to show buttons

elif st.session_state.step == "saved":
    st.markdown("### ✅ Data saved. What would you like to do next?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 View This Report"):
            st.session_state.step = 2
    with col2:
        if st.button("⬅️ Back to Home"):
            st.session_state.step = 0

# ---------- STEP 2: SHOW REPORT FOR SAVED MONTH ----------
elif st.session_state.step == 2:
    st.subheader(f"📄 Report for {st.session_state.last_saved_month} {st.session_state.last_saved_year}")
    df = pd.read_csv(DATA_FILE)
    summary = df[(df["Month"] == st.session_state.last_saved_month) & (df["Year"] == st.session_state.last_saved_year)]
    st.write(summary[["DAU", "MAU", "Churn"]])
    st.info(summary["Insights"].values[0] if summary["Insights"].values[0] else "_No insights provided._")

    st.bar_chart(summary[["DAU", "MAU", "Churn"]].T)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button("⬇️ Download This Report", data=summary.to_csv(index=False), file_name="monthly_kpi_report.csv")
    with col2:
        if st.button("🔁 Log Another Month"):
            st.session_state.step = 1
    with col3:
        if st.button("⬅️ Back to Home"):
            st.session_state.step = 0


# ---------- STEP 5: REPORT OPTIONS ----------
elif st.session_state.step == 5:
    st.subheader("📊 Choose Report Range")
    col1, col2, col3 = st.columns(3)
    if col1.button("📅 Past 3 Months"):
        st.session_state.report_range = 3
        st.session_state.step = 6
    if col2.button("📅 Past 6 Months"):
        st.session_state.report_range = 6
        st.session_state.step = 6
    if col3.button("📅 Past 12 Months"):
        st.session_state.report_range = 12
        st.session_state.step = 6
    if st.button("⬅️ Back to Home"):
        st.session_state.step = 0

# ---------- STEP 6: GENERATE PERIOD REPORT ----------
elif st.session_state.step == 6:
    st.subheader(f"📈 KPI Trends – Last {st.session_state.report_range} Months")

    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df["Date"] = pd.to_datetime(df["Month"] + " " + df["Year"].astype(str))
        df = df.sort_values("Date", ascending=True).tail(st.session_state.report_range)

        st.write(df[["Month", "Year", "DAU", "MAU", "Churn", "Insights"]])
        st.bar_chart(df.set_index("Date")[["DAU", "MAU", "Churn"]])

        col1, col2 = st.columns(2)
        with col1:
            st.download_button("⬇️ Download Report", data=df.to_csv(index=False), file_name=f"kpi_report_last_{st.session_state.report_range}_months.csv")
        with col2:
            if st.button("⬅️ Back to Reports"):
                st.session_state.step = 5
    else:
        st.warning("⚠️ No KPI data found. Please log some data first.")
        if st.button("⬅️ Back to Home"):
            st.session_state.step = 0
