import streamlit as st
import firebase_config

# Page Header
st.markdown("""
<div style="background: linear-gradient(135deg, #1e293b, #0f172a); padding: 2rem; border-radius: 12px; border: 1px solid #1e293b; margin-bottom: 2rem; text-align: center;">
    <h1 style="color: #38bdf8; margin: 0; font-size: 2.2rem; font-weight: 700; letter-spacing: 0.5px;">🌌 Impact & Investment Evaluation</h1>
    <p style="color: #94a3b8; font-size: 1.1rem; margin: 0.75rem 0 0 0;">ระบบประเมินผลลัพธ์และผลกระทบทางเศรษฐกิจ สังคม และสิ่งแวดล้อม จากผลงานวิจัยและพัฒนา</p>
</div>
""", unsafe_allow_html=True)

# Grid Layout for Features
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <span class="icon">📋</span>
        <h3>1. ประเมินความพร้อม</h3>
        <p>ทำ Checklist เพื่อวิเคราะห์ความพร้อมของโครงการวิจัยตามเกณฑ์ประเมินเบื้องต้น ก่อนดำเนินการคิดคำนวณมูลค่าผลกระทบจริง</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("เข้าสู่หน้า Checklist ➡️", key="btn_home_checklist", use_container_width=True):
        st.switch_page("pages/checklist.py")

with col2:
    st.markdown("""
    <div class="feature-card">
        <span class="icon">🧮</span>
        <h3>2. คำนวณ Pre-Impact</h3>
        <p>เครื่องมือกรอกตัวเลขและสูตรคำนวณอัตโนมัติ 10 ด้าน เพื่อประเมินมูลค่า Pre-Impact และ Pre-Investment พร้อมระบบบันทึกแบบร่าง (Draft) บนคลาวด์</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("เข้าสู่หน้าเครื่องประเมิน ➡️", key="btn_home_calculator", use_container_width=True):
        st.switch_page("pages/calculator.py")

with col3:
    st.markdown("""
    <div class="feature-card">
        <span class="icon">📊</span>
        <h3>3. แผงควบคุมสถิติ</h3>
        <p>วิเคราะห์ข้อมูลภาพรวม สถิติผู้ประเมิน มูลค่าผลกระทบจำแนกตามรายสาขาวิจัยและสังกัด อัปเดตแบบเรียลไทม์ผ่านกราฟิกสุดพรีเมียม</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("เข้าสู่หน้า Dashboard ➡️", key="btn_home_dashboard", use_container_width=True):
        st.switch_page("pages/dashboard.py")

st.markdown("---")

# Quick Stats Card
st.markdown("<h3 style='color:#38bdf8;'>📈 สถิติการใช้งานระบบขณะนี้</h3>", unsafe_allow_html=True)
stats = firebase_config.get_dashboard_stats() if firebase_config.is_db_connected() else None

if stats:
    total_evals = stats["total"]
    st.markdown(f"""
    <div class="total-users-card" style="margin-top: 1rem;">
        <div class="total-icon">🚀</div>
        <div class="total-info">
            <span class="total-number">{total_evals} รายการ</span>
            <span class="total-label">จำนวนโครงการวิจัยที่ได้รับการประเมิน Pre-Impact บนระบบ</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    # Local demo mode placeholder
    st.markdown("""
    <div class="total-users-card" style="margin-top: 1rem; background: linear-gradient(135deg, #1e293b, #334155); box-shadow: none;">
        <div class="total-icon">🔌</div>
        <div class="total-info">
            <span class="total-number">ทำงานแบบ Offline</span>
            <span class="total-label">ไม่พบคอนฟิกเกอร์เชื่อมต่อ Firebase ข้อมูลจะถูกบันทึกชั่วคราวใน Local Session เท่านั้น</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# User Guide / Notice Box
st.markdown("""
<div style="background-color: rgba(56, 189, 248, 0.05); border-left: 4px solid #38bdf8; padding: 1.25rem; border-radius: 6px; margin-top: 2rem;">
    <h4 style="color: #38bdf8; margin-top: 0;">💡 คำชี้แจงในการใช้ระบบ</h4>
    <p style="font-size: 0.95rem; line-height: 1.6; margin: 0; color: #cbd5e1;">
        ระบบนี้ได้รับการพัฒนาเพื่อช่วยนักวิจัยและผู้ประเมินโครงการวิจัยและพัฒนาของ <b>สวทช. (NSTDA)</b> 
        ในการวิเคราะห์และจัดทำเอกสารความพร้อมรวมถึงตัวเลขประมาณการเบื้องต้นของผลลัพธ์เชิงเศรษฐกิจและสังคม (Pre-Impact) 
        และเงินลงทุนร่วมจากผู้ใช้ประโยชน์ (Pre-Investment) อย่างเป็นระบบตามระเบียบวิธีประเมินสากล
    </p>
</div>
""", unsafe_allow_html=True)
