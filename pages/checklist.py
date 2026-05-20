import streamlit as st

st.markdown("""
<div class="section-header">
    <span class="section-header-title">📋 Checklist ความพร้อมในการประเมินผลงานวิจัย</span>
</div>
""", unsafe_allow_html=True)

# Stepper UI
def render_stepper(current_step):
    steps = [
        ("📋 1. Checklist ความพร้อม", 1),
        ("🧮 2. เครื่องคำนวณ Pre-Impact", 2),
        ("📤 3. ส่งและพิมพ์รายงาน", 3)
    ]
    cols = st.columns(len(steps))
    for i, (label, step_num) in enumerate(steps):
        is_active = step_num == current_step
        color = "#3b82f6" if is_active else "#64748b"
        weight = "bold" if is_active else "normal"
        border = f"2px solid {color}" if is_active else "1px solid #334155"
        bg = "rgba(59, 130, 246, 0.15)" if is_active else "transparent"
        
        cols[i].markdown(f"""
        <div style="border: {border}; background-color: {bg}; padding: 0.6rem; border-radius: 8px; text-align: center;">
            <span style="font-weight: {weight}; color: {color}; font-size: 0.9rem;">{label}</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

render_stepper(1)

st.write("กรุณาทำแบบสำรวจความพร้อมเบื้องต้นของโครงการวิจัยและพัฒนา เพื่อพิจารณาความเหมาะสมในการประเมินมูลค่า Pre-Impact / Pre-Investment")

# Track Checklist State locally in session state
if "chk_a1" not in st.session_state:
    st.session_state.chk_a1 = False
if "chk_a2" not in st.session_state:
    st.session_state.chk_a2 = False
if "chk_b1" not in st.session_state:
    st.session_state.chk_b1 = False
if "chk_b2" not in st.session_state:
    st.session_state.chk_b2 = False
if "chk_b3" not in st.session_state:
    st.session_state.chk_b3 = False
if "chk_b4" not in st.session_state:
    st.session_state.chk_b4 = False
if "chk_b5" not in st.session_state:
    st.session_state.chk_b5 = False
if "chk_b5_text" not in st.session_state:
    st.session_state.chk_b5_text = ""

# Section 1: หลักเกณฑ์เบื้องต้น
st.markdown("### 1. หลักเกณฑ์เบื้องต้น (Basic Criteria)")

with st.container(border=True):
    st.session_state.chk_a1 = st.checkbox(
        "ผู้รับบริการ/ผู้รับประโยชน์เป็นหน่วยงานภายนอก สวทช.",
        value=st.session_state.chk_a1,
        help="โครงการวิจัยต้องมีการนำไปใช้หรือส่งมอบประโยชน์ให้กับบุคคล/องค์กรภายนอก สวทช."
    )
    
    st.session_state.chk_a2 = st.checkbox(
        "มีผู้ใช้ผลงานมาแล้ว ≥ 1 ปี",
        value=st.session_state.chk_a2,
        help="ผลงานวิจัยต้องผ่านกระบวนการใช้งาน/ส่งมอบแล้วเป็นเวลาอย่างน้อย 1 ปี"
    )
    
    if st.session_state.chk_a2:
        st.info("""
        ℹ️ **แบบฟอร์มขอใช้บริการคิด Impact สำหรับผลงานใหม่/โครงการใหม่:**
        ท่านสามารถคลิกเพื่อกรอกแบบฟอร์มเพื่อส่งข้อมูลเบื้องต้นให้ทีมงานได้ที่นี่: 
        [แบบฟอร์มบันทึกข้อมูลเตรียมประเมินผลกระทบ](https://docs.google.com/forms/d/e/1FAIpQLScwlAAKrQXUrOwPZRMgnIdN4C8DKjJCc-p_unsezdtQ7tELjg/viewform)
        """)

# Section 2: ลักษณะของผลงาน/บริการ
st.markdown("### 2. ลักษณะของผลงาน/บริการ (Project/Service Characteristics)")

with st.container(border=True):
    st.session_state.chk_b1 = st.checkbox("ต้นแบบ/ผลิตภัณฑ์", value=st.session_state.chk_b1)
    if st.session_state.chk_b1:
        st.info("💡 **ตัวอย่างมิติผลประโยชน์ที่สามารถวัดได้:** กำไร/รายได้เพิ่ม, ลดค่าใช้จ่าย/ต้นทุน, ลดการนำเข้า, เพิ่มประสิทธิภาพการทำงาน, เกิดการลงทุนร่วม/ลงทุนเพิ่ม")
        
    st.session_state.chk_b2 = st.checkbox("แอปพลิเคชัน/แพลตฟอร์ม", value=st.session_state.chk_b2)
    if st.session_state.chk_b2:
        st.info("💡 **ตัวอย่างมิติผลประโยชน์ที่สามารถวัดได้:** กำไร/รายได้เพิ่ม, ลดค่าใช้จ่าย/ต้นทุน, ลดการนำเข้า, เพิ่มประสิทธิภาพการทำงาน, เกิดการลงทุนร่วม/ลงทุนเพิ่ม")
        
    st.session_state.chk_b3 = st.checkbox("จัดหลักสูตรฝึกอบรมแบบไม่มีค่าใช้จ่ายและมีผลงานประกอบ/กิจกรรมประกวดแข่งขัน", value=st.session_state.chk_b3)
    if st.session_state.chk_b3:
        st.info("💡 **ตัวอย่างมิติผลประโยชน์ที่สามารถวัดได้:** ทักษะความรู้เพิ่มขึ้น, ลดค่าใช้จ่าย, ความภาคภูมิใจ, ใช้เวลาว่างให้เกิดประโยชน์, เกิดการลงทุนเพิ่มเติม")
        
    st.session_state.chk_b4 = st.checkbox("จัดหลักสูตรฝึกอบรมแบบไม่มีค่าใช้จ่ายและไม่มีผลงานประกอบ / แบบมีค่าใช้จ่าย", value=st.session_state.chk_b4)
    if st.session_state.chk_b4:
        st.info("💡 **ตัวอย่างมิติผลประโยชน์ที่สามารถวัดได้:** กำไร/รายได้เพิ่ม, ลดค่าใช้จ่าย/ต้นทุน, เพิ่มประสิทธิภาพการทำงาน, เกิดการลงทุนร่วม/ลงทุนเพิ่ม")
        
    st.session_state.chk_b5 = st.checkbox("อื่น ๆ", value=st.session_state.chk_b5)
    if st.session_state.chk_b5:
        st.session_state.chk_b5_text = st.text_area(
            "ระบุลักษณะผลงานเพิ่มเติม:",
            value=st.session_state.chk_b5_text,
            placeholder="กรุณาระบุรายละเอียดลักษณะผลงานวิจัย..."
        )

# Calculation of Completion
sec1_complete = st.session_state.chk_a1 or st.session_state.chk_a2
sec2_complete = (
    st.session_state.chk_b1 or 
    st.session_state.chk_b2 or 
    st.session_state.chk_b3 or 
    st.session_state.chk_b4 or 
    (st.session_state.chk_b5 and len(st.session_state.chk_b5_text.strip()) > 0)
)

score = 0
if sec1_complete:
    score += 1
if sec2_complete:
    score += 1

progress_percent = score / 2.0

st.markdown("---")
st.markdown("### ความคืบหน้าการทำ Checklist")
st.progress(progress_percent)
st.write(f"ทำเสร็จสิ้น: {score} จาก 2 หมวด")

# Save status globally
if score == 2:
    st.session_state.checklist_passed = True
    st.session_state.checklist_data = {
        "chk_a1": st.session_state.chk_a1,
        "chk_a2": st.session_state.chk_a2,
        "chk_b1": st.session_state.chk_b1,
        "chk_b2": st.session_state.chk_b2,
        "chk_b3": st.session_state.chk_b3,
        "chk_b4": st.session_state.chk_b4,
        "chk_b5": st.session_state.chk_b5,
        "chk_b5_text": st.session_state.chk_b5_text if st.session_state.chk_b5 else ""
    }
    
    st.success("🎉 โครงการของท่านผ่านเกณฑ์ checklist ความพร้อมเรียบร้อยแล้ว!")
    st.markdown("""
    <div style="background-color: rgba(16, 185, 129, 0.1); border: 1px solid #10b981; border-radius: 8px; padding: 1.5rem; text-align: center; margin-top: 1rem; margin-bottom: 1.5rem;">
        <h4 style="color: #10b981; margin-top: 0;">🔓 เครื่องประเมินได้รับการปลดล็อคแล้ว</h4>
        <p style="font-size: 0.95rem; color: #cbd5e1; margin-bottom: 0;">ท่านสามารถย้ายไปยังเมนูเครื่องประเมินเพื่อดำเนินการคำนวณ Pre-Impact ได้ทันที</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Pulsating proceed button using switch_page
    if st.button("➡️ ดำเนินการต่อเข้าสู่เครื่องประเมิน (Proceed to Calculator)", type="primary", use_container_width=True):
        st.switch_page("pages/calculator.py")
else:
    st.session_state.checklist_passed = False
    st.warning("⚠️ โครงการของท่านยังไม่ผ่านเกณฑ์ checklist ความพร้อม (ต้องทำเครื่องหมายในทั้ง 2 หมวดให้ครบถ้วนก่อน)")
