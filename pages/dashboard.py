import streamlit as st
import pandas as pd
import plotly.express as px
import firebase_config
from datetime import datetime, timedelta
import random

# Page Title Header
st.markdown("""
<div class="section-header">
    <span class="section-header-title">📊 Dashboard สถิติผลลัพธ์และผลกระทบ</span>
</div>
""", unsafe_allow_html=True)

# 1. Mock Data Generator
def get_mock_data():
    orgs = ["NECTEC", "BIOTEC", "MTEC", "NANOTEC", "ENTEC", "NSTDA"]
    data = []
    
    start_date = datetime.now() - timedelta(days=90)
    # Seed random for consistency across dashboard refreshes if desired
    random.seed(42)
    for i in range(1, 36):
        days_offset = random.randint(0, 90)
        sub_date = start_date + timedelta(days=days_offset)
        org = random.choice(orgs)
        emp_id = f"EMP{random.randint(1000, 9999)}"
        proj_id = f"P-{random.randint(20, 26)}-{random.randint(10000, 99999)}"
        proj_name = f"โครงการวิจัยพัฒนาศักยภาพเชิงพาณิชย์ที่ {i}"
        
        impact = random.choice([0.0, random.uniform(100000, 15000000)])
        investment = random.choice([0.0, random.uniform(50000, 5000000)])
        if impact == 0 and investment == 0:
            impact = 500000.0
            
        data.append({
            "id": f"mock_doc_{i}",
            "employee_id": emp_id,
            "organization": org,
            "project_id": proj_id,
            "project_name": proj_name,
            "report_type": random.choice(["รายปี", "5 ปี"]),
            "total_impact": round(impact, 2),
            "total_investment": round(investment, 2),
            "submitted_at_str": sub_date.strftime("%Y-%m-%d %H:%M:%S"),
            "submitted_date": sub_date.date()
        })
    return data

# 2. Retrieve Data
db_stats = None
is_mock = False
evaluations_list = []

if firebase_config.is_db_connected():
    db_stats = firebase_config.get_dashboard_stats()
    if db_stats is not None:
        evaluations_list = db_stats["evaluations"]
        if db_stats["total"] > 0:
            st.sidebar.success(f"📊 เชื่อมต่อ Firebase สำเร็จ (พบ {db_stats['total']} รายการ)")
        else:
            st.sidebar.info("ℹ️ เชื่อมต่อ Firebase แล้ว แต่ยังไม่มีข้อมูลการประเมิน")
    else:
        st.sidebar.error("❌ เกิดข้อผิดพลาดในการดึงข้อมูลจาก Firebase")
        is_mock = True
else:
    st.sidebar.warning("⚠️ ไม่พบการเชื่อมต่อคลาวด์ (โหมด Offline)")
    is_mock = True

# Fallback to mock data ONLY if specifically in mock mode or failed to get anything
if is_mock and not evaluations_list:
    evaluations_list = get_mock_data()
    st.info("ℹ️ **ระบบจำลองสถิติ (Demo Mode):** กำลังแสดงข้อมูลจำลองเนื่องจากไม่ได้เชื่อมต่อฐานข้อมูลจริง")

# 3. Process into DataFrame
if evaluations_list:
    df = pd.DataFrame(evaluations_list)
    # Ensure numeric columns
    df["total_impact"] = pd.to_numeric(df.get("total_impact", 0), errors='coerce').fillna(0)
    df["total_investment"] = pd.to_numeric(df.get("total_investment", 0), errors='coerce').fillna(0)

    # Convert submitted_date to datetime for graphing sorting
    if "submitted_date" in df.columns:
        df["submitted_date"] = pd.to_datetime(df["submitted_date"])
        df = df.sort_values(by="submitted_date")
    else:
        # Fallback if no date column
        df["submitted_date"] = datetime.now().date()
else:
    st.warning("📭 ไม่พบข้อมูลการประเมินในระบบ")
    st.stop()

# 4. Metrics Grid
st.markdown("### 📈 ภาพรวมการประเมินโครงการวิจัย")
col_m1, col_m2, col_m3 = st.columns(3)

total_assessments = len(df)
sum_impact = df["total_impact"].sum()
sum_investment = df["total_investment"].sum()

col_m1.metric("จำนวนโครงการประเมินทั้งหมด", f"{total_assessments} โครงการ", delta=None)
col_m2.metric("มูลค่า Pre-Impact สัญญารวม", f"฿ {sum_impact:,.2f}", delta=None)
col_m3.metric("มูลค่า Pre-Investment ร่วมลงทุน", f"฿ {sum_investment:,.2f}", delta=None)

st.markdown("---")

# 5. Graphical Layout (Grid)
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.markdown("#### 🏢 สัดส่วนโครงการจำแนกตามหน่วยงาน/สังกัด")
    org_counts = df["organization"].value_counts().reset_index()
    org_counts.columns = ["organization", "count"]
    
    fig_org = px.pie(
        org_counts, 
        names="organization", 
        values="count", 
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_org.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#f8fafc',
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_org, use_container_width=True)

with col_g2:
    st.markdown("#### 💰 ผลตอบแทนทางตรงเฉลี่ยต่อหน่วยงาน")
    org_sums = df.groupby("organization")[["total_impact", "total_investment"]].sum().reset_index()
    
    fig_bars = px.bar(
        org_sums,
        x="organization",
        y=["total_impact", "total_investment"],
        barmode="group",
        labels={"value": "มูลค่าการประเมิน (บาท)", "organization": "หน่วยงาน"},
        color_discrete_map={"total_impact": "#10b981", "total_investment": "#f59e0b"}
    )
    fig_bars.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#f8fafc',
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor='#1e293b')
    )
    st.plotly_chart(fig_bars, use_container_width=True)

st.markdown("---")

# 6. Timeseries Line Chart
st.markdown("#### 📅 มูลค่าการประเมินสะสมจำแนกตามรายเวลา")
df_timeseries = df.groupby("submitted_date")[["total_impact", "total_investment"]].sum().cumsum().reset_index()

fig_line = px.line(
    df_timeseries,
    x="submitted_date",
    y=["total_impact", "total_investment"],
    labels={"submitted_date": "วันที่ส่งการประเมิน", "value": "มูลค่าสะสม (บาท)"},
    color_discrete_map={"total_impact": "#10b981", "total_investment": "#f59e0b"}
)
fig_line.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font_color='#f8fafc',
    xaxis=dict(showgrid=False),
    yaxis=dict(gridcolor='#1e293b')
)
st.plotly_chart(fig_line, use_container_width=True)

st.markdown("---")

# 7. Searchable Data Table
st.markdown("#### 🔎 รายการโครงการที่บันทึกไว้ในระบบ")

col_search, col_filter = st.columns([2, 1])
search_term = col_search.text_input("ค้นหาจากรหัสหรือชื่อโครงการ:", placeholder="พิมพ์ค้นหา...")
filter_org = col_filter.selectbox("กรองเฉพาะหน่วยงาน:", ["ทั้งหมด"] + sorted(list(df["organization"].unique())))

# Filter logic
filtered_df = df.copy()
if search_term:
    filtered_df = filtered_df[
        filtered_df["project_id"].str.contains(search_term, case=False, na=False) |
        filtered_df["project_name"].str.contains(search_term, case=False, na=False)
    ]
if filter_org != "ทั้งหมด":
    filtered_df = filtered_df[filtered_df["organization"] == filter_org]

# Format fields for readable table
table_df = filtered_df[[
    "project_id", 
    "project_name", 
    "organization", 
    "employee_id", 
    "submitted_at_str", 
    "total_impact", 
    "total_investment"
]].copy()

table_df.columns = [
    "รหัสโครงการ (ID)", 
    "ชื่อโครงการ", 
    "หน่วยงาน", 
    "ผู้ประเมิน", 
    "วันที่ประเมิน", 
    "Pre-Impact (บาท)", 
    "Pre-Investment (บาท)"
]

# Formatting column values
table_df["Pre-Impact (บาท)"] = table_df["Pre-Impact (บาท)"].map(lambda x: f"{x:,.2f}")
table_df["Pre-Investment (บาท)"] = table_df["Pre-Investment (บาท)"].map(lambda x: f"{x:,.2f}")

st.dataframe(table_df, use_container_width=True, hide_index=True)
