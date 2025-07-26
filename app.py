import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

# ----------PDF function -----------
def generate_pdf(df, fig, title="KPI Report"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 0.25 * inch))

    # Save Matplotlib chart to image buffer
    img_buffer = BytesIO()
    fig.savefig(img_buffer, format='PNG', bbox_inches='tight')
    img_buffer.seek(0)
    elements.append(RLImage(img_buffer, width=6*inch, height=3*inch))
    elements.append(Spacer(1, 0.5 * inch))

    # Add table data
    text_data = df.to_string(index=False)
    elements.append(Paragraph("<b>Data Table</b>", styles['Heading2']))
    for line in text_data.split("\n"):
        elements.append(Paragraph(line.replace("  ", "&nbsp;&nbsp;&nbsp;&nbsp;"), styles['Code']))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ---------- CONFIG ----------
st.set_page_config(page_title="Prod-Pop!", page_icon="✨")
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
    st.markdown("<h1 style='text-align: center;'>✨ Prod-Pop!</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: orange;'>Hey there! Welcome to Prod-Pop! with Clarity. I'm Clarity – your assistant and I'm here to help you log KPIs and generate summary reports with ease.</p>", unsafe_allow_html=True)
    
    st.markdown("### What would you like to do?")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📝 Log New Month Data"):
            st.session_state.step = 1
    with col2:
        if st.button("📊 View Reports"):
            st.session_state.step = 5
    with col3:
        if st.button("🗑️ Delete Specific Month Data"):
            st.session_state.step = 7

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
        st.session_state.step = "saved"
    
    if st.button("⬅️ Back to Home"):
        st.session_state.step = 0

# ---------- STEP 1.5: POST SAVE OPTIONS ----------
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

        import matplotlib.pyplot as plt
        df_plot = df.set_index("Date")[["DAU", "MAU", "Churn"]]
        fig, ax = plt.subplots(figsize=(10, 5))

        if st.session_state.report_range == 3:
            df_plot.plot(kind="bar", ax=ax, color=["blue", "orange", "purple"], width=0.6)
            ax.set_title("📊 KPI Trends – Last 3 Months")
        else:
            df_plot.plot(kind="line", ax=ax, marker='o', color=["blue", "orange", "purple"])
            ax.set_title(f"📈 KPI Trends – Last {st.session_state.report_range} Months")

        ax.set_ylabel("Values")
        ax.set_xlabel("Date")
        ax.legend(title="Metrics")
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)

        # ✅ Aligned buttons in one row
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            st.download_button(
                "⬇️ Download CSV",
                data=df.to_csv(index=False),
                file_name=f"kpi_report_last_{st.session_state.report_range}_months.csv",
                mime="text/csv"
            )

        with col2:
            pdf_file = generate_pdf(df, fig, title=f"KPI Report – Last {st.session_state.report_range} Months")
            st.download_button(
                label="⬇️ Download PDF",
                data=pdf_file,
                file_name=f"kpi_report_last_{st.session_state.report_range}_months.pdf",
                mime="application/pdf"
            )

        with col3:
            if st.button("⬅️ Back to Reports"):
                st.session_state.step = 5

    else:
        st.warning("⚠️ No KPI data found. Please log some data first.")
        if st.button("⬅️ Back to Home"):
            st.session_state.step = 0

# ---------- STEP 7: DELETE A SPECIFIC MONTH ----------
elif st.session_state.step == 7:
    st.subheader("🗑️ Delete a Specific Month’s KPI Data")

    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)

        if len(df) == 0:
            st.info("📭 No data available to delete.")
            if st.button("⬅️ Back to Home"):
                st.session_state.step = 0
        else:
            df["Label"] = df["Month"] + " " + df["Year"].astype(str)
            selected_label = st.selectbox("📅 Select entry to delete", df["Label"].tolist())

            if st.button("❌ Delete Selected Entry"):
                df = df[df["Label"] != selected_label]
                df.drop(columns=["Label"], inplace=True)
                df.to_csv(DATA_FILE, index=False)
                st.success(f"✅ Deleted data for {selected_label}")

            # Show back button regardless of delete status
            if st.button("⬅️ Back to Home"):
                st.session_state.step = 0
    else:
        st.warning("⚠️ No data file found. Nothing to delete.")
        if st.button("⬅️ Back to Home"):
            st.session_state.step = 0
