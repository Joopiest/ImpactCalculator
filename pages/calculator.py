import streamlit as st
import requests
import firebase_config
from datetime import datetime

# 1. Google Sheets Logging Endpoint
GOOGLE_SHEET_URL = 'https://script.google.com/macros/s/AKfycbzylM96oiM837gDntJnqvfR3t7GEKb8OBaD2VdFfUaQ93PQ0j0Hrc3EHiqayIgHWsQg/exec'

# 2. Activity Coefficient Mapping
COEFF_OPTIONS = {
    "รับจ้างวิจัย (1.0)": 1.0,
    "ร่วมวิจัย (1.0)": 1.0,
    "การอนุญาตให้ใช้สิทธิ (1.0)": 1.0,
    "รับจ้างผลิต (1.0)": 1.0,
    "การวิเคราะห์ทดสอบที่ใช้เนื้องานวิจัย (1.0)": 1.0,
    "ขยายผลงานวิจัย (1.0)": 1.0,
    "บริการโครงสร้างพื้นฐานด้านการคำนวณ (1.0)": 1.0,
    "บริการให้คำปรึกษา (0.6)": 0.6,
    "ร่วมลงทุนในนามนิติบุคคล (0.6)": 0.6,
    "บริการเครือข่ายสารสนเทศ/ฐานข้อมูล (0.3)": 0.3,
    "บริการวิเคราะห์ ทดสอบ รับรองคุณภาพ (0.3)": 0.3,
    "บริการฝึกอบรม/บ่มเพาะธุรกิจ (0.3)": 0.3,
    "เช่าพื้นที่ในอุทยานวิทยาศาสตร์/บริการโครงสร้างพื้นฐาน (0.3)": 0.3,
    "บริการเงินกู้ดอกเบี้ยต่ำ (0.3)": 0.3,
    "การรับรองโครงการวิจัยพัฒนาเพื่อลดหย่อนภาษี (0.3)": 0.3,
    "อื่น ๆ ระบุ... (0.0)": 0.0
}
COEFF_LABELS = list(COEFF_OPTIONS.keys())

TABS_LIST = [
    "📋 1. ข้อมูลโครงการ (Details)", 
    "📈 2. มิติผลกระทบ (Pre-Impact)", 
    "💰 3. มิติร่วมลงทุน (Pre-Investment)", 
    "💾 4. ส่งรายงาน & แบบร่าง (Submit & Drafts)"
]

# 3. Field defaults (module-level for reuse in snapshot/restore)
FIELD_DEFAULTS = {
    'b1': 0.0, 'b2': 0.0, 'b4': 100.0, 'b5': 1.0, 'b6': COEFF_LABELS[0], 'b7': 100.0,
    'c1': 0.0, 'c2': 0.0, 'c3': 0.0, 'c4': 0.0, 'c6': COEFF_LABELS[0], 'c7': 100.0,
    'd1': 0.0, 'd2': 0.0, 'd4': COEFF_LABELS[0], 'd5': 100.0,
    'e1': 0.0, 'e2': 8.0, 'e6': 0.0, 'e7': 0.0, 'e9': 1.0, 'e10': COEFF_LABELS[0], 'e11': 100.0,
    'f1': 0.0, 'f2': 100.0, 'f3': 100.0, 'f4': COEFF_LABELS[0], 'f5': 100.0,
    'g1': 1.0, 'g2': 0.0, 'g3': COEFF_LABELS[0], 'g4': 100.0,
    'h1': 0.0, 'h2': COEFF_LABELS[0], 'h3': 100.0,
    'i1': 0.0, 'i2': COEFF_LABELS[0], 'i3': 100.0,
    'j1': 0.0, 'j2': 100.0, 'j3': COEFF_LABELS[0], 'j4': 100.0,
    'k1': 0.0, 'k2': COEFF_LABELS[0], 'k3': 100.0
}

def sync_chk(section):
    """Callback to sync checkbox state to persistent shadow key immediately."""
    w_key = f"chk_{section}"
    p_key = f"_p_chk_{section}"
    if w_key in st.session_state:
        new_val = st.session_state[w_key]
        st.session_state[p_key] = new_val
        
        # Give user feedback
        status = "✅ เลือก" if new_val else "⚪ ยกเลิก"
        st.toast(f"{status} หมวด {section} แล้ว")
    
        # Handle exclusivity rules
        if section == 'B' and new_val:
            for s in ['C', 'D', 'E', 'F', 'G']:
                st.session_state[f"chk_{s}"] = False
                st.session_state[f"_p_chk_{s}"] = False
        elif section in ['C', 'D', 'E', 'F', 'G'] and new_val:
            st.session_state["chk_B"] = False
            st.session_state["_p_chk_B"] = False

def sync_val(field_id):
    """Callback to sync field value to persistent shadow key immediately."""
    w_key = f"val_{field_id}"
    p_key = f"_p_val_{field_id}"
    if w_key in st.session_state:
        st.session_state[p_key] = st.session_state[w_key]
        st.toast(f"💾 บันทึกค่า {field_id} สำเร็จ")

def init_states():
    # Debug logging
    try:
        import os
        import json
        log_file = "calculator_debug.log"
        safe_state = {}
        for k, v in st.session_state.items():
            if isinstance(v, (int, float, str, bool, list, dict)):
                safe_state[k] = v
            else:
                safe_state[k] = f"<{type(v).__name__}>"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"\n=== RERUN START ===\n")
            f.write(f"Active Tab at start: {st.session_state.get('active_calc_tab')}\n")
            f.write(f"Segmented Tab at start: {st.session_state.get('segmented_calc_tab')}\n")
            f.write(f"State keys: {json.dumps(safe_state, ensure_ascii=False)}\n")
    except Exception as e:
        pass

    if "active_calc_tab" not in st.session_state:
        st.session_state.active_calc_tab = TABS_LIST[0]
    if "segmented_calc_tab" not in st.session_state:
        st.session_state.segmented_calc_tab = TABS_LIST[0]
    if "last_active_tab" not in st.session_state:
        st.session_state.last_active_tab = TABS_LIST[0]

    if "projectId" not in st.session_state:
        st.session_state.projectId = ""
    if "projectName" not in st.session_state:
        st.session_state.projectName = ""
    if "reportType" not in st.session_state:
        st.session_state.reportType = "รายปี"
    
    # KRRN/KRID/Patent metadata fields
    for meta in ["meta_krrn", "meta_krid", "meta_krrn_related", "meta_patent_id"]:
        if meta not in st.session_state:
            st.session_state[meta] = ""
        
    # Initialize persistent keys (_p_) and restore widget keys if missing
    for s in ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']:
        p_key = f"_p_chk_{s}"
        w_key = f"chk_{s}"
        if p_key not in st.session_state:
            st.session_state[p_key] = False
        # Restore widget state ONLY if it's missing (e.g. after switching back to this tab)
        if w_key not in st.session_state:
            st.session_state[w_key] = st.session_state[p_key]
            
    for k, v in FIELD_DEFAULTS.items():
        p_key = f"_p_val_{k}"
        w_key = f"val_{k}"
        if p_key not in st.session_state:
            st.session_state[p_key] = v
        # Restore widget state ONLY if it's missing
        if w_key not in st.session_state:
            st.session_state[w_key] = st.session_state[p_key]

def snapshot_state():
    """Manual trigger to save all current widget values to persistent shadow keys."""
    for s in ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']:
        sync_chk(s)
    for k in FIELD_DEFAULTS:
        sync_val(k)

init_states()

def _pv(key, default=0.0):
    """Read field value: prefer persistent shadow key, fall back to widget key or default."""
    p_val = st.session_state.get(f"_p_val_{key}")
    if p_val is not None:
        return p_val
    w_val = st.session_state.get(f"val_{key}")
    return w_val if w_val is not None else default

def _pc(section):
    """Read checkbox state: prefer persistent shadow key, fall back to widget key or False."""
    p_val = st.session_state.get(f"_p_chk_{section}")
    if p_val is not None:
        return p_val
    w_val = st.session_state.get(f"chk_{section}")
    return w_val if w_val is not None else False



def compute_results():
    res = {}
    
    # B
    b1 = _pv('b1')
    b2 = _pv('b2')
    b3 = b1 - b2
    b4 = _pv('b4', 100.0)
    b5 = _pv('b5', 1.0)
    b6_lbl = _pv('b6', COEFF_LABELS[0])
    b6 = COEFF_OPTIONS.get(b6_lbl, 1.0)
    b7 = _pv('b7', 100.0)
    res["B"] = b3 * (b4 / 100.0) * b5 * b6 * (b7 / 100.0) if _pc('B') else 0.0
    
    # C
    c1 = _pv('c1')
    c2 = _pv('c2')
    c3 = _pv('c3')
    c4 = _pv('c4')
    c5 = (c3 - c4) - (c1 - c2)
    c6_lbl = _pv('c6', COEFF_LABELS[0])
    c6 = COEFF_OPTIONS.get(c6_lbl, 1.0)
    c7 = _pv('c7', 100.0)
    res["C"] = c5 * c6 * (c7 / 100.0) if _pc('C') else 0.0
    
    # D
    d1 = _pv('d1')
    d2 = _pv('d2')
    d3 = d1 - d2
    d4_lbl = _pv('d4', COEFF_LABELS[0])
    d4 = COEFF_OPTIONS.get(d4_lbl, 1.0)
    d5 = _pv('d5', 100.0)
    res["D"] = d3 * d4 * (d5 / 100.0) if _pc('D') else 0.0
    
    # E
    e1 = _pv('e1')
    e2 = _pv('e2', 8.0)
    e3 = e2 * 60.0
    e4 = e3 * 20.0
    e5 = e1 / e4 if e4 > 0 else 0.0
    e6 = _pv('e6')
    e7 = _pv('e7')
    e8 = e6 - e7
    e9 = _pv('e9', 1.0)
    e10_lbl = _pv('e10', COEFF_LABELS[0])
    e10 = COEFF_OPTIONS.get(e10_lbl, 1.0)
    e11 = _pv('e11', 100.0)
    res["E"] = e5 * e8 * e9 * e10 * (e11 / 100.0) if _pc('E') else 0.0
    
    # F
    f1 = _pv('f1')
    f2 = _pv('f2', 100.0)
    f3 = _pv('f3', 100.0)
    f4_lbl = _pv('f4', COEFF_LABELS[0])
    f4 = COEFF_OPTIONS.get(f4_lbl, 1.0)
    f5 = _pv('f5', 100.0)
    res["F"] = f1 * (f2 / 100.0) * (f3 / 100.0) * f4 * (f5 / 100.0) if _pc('F') else 0.0
    
    # G
    g1 = _pv('g1', 1.0)
    g2 = _pv('g2')
    g3_lbl = _pv('g3', COEFF_LABELS[0])
    g3 = COEFF_OPTIONS.get(g3_lbl, 1.0)
    g4 = _pv('g4', 100.0)
    res["G"] = g1 * g2 * g3 * (g4 / 100.0) if _pc('G') else 0.0
    
    # K
    k1 = _pv('k1')
    k2_lbl = _pv('k2', COEFF_LABELS[0])
    k2 = COEFF_OPTIONS.get(k2_lbl, 1.0)
    k3 = _pv('k3', 100.0)
    res["K"] = k1 * k2 * (k3 / 100.0) if _pc('K') else 0.0
    
    # H
    h1 = _pv('h1')
    h2_lbl = _pv('h2', COEFF_LABELS[0])
    h2 = COEFF_OPTIONS.get(h2_lbl, 1.0)
    h3 = _pv('h3', 100.0)
    res["H"] = h1 * h2 * (h3 / 100.0) if _pc('H') else 0.0
    
    # I
    i1 = _pv('i1')
    i2_lbl = _pv('i2', COEFF_LABELS[0])
    i2 = COEFF_OPTIONS.get(i2_lbl, 1.0)
    i3 = _pv('i3', 100.0)
    res["I"] = i1 * i2 * (i3 / 100.0) if _pc('I') else 0.0
    
    # J
    j1 = _pv('j1')
    j2 = _pv('j2', 100.0)
    j3_lbl = _pv('j3', COEFF_LABELS[0])
    j3 = COEFF_OPTIONS.get(j3_lbl, 1.0)
    j4 = _pv('j4', 100.0)
    res["J"] = j1 * (j2 / 100.0) * j3 * (j4 / 100.0) if _pc('J') else 0.0
    
    return res

# Render Header
st.markdown("""
<div class="section-header">
    <span class="section-header-title">🧮 เครื่องประเมินผลลัพธ์ (Pre-Impact / Pre-Investment)</span>
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

render_stepper(2)

# 4. Checklist verification check
if not st.session_state.checklist_passed:
    st.error("🚫 **การเข้าถึงถูกจำกัด (Access Restricted):** ท่านจำเป็นต้องประเมินความพร้อมแบบ **Checklist** ให้ผ่านเกณฑ์ก่อนเข้าใช้งานเครื่องประเมิน Pre-Impact")
    st.info("💡 **คำแนะนำ:** กรุณากรอก Checklist ในหมวดที่ 1 (หลักเกณฑ์เบื้องต้น) และหมวดที่ 2 (ลักษณะของผลงาน/บริการ) ให้ครบถ้วนเพื่อปลดล็อคเครื่องคำนวณ")
    
    if st.button("📋 ไปหน้า Checklist ความพร้อมเพื่อปลดล็อค", use_container_width=True, type="primary"):
        st.switch_page("pages/checklist.py")
    st.stop()

# 5. Form Fields & Interactive Logic Containers
# Synchronize state based on user interaction source (widget vs button)
if "segmented_calc_tab" in st.session_state and st.session_state.segmented_calc_tab != st.session_state.last_active_tab:
    # Widget was clicked
    st.session_state.active_calc_tab = st.session_state.segmented_calc_tab
    st.session_state.last_active_tab = st.session_state.segmented_calc_tab
elif st.session_state.active_calc_tab != st.session_state.last_active_tab:
    # Button was clicked
    st.session_state.segmented_calc_tab = st.session_state.active_calc_tab
    st.session_state.last_active_tab = st.session_state.active_calc_tab

active_tab = st.segmented_control(
    "ขั้นตอนการประเมิน:",
    options=TABS_LIST,
    key="segmented_calc_tab",
    label_visibility="collapsed"
)

results = compute_results()

# ==================== TAB 1: PROJECT DETAILS ====================
if st.session_state.active_calc_tab == TABS_LIST[0]:
    st.markdown("### 📋 กรอกข้อมูลรายละเอียดโครงการ")
    st.session_state.projectId = st.text_input(
        "รหัสโครงการ (Project ID) 👉 [กรอกข้อมูล]", 
        value=st.session_state.projectId, 
        placeholder="เช่น P-20-XXXXX",
        help="รหัสอ้างอิงโครงการที่จดทะเบียนของหน่วยงาน"
    )
    st.session_state.projectName = st.text_input(
        "ชื่อโครงการ (Project Name) 👉 [กรอกข้อมูล]", 
        value=st.session_state.projectName, 
        placeholder="ระบุชื่อโครงการวิจัย...",
        help="ชื่อหัวข้อโครงการวิจัยและพัฒนาฉบับเต็ม"
    )
    
    st.session_state.reportType = st.radio(
        "แนวทางการรายงานผล (Report Timeline Style) 👉 [กรอกข้อมูล]",
        ["รายปี", "5 ปี"],
        index=0 if st.session_state.reportType == "รายปี" else 1,
        horizontal=True,
        help="ระบุรูปแบบการวัดผลกระทบ: แบบรายปีปกติ หรือ ประเมินสะสมรวมระยะเวลา 5 ปี (60 เดือน)"
    )
    
    # KRRN/KRID/Patent Metadata Section (Google Form Q7-Q10)
    st.markdown("---")
    st.markdown("#### 🔗 ข้อมูลอ้างอิงผลงาน 3P (KRRN / KRID / สิทธิบัตร)")
    st.caption('ถ้าไม่มี ให้ระบุว่า "ไม่มี" หรือ ถ้ามีมากกว่า 1 ให้ใช้ "," คั่น')
    
    st.session_state.meta_krrn = st.text_input(
        "7. เลขที่ KRRN ผลงาน 3P 👉 [กรอกข้อมูล]",
        value=st.session_state.meta_krrn,
        placeholder="ตัวอย่าง: 65248, 70065",
        help='เลขที่ KRRN ผลงาน 3P (ถ้าไม่มี ให้ระบุว่า "ไม่มี" หรือ ถ้ามีมากกว่า 1 ให้ใช้ ",")'
    )
    st.session_state.meta_krid = st.text_input(
        "8. เลขที่ KRID ผลงาน 3P 👉 [กรอกข้อมูล]",
        value=st.session_state.meta_krid,
        placeholder="ตัวอย่าง: 45606029, 45809086",
        help='เลขที่ KRID ผลงาน 3P (ถ้าไม่มี ให้ระบุว่า "ไม่มี" หรือ ถ้ามีมากกว่า 1 ให้ใช้ ",")'
    )
    st.session_state.meta_krrn_related = st.text_input(
        "9. เลขที่ KRRN ผลงาน 3P ที่เกี่ยวข้อง 👉 [กรอกข้อมูล]",
        value=st.session_state.meta_krrn_related,
        placeholder="ตัวอย่าง: 45606029, 45809086",
        help='เลขที่ KRRN ผลงาน 3P ที่เกี่ยวข้อง (ถ้าไม่มี ให้ระบุว่า "ไม่มี" หรือ ถ้ามีมากกว่า 1 ให้ใช้ ",")'
    )
    st.session_state.meta_patent_id = st.text_input(
        "10. เลขที่คำขอยื่นสิทธิบัตร/อนุสิทธิบัตร 👉 [กรอกข้อมูล]",
        value=st.session_state.meta_patent_id,
        placeholder="ตัวอย่าง: BTT028/2560 (LCA-NT-2560-3304-TH)",
        help='เลขที่คำขอยื่นสิทธิบัตร/อนุสิทธิบัตร (ถ้าไม่มี ให้ระบุว่า "ไม่มี" หรือ ถ้ามีมากกว่า 1 ให้ใช้ ",")'
    )
    
    st.markdown("""
    <div style="background-color: rgba(59, 130, 246, 0.05); border: 1px solid #3b82f6; border-radius: 8px; padding: 1.2rem; margin-top: 1.5rem;">
        <h5 style="color: #3b82f6; margin-top: 0; margin-bottom: 0.5rem;">💡 คำแนะนำความเชื่อมโยง</h5>
        <p style="font-size: 0.9rem; color: #cbd5e1; margin: 0; line-height: 1.5;">
            หลังกรอกรหัสและชื่อโครงการเรียบร้อยแล้ว ให้เลือกมิติความสำเร็จใน <b>แท็บที่ 2 (Pre-Impact)</b> และ <b>แท็บที่ 3 (Pre-Investment)</b> เพื่อคำนวณมูลค่ารายหมวด และกดส่งสรุปที่ <b>แท็บที่ 4</b>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("ขั้นตอนถัดไป (Next) ➡️", key="btn_next_tab1", use_container_width=True, type="primary"):
        snapshot_state()
        st.session_state.active_calc_tab = TABS_LIST[1]
        st.rerun()

# ==================== TAB 2: PRE-IMPACT ====================
elif st.session_state.active_calc_tab == TABS_LIST[1]:
    st.markdown("### 📈 ประเมินมูลค่าผลกระทบทางเศรษฐกิจ/สังคม (Pre-Impact)")
    st.info("""
    💡 **กฎความซ้ำซ้อน (Exclusivity Rule):**
    หากเลือก **หมวด B (ลดการนำเข้า)** ระบบจะปิดการใช้งานหมวด C, D, E, F, G โดยอัตโนมัติ เพื่อป้องกันการประเมินมูลค่าทับซ้อนกันในโครงการเดียวกัน
    """)
    
    # Section B
    sec_B = st.checkbox("B. ผู้รับบริการลดการนำเข้าจากต่างประเทศ (Import Substitution)", value=_pc('B'), key="chk_B", on_change=sync_chk, args=('B',))
    if sec_B:
        with st.container(border=True):
            st.markdown("<h4 style='color: #3b82f6;'>หมวด B: ลดการนำเข้าจากต่างประเทศ</h4>", unsafe_allow_html=True)
            b1 = st.number_input(
                "มูลค่าสินค้าหรือบริการจากต่างประเทศ (b1) 👉 [กรอกข้อมูล]", 
                min_value=0.0, step=1000.0, value=_pv('b1'), key="val_b1", on_change=sync_val, args=('b1',),
                help="ราคาสินค้านำเข้าเดิมจากต่างประเทศที่ต้องการทดแทนต่อชิ้น/หน่วย"
            )
            b2 = st.number_input(
                "มูลค่าสินค้าหรือบริการทดแทนของเนคเทค (b2) 👉 [กรอกข้อมูล]", 
                min_value=0.0, step=1000.0, value=_pv('b2'), key="val_b2", on_change=sync_val, args=('b2',),
                help="ราคาสินค้าหรือบริการที่เนคเทคคิดค่าใช้จ่ายกับลูกค้าต่อชิ้น/หน่วย"
            )
            b3 = b1 - b2
            st.info(f"✨ [คำนวณอัตโนมัติ] ส่วนต่างที่ประหยัดได้ต่อหน่วย (b3) = b1 - b2: **{b3:,.2f} บาท**")
            
            b4 = st.number_input(
                "สัดส่วนเปรียบเทียบคุณสมบัติหรือสเปกสินค้า (%) (b4) 👉 [กรอกข้อมูล]", 
                min_value=0.0, max_value=100.0, value=_pv('b4', 100.0), key="val_b4", on_change=sync_val, args=('b4',),
                help="ประสิทธิภาพการทำงานเปรียบเทียบเมื่อเทียบกับของต่างประเทศ (คิดเป็น % คุณภาพ)"
            )
            b5 = st.number_input(
                "จำนวนสินค้า/บริการที่เกิดการทดแทน (b5) 👉 [กรอกข้อมูล]", 
                min_value=0.0, step=1.0, value=_pv('b5', 1.0), key="val_b5", on_change=sync_val, args=('b5',),
                help="ปริมาณชิ้นงานที่ลูกค้านำไปใช้งานจริงทดแทนนำเข้า"
            )
            b6_label = st.selectbox(
                "กิจกรรมส่งมอบหลักของผลงาน (b6) 👉 [กรอกข้อมูล]", 
                options=COEFF_LABELS, index=COEFF_LABELS.index(_pv('b6', COEFF_LABELS[0])), key="val_b6", on_change=sync_val, args=('b6',),
                help="สัมประสิทธิ์น้ำหนักประเภทกิจกรรมส่งมอบของ สวทช."
            )
            b6 = COEFF_OPTIONS[b6_label]
            b7 = st.number_input(
                "สัดส่วนน้ำหนักการมีส่วนร่วมของ สวทช. (%) (b7) 👉 [กรอกข้อมูล]", 
                min_value=0.0, max_value=100.0, value=_pv('b7', 100.0), key="val_b7", on_change=sync_val, args=('b7',),
                help="น้ำหนักสัดส่วนบทบาทความสำเร็จของ สวทช. ในการส่งมอบผลงานนี้ (Contribution)"
            )
            
            # Calculate
            b8 = b3 * (b4 / 100.0) * b5 * b6 * (b7 / 100.0)
            results["B"] = b8
            st.success(f"🏆 [คำนวณอัตโนมัติ] มูลค่า Pre-Impact หมวด B: **{b8:,.2f} บาท**")

    # Section C
    sec_C = st.checkbox("C. ผู้รับบริการมีกำไร/รายได้เพิ่มขึ้น (Revenue/Profit Increase)", value=_pc('C'), key="chk_C", on_change=sync_chk, args=('C',), disabled=st.session_state.chk_B)
    if sec_C:
        with st.container(border=True):
            st.markdown("<h4 style='color: #3b82f6;'>หมวด C: ผู้รับบริการมีกำไร/รายได้เพิ่มขึ้น</h4>", unsafe_allow_html=True)
            c1 = st.number_input("รายได้ก่อนใช้ผลงานวิจัย (c1) 👉 [กรอกข้อมูล]", min_value=0.0, step=1000.0, value=_pv('c1'), key="val_c1", on_change=sync_val, args=('c1',), help="รายได้เดิมต่อปีของผู้รับบริการ")
            c2 = st.number_input("ต้นทุนดำเนินงานก่อนใช้ผลงานวิจัย (c2) 👉 [กรอกข้อมูล]", min_value=0.0, step=1000.0, value=_pv('c2'), key="val_c2", on_change=sync_val, args=('c2',), help="ต้นทุนดำเนินงานเดิมต่อปี")
            c3 = st.number_input("รายได้หลังใช้ผลงานวิจัย (c3) 👉 [กรอกข้อมูล]", min_value=0.0, step=1000.0, value=_pv('c3'), key="val_c3", on_change=sync_val, args=('c3',), help="รายได้ใหม่ต่อปีหลังประยุกต์ใช้ระบบ")
            c4 = st.number_input("ต้นทุนดำเนินงานหลังใช้ผลงานวิจัย (c4) 👉 [กรอกข้อมูล]", min_value=0.0, step=1000.0, value=_pv('c4'), key="val_c4", on_change=sync_val, args=('c4',), help="ต้นทุนดำเนินงานใหม่ต่อปีหลังประยุกต์ใช้ระบบ")
            c5 = (c3 - c4) - (c1 - c2)
            st.info(f"✨ [คำนวณอัตโนมัติ] กำไรสุทธิส่วนเพิ่มที่เกิดขึ้น (c5) = (c3 - c4) - (c1 - c2): **{c5:,.2f} บาท**")
            
            c6_label = st.selectbox("กิจกรรมส่งมอบหลักของผลงาน (c6) 👉 [กรอกข้อมูล]", options=COEFF_LABELS, index=COEFF_LABELS.index(_pv('c6', COEFF_LABELS[0])), key="val_c6", on_change=sync_val, args=('c6',), help="สัมประสิทธิ์กิจกรรมส่งมอบ สวทช.")
            c6 = COEFF_OPTIONS[c6_label]
            c7 = st.number_input("สัดส่วนน้ำหนักการมีส่วนร่วมของ สวทช. (%) (c7) 👉 [กรอกข้อมูล]", min_value=0.0, max_value=100.0, value=_pv('c7', 100.0), key="val_c7", on_change=sync_val, args=('c7',), help="เปอร์เซ็นต์ส่วนร่วมของ สวทช. (Contribution)")
            
            # Calculate
            c8 = c5 * c6 * (c7 / 100.0)
            results["C"] = c8
            st.success(f"🏆 [คำนวณอัตโนมัติ] มูลค่า Pre-Impact หมวด C: **{c8:,.2f} บาท**")

    # Section D
    sec_D = st.checkbox("D. ผู้รับบริการประหยัดค่าใช้จ่าย/ลดต้นทุนดำเนินงาน (Cost/Expense Reduction)", value=_pc('D'), key="chk_D", on_change=sync_chk, args=('D',), disabled=st.session_state.chk_B)
    if sec_D:
        with st.container(border=True):
            st.markdown("<h4 style='color: #3b82f6;'>หมวด D: ผู้รับบริการประหยัดค่าใช้จ่าย/ลดต้นทุน</h4>", unsafe_allow_html=True)
            d1 = st.number_input("ค่าใช้จ่ายหรือต้นทุนก่อนใช้ผลงานวิจัย (d1) 👉 [กรอกข้อมูล]", min_value=0.0, step=1000.0, value=_pv('d1'), key="val_d1", on_change=sync_val, args=('d1',), help="ค่าใช้จ่ายรายปีของส่วนงานผู้ใช้บริการก่อนเริ่มโครงการ")
            d2 = st.number_input("ค่าใช้จ่ายหรือต้นทุนหลังใช้ผลงานวิจัย (d2) 👉 [กรอกข้อมูล]", min_value=0.0, step=1000.0, value=_pv('d2'), key="val_d2", on_change=sync_val, args=('d2',), help="ค่าใช้จ่ายรายปีหลังเอาเทคโนโลยีมาช่วย")
            d3 = d1 - d2
            st.info(f"✨ [คำนวณอัตโนมัติ] รายจ่ายที่ลดลงได้ (d3) = d1 - d2: **{d3:,.2f} บาท**")
            
            d4_label = st.selectbox("กิจกรรมส่งมอบหลักของผลงาน (d4) 👉 [กรอกข้อมูล]", options=COEFF_LABELS, index=COEFF_LABELS.index(_pv('d4', COEFF_LABELS[0])), key="val_d4", on_change=sync_val, args=('d4',))
            d4 = COEFF_OPTIONS[d4_label]
            d5 = st.number_input("สัดส่วนน้ำหนักการมีส่วนร่วมของ สวทช. (%) (d5) 👉 [กรอกข้อมูล]", min_value=0.0, max_value=100.0, value=_pv('d5', 100.0), key="val_d5", on_change=sync_val, args=('d5',))
            
            # Calculate
            d6 = d3 * d4 * (d5 / 100.0)
            results["D"] = d6
            st.success(f"🏆 [คำนวณอัตโนมัติ] มูลค่า Pre-Impact หมวด D: **{d6:,.2f} บาท**")

    # Section E
    sec_E = st.checkbox("E. ผู้รับบริการมีประสิทธิภาพการปฏิบัติงานเพิ่มขึ้น (Efficiency Increase)", value=_pc('E'), key="chk_E", on_change=sync_chk, args=('E',), disabled=st.session_state.chk_B)
    if sec_E:
        with st.container(border=True):
            st.markdown("<h4 style='color: #3b82f6;'>หมวด E: เพิ่มประสิทธิภาพในการทำงาน</h4>", unsafe_allow_html=True)
            e1 = st.number_input("ฐานอัตราเงินเดือนเฉลี่ยของบุคลากรที่เกี่ยวข้อง (e1) 👉 [กรอกข้อมูล]", min_value=0.0, step=1000.0, value=_pv('e1'), key="val_e1", on_change=sync_val, args=('e1',), help="ฐานเงินเดือนเฉลี่ยของพนักงานที่รับผิดชอบภารกิจนั้น")
            e2 = st.number_input("จำนวนชั่วโมงการทำงานปกติในหนึ่งวัน (e2) 👉 [กรอกข้อมูล]", min_value=0.0, max_value=24.0, value=_pv('e2', 8.0), key="val_e2", on_change=sync_val, args=('e2',), help="ปกติจะเฉลี่ยเป็น 8 ชั่วโมงต่อวัน")
            e3 = e2 * 60.0
            e4 = e3 * 20.0
            e5 = e1 / e4 if e4 > 0 else 0.0
            st.info(f"✨ [คำนวณอัตโนมัติ] คิดเป็นนาทีละ (e5) = e1 / (e2 * 60 * 20): **{e5:,.2f} บาท/นาที**")
            
            e6 = st.number_input("ระยะเวลาดำเนินงานเดิมก่อนใช้ผลงานวิจัย (นาที) (e6) 👉 [กรอกข้อมูล]", min_value=0.0, step=10.0, value=_pv('e6'), key="val_e6", on_change=sync_val, args=('e6',), help="เวลาดำเนินงานต่อ 1 ครั้งก่อนใช้ผลงาน")
            e7 = st.number_input("ระยะเวลาดำเนินงานใหม่หลังใช้ผลงานวิจัย (นาที) (e7) 👉 [กรอกข้อมูล]", min_value=0.0, step=10.0, value=_pv('e7'), key="val_e7", on_change=sync_val, args=('e7',), help="เวลาดำเนินงานต่อ 1 ครั้งหลังระบบช่วยลดระยะเวลา")
            e8 = e6 - e7
            st.info(f"✨ [คำนวณอัตโนมัติ] เวลาที่ประหยัดได้ต่อครั้ง (e8) = e6 - e7: **{e8:,.2f} นาที**")
            
            e9 = st.number_input("ความถี่ในการปฏิบัติภารกิจต่อปี (e9) 👉 [กรอกข้อมูล]", min_value=0.0, step=1.0, value=_pv('e9', 1.0), key="val_e9", on_change=sync_val, args=('e9',), help="จำนวนครั้งในการดำเนินภารกิจนี้ทั้งหมดรวมตลอดปี")
            e10_label = st.selectbox("กิจกรรมส่งมอบหลักของผลงาน (e10) 👉 [กรอกข้อมูล]", options=COEFF_LABELS, index=COEFF_LABELS.index(_pv('e10', COEFF_LABELS[0])), key="val_e10", on_change=sync_val, args=('e10',))
            e10 = COEFF_OPTIONS[e10_label]
            e11 = st.number_input("สัดส่วนน้ำหนักการมีส่วนร่วมของ สวทช. (%) (e11) 👉 [กรอกข้อมูล]", min_value=0.0, max_value=100.0, value=_pv('e11', 100.0), key="val_e11", on_change=sync_val, args=('e11',))
            
            # Calculate
            e12 = e5 * e8 * e9 * e10 * (e11 / 100.0)
            results["E"] = e12
            st.success(f"🏆 [คำนวณอัตโนมัติ] มูลค่า Pre-Impact หมวด E: **{e12:,.2f} บาท**")

    # Section F
    sec_F = st.checkbox("F. การลดระดับความเสี่ยงหรือป้องกันความเสียหาย (Risk Mitigation / Damage Prevention)", value=_pc('F'), key="chk_F", on_change=sync_chk, args=('F',), disabled=st.session_state.chk_B)
    if sec_F:
        with st.container(border=True):
            st.markdown("<h4 style='color: #3b82f6;'>หมวด F: ลดระดับความเสี่ยงหรือความเสียหาย</h4>", unsafe_allow_html=True)
            f1 = st.number_input("มูลค่าของความเสียหายทางตรงเฉลี่ยต่อปี (f1) 👉 [กรอกข้อมูล]", min_value=0.0, step=1000.0, value=_pv('f1'), key="val_f1", on_change=sync_val, args=('f1',), help="มูลค่าค่าปรับ/ความเสียหายของอุปกรณ์/ผลผลิตในกรณีเกิดเหตุการณ์ล้มเหลว")
            f2 = st.number_input("ระดับโอกาสความน่าจะเป็นที่จะเกิดการสูญเสีย (%) (f2) 👉 [กรอกข้อมูล]", min_value=0.0, max_value=100.0, value=_pv('f2', 100.0), key="val_f2", on_change=sync_val, args=('f2',), help="ความน่าจะเป็นในการเกิดภัยพิบัติหรือความล้มเหลวเดิม")
            f3 = st.number_input("สัดส่วนความเสียหายที่สามารถป้องกันได้ (%) (f3) 👉 [กรอกข้อมูล]", min_value=0.0, max_value=100.0, value=_pv('f3', 100.0), key="val_f3", on_change=sync_val, args=('f3',), help="สัญญานเตือนภัย/ระบบตรวจจับช่วยลดโอกาสความรุนแรงลงไปกี่ %")
            f4_label = st.selectbox("กิจกรรมส่งมอบหลักของผลงาน (f4) 👉 [กรอกข้อมูล]", options=COEFF_LABELS, index=COEFF_LABELS.index(_pv('f4', COEFF_LABELS[0])), key="val_f4", on_change=sync_val, args=('f4',))
            f4 = COEFF_OPTIONS[f4_label]
            f5 = st.number_input("สัดส่วนน้ำหนักการมีส่วนร่วมของ สวทช. (%) (f5) 👉 [กรอกข้อมูล]", min_value=0.0, max_value=100.0, value=_pv('f5', 100.0), key="val_f5", on_change=sync_val, args=('f5',))
            
            # Calculate
            f6 = f1 * (f2 / 100.0) * (f3 / 100.0) * f4 * (f5 / 100.0)
            results["F"] = f6
            st.success(f"🏆 [คำนวณอัตโนมัติ] มูลค่า Pre-Impact หมวด F: **{f6:,.2f} บาท**")

    # Section G
    sec_G = st.checkbox("G. การพัฒนาสมรรถนะบุคลากรผ่านการฝึกอบรม (Technical Skill Upgrade)", value=_pc('G'), key="chk_G", on_change=sync_chk, args=('G',), disabled=st.session_state.chk_B)
    if sec_G:
        with st.container(border=True):
            st.markdown("<h4 style='color: #3b82f6;'>หมวด G: พัฒนาสมรรถนะทักษะบุคลากร</h4>", unsafe_allow_html=True)
            g1 = st.number_input("จำนวนบุคลากรภายนอกที่ผ่านหลักสูตรการฝึกอบรม (g1) 👉 [กรอกข้อมูล]", min_value=0.0, step=1.0, value=_pv('g1', 1.0), key="val_g1", on_change=sync_val, args=('g1',), help="จำนวนผู้เข้าร่วมอบรมทั้งหมด")
            g2 = st.number_input("มูลค่าคอร์สอบรมหลักสูตรใกล้เคียงในตลาด (g2) 👉 [กรอกข้อมูล]", min_value=0.0, step=100.0, value=_pv('g2'), key="val_g2", on_change=sync_val, args=('g2',), help="เทียบเคียงจากราคาคอร์สเอกชนหรือผู้เชี่ยวชาญอื่นต่อหัว")
            g3_label = st.selectbox("กิจกรรมส่งมอบหลักของผลงาน (g3) 👉 [กรอกข้อมูล]", options=COEFF_LABELS, index=COEFF_LABELS.index(_pv('g3', COEFF_LABELS[0])), key="val_g3", on_change=sync_val, args=('g3',))
            g3 = COEFF_OPTIONS[g3_label]
            g4 = st.number_input("สัดส่วนน้ำหนักการมีส่วนร่วมของ สวทช. (%) (g4) 👉 [กรอกข้อมูล]", min_value=0.0, max_value=100.0, value=_pv('g4', 100.0), key="val_g4", on_change=sync_val, args=('g4',))
            
            # Calculate
            g5 = g1 * g2 * g3 * (g4 / 100.0)
            results["G"] = g5
            st.success(f"🏆 [คำนวณอัตโนมัติ] มูลค่า Pre-Impact หมวด G: **{g5:,.2f} บาท**")

    # Section K
    sec_K = st.checkbox("K. [Impact] อื่น ๆ เปรียบเทียบสิ่งที่เกิดขึ้นก่อน-หลังใช้ผลงานวิจัย (Other Comparative Impact)", value=_pc('K'), key="chk_K", on_change=sync_chk, args=('K',))
    if sec_K:
        with st.container(border=True):
            st.markdown("<h4 style='color: #3b82f6;'>หมวด K: [Impact] อื่น ๆ เปรียบเทียบสิ่งที่เกิดขึ้นก่อน-หลังใช้ผลงานวิจัย</h4>", unsafe_allow_html=True)
            k1 = st.number_input("มูลค่า...(ระบุ)... (k1) 👉 [กรอกข้อมูล]", min_value=0.0, step=1000.0, value=_pv('k1'), key="val_k1", on_change=sync_val, args=('k1',), help="ระบุมูลค่าส่วนต่างที่ได้ทำการประเมินเพิ่มเติม เช่น มูลค่าเปรียบเทียบก่อน-หลังใช้ผลงานวิจัย")
            k2_label = st.selectbox("กิจกรรมส่งมอบหลักของผลงาน (k2) 👉 [กรอกข้อมูล]", options=COEFF_LABELS, index=COEFF_LABELS.index(_pv('k2', COEFF_LABELS[0])), key="val_k2", on_change=sync_val, args=('k2',))
            k2 = COEFF_OPTIONS[k2_label]
            k3 = st.number_input("Contribution (จากผู้รับบริการ) (%) (k3) 👉 [กรอกข้อมูล]", min_value=0.0, max_value=100.0, value=_pv('k3', 100.0), key="val_k3", on_change=sync_val, args=('k3',))
            
            # Calculate
            k4 = k1 * k2 * (k3 / 100.0)
            results["K"] = k4
            st.success(f"🏆 [คำนวณอัตโนมัติ] มูลค่า Pre-Impact หมวด K: **{k4:,.2f} บาท**")

    st.markdown("---")
    col_nav1, col_nav2 = st.columns(2)
    if col_nav1.button("⬅️ ย้อนกลับ (Back)", key="btn_back_tab2", use_container_width=True):
        st.session_state.active_calc_tab = TABS_LIST[0]
        st.rerun()
    if col_nav2.button("ขั้นตอนถัดไป (Next) ➡️", key="btn_next_tab2", use_container_width=True, type="primary"):
        st.session_state.active_calc_tab = TABS_LIST[2]
        st.rerun()

# ==================== TAB 3: PRE-INVESTMENT ====================
elif st.session_state.active_calc_tab == TABS_LIST[2]:
    st.markdown("### 💰 ประเมินการร่วมลงทุนเพิ่มของกลุ่มลูกค้า/ผู้รับประโยชน์ (Pre-Investment)")
    
    # Section H
    sec_H = st.checkbox("H. [Investment] ผู้รับบริการมีการลงทุนวิจัยต่อยอด (Client R&D Investment)", value=_pc('H'), key="chk_H", on_change=sync_chk, args=('H',))
    if sec_H:
        with st.container(border=True):
            st.markdown("<h4 style='color: #f59e0b;'>หมวด H: การลงทุนเพื่อวิจัยและพัฒนาต่อยอด</h4>", unsafe_allow_html=True)
            h1 = st.number_input("มูลค่าการลงทุนวิจัยต่อยอดโดยตรง (h1) 👉 [กรอกข้อมูล]", min_value=0.0, step=1000.0, value=_pv('h1'), key="val_h1", on_change=sync_val, args=('h1',), help="เงินร่วมทุนวิจัยเพิ่มของลูกค้าเพื่อต่อยอดผลิตภัณฑ์")
            h2_label = st.selectbox("กิจกรรมส่งมอบหลักของผลงาน (h2) 👉 [กรอกข้อมูล]", options=COEFF_LABELS, index=COEFF_LABELS.index(_pv('h2', COEFF_LABELS[0])), key="val_h2", on_change=sync_val, args=('h2',))
            h2 = COEFF_OPTIONS[h2_label]
            h3 = st.number_input("สัดส่วนน้ำหนักการมีส่วนร่วมของ สวทช. (%) (h3) 👉 [กรอกข้อมูล]", min_value=0.0, max_value=100.0, value=_pv('h3', 100.0), key="val_h3", on_change=sync_val, args=('h3',))
            
            # Calculate
            h4 = h1 * h2 * (h3 / 100.0)
            results["H"] = h4
            st.success(f"🏆 [คำนวณอัตโนมัติ] มูลค่า Pre-Investment หมวด H: **{h4:,.2f} บาท**")

    # Section I
    sec_I = st.checkbox("I. [Investment] ผู้รับบริการมีการลงทุนในกระบวนการผลิตและบริการ (Client Process Investment)", value=_pc('I'), key="chk_I", on_change=sync_chk, args=('I',))
    if sec_I:
        with st.container(border=True):
            st.markdown("<h4 style='color: #f59e0b;'>หมวด I: ลงทุนเพิ่มเติมในระบบการผลิต</h4>", unsafe_allow_html=True)
            i1 = st.number_input("มูลค่าจัดซื้อเครื่องจักร/ปรับสายการผลิต (i1) 👉 [กรอกข้อมูล]", min_value=0.0, step=1000.0, value=_pv('i1'), key="val_i1", on_change=sync_val, args=('i1',), help="มูลค่าเครื่องจักรหรือการปรับแต่งโรงงานเพื่อรองรับการใช้งานผลงานวิจัย")
            i2_label = st.selectbox("กิจกรรมส่งมอบหลักของผลงาน (i2) 👉 [กรอกข้อมูล]", options=COEFF_LABELS, index=COEFF_LABELS.index(_pv('i2', COEFF_LABELS[0])), key="val_i2", on_change=sync_val, args=('i2',))
            i2 = COEFF_OPTIONS[i2_label]
            i3 = st.number_input("สัดส่วนน้ำหนักการมีส่วนร่วมของ สวทช. (%) (i3) 👉 [กรอกข้อมูล]", min_value=0.0, max_value=100.0, value=_pv('i3', 100.0), key="val_i3", on_change=sync_val, args=('i3',))
            
            # Calculate
            i4 = i1 * i2 * (i3 / 100.0)
            results["I"] = i4
            st.success(f"🏆 [คำนวณอัตโนมัติ] มูลค่า Pre-Investment หมวด I: **{i4:,.2f} บาท**")

    # Section J
    sec_J = st.checkbox("J. [Investment] ผู้รับบริการมีการจ้างงานเพิ่ม (Additional Staff Hiring)", value=_pc('J'), key="chk_J", on_change=sync_chk, args=('J',))
    if sec_J:
        with st.container(border=True):
            st.markdown("<h4 style='color: #f59e0b;'>หมวด J: ร่วมลงทุนจ้างงานบุคลากรใหม่</h4>", unsafe_allow_html=True)
            j1 = st.number_input("อัตราเงินเดือนค่าจ้างบุคลากรเพิ่มรวมต่อปี (j1) 👉 [กรอกข้อมูล]", min_value=0.0, step=1000.0, value=_pv('j1'), key="val_j1", on_change=sync_val, args=('j1',), help="ยอดรวมเงินเดือนที่ลูกค้าจ่ายเพิ่มขึ้นให้กับพนักงานใหม่ที่เข้ามาคุมงานระบบวิจัย")
            j2 = st.number_input("สัดส่วนเวลาการปฏิบัติภารกิจเกี่ยวข้องตรง (%) (j2) 👉 [กรอกข้อมูล]", min_value=0.0, max_value=100.0, value=_pv('j2', 100.0), key="val_j2", on_change=sync_val, args=('j2',), help="สัดส่วนเวลา (FTE) ของผู้ว่าจ้างที่เกี่ยวข้องกับการคุมระบบวิจัย")
            j3_label = st.selectbox("กิจกรรมส่งมอบหลักของผลงาน (j3) 👉 [กรอกข้อมูล]", options=COEFF_LABELS, index=COEFF_LABELS.index(_pv('j3', COEFF_LABELS[0])), key="val_j3", on_change=sync_val, args=('j3',))
            j3 = COEFF_OPTIONS[j3_label]
            j4 = st.number_input("สัดส่วนน้ำหนักการมีส่วนร่วมของ สวทช. (%) (j4) 👉 [กรอกข้อมูล]", min_value=0.0, max_value=100.0, value=_pv('j4', 100.0), key="val_j4", on_change=sync_val, args=('j4',))
            
            # Calculate
            j5 = j1 * (j2 / 100.0) * j3 * (j4 / 100.0)
            results["J"] = j5
            st.success(f"🏆 [คำนวณอัตโนมัติ] มูลค่า Pre-Investment หมวด J: **{j5:,.2f} บาท**")

    st.markdown("---")
    col_nav1, col_nav2 = st.columns(2)
    if col_nav1.button("⬅️ ย้อนกลับ (Back)", key="btn_back_tab3", use_container_width=True):
        st.session_state.active_calc_tab = TABS_LIST[1]
        st.rerun()
    if col_nav2.button("ขั้นตอนถัดไป (Next) ➡️", key="btn_next_tab3", use_container_width=True, type="primary"):
        st.session_state.active_calc_tab = TABS_LIST[3]
        st.rerun()

# ==================== TAB 4: SUBMIT & DRAFTS ====================
elif st.session_state.active_calc_tab == TABS_LIST[3]:
    st.markdown("### 💾 แผงควบคุมและจัดส่งรายงานการประเมิน")
    
    # Refresh results for Tab 4 to ensure they match current state
    current_results = compute_results()
    
    # Calculate Sums
    total_impact = sum([current_results.get(s, 0.0) for s in ['B', 'C', 'D', 'E', 'F', 'G', 'K']])
    total_investment = sum([current_results.get(s, 0.0) for s in ['H', 'I', 'J']])

    # Debug logging for results
    try:
        with open("calculator_debug.log", "a", encoding="utf-8") as f:
            f.write(f"Tab 4 computed current_results: {current_results}\n")
            f.write(f"total_impact: {total_impact}, total_investment: {total_investment}\n")
    except:
        pass
    
    st.markdown("#### 📊 ผลรวมการประมาณมูลค่า")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown(f"""
        <div style="background-color: rgba(16, 185, 129, 0.1); padding: 1.2rem; border-radius: 8px; border: 1px solid #10b981; text-align: center;">
            <span style="font-size: 0.9rem; color: #10b981; font-weight: bold;">มูลค่า Pre-Impact รวมทั้งหมด</span>
            <h2 style="color: #10b981; margin: 0.5rem 0 0 0; font-size: 2rem;">{total_impact:,.2f} บาท</h2>
            <span style="font-size: 0.8rem; color: #94a3b8;">({st.session_state.reportType})</span>
        </div>
        """, unsafe_allow_html=True)
        
    with col_t2:
        st.markdown(f"""
        <div style="background-color: rgba(245, 158, 11, 0.1); padding: 1.2rem; border-radius: 8px; border: 1px solid #f59e0b; text-align: center;">
            <span style="font-size: 0.9rem; color: #f59e0b; font-weight: bold;">มูลค่า Pre-Investment รวมทั้งหมด</span>
            <h2 style="color: #f59e0b; margin: 0.5rem 0 0 0; font-size: 2rem;">{total_investment:,.2f} บาท</h2>
            <span style="font-size: 0.8rem; color: #94a3b8;">({st.session_state.reportType})</span>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 1. Draft Controls inside the Tab
    st.markdown("---")
    st.markdown("#### 📂 จัดการแบบร่างแบบคลาวด์ (Cloud Drafts)")
    
    if firebase_config.is_db_connected():
        drafts = firebase_config.load_drafts(st.session_state.employee_id)
        if drafts:
            draft_options = {f"{d['project_id']} - {d['project_name']} (เซฟเมื่อ {d['saved_at']})": d for d in drafts}
            selected_draft_name = st.selectbox("เลือกเปิดแบบร่างโครงการเดิมที่เคยเซฟไว้:", ["-- เลือกแบบร่าง --"] + list(draft_options.keys()))
            
            if selected_draft_name != "-- เลือกแบบร่าง --":
                draft_data = draft_options[selected_draft_name]
                col_ld, col_del = st.columns(2)
                
                if col_ld.button("🔄 โหลดข้อมูลแบบร่างทับค่าปัจจุบัน", use_container_width=True, type="primary"):
                    st.session_state.projectId = draft_data.get("project_id", "")
                    st.session_state.projectName = draft_data.get("project_name", "")
                    st.session_state.reportType = draft_data.get("report_type", "รายปี")
                    
                    # Restoring checkbox toggles
                    sections = draft_data.get("sections", {})
                    for s in ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']:
                        st.session_state[f"chk_{s}"] = sections.get(s, False)
                        
                    # Restoring fields
                    fields = draft_data.get("fields", {})
                    for k, v in fields.items():
                        st.session_state[f"val_{k}"] = v
                    snapshot_state()  # Persist restored values to shadow keys
                    st.success("⚡ โหลดข้อมูลแบบร่างเรียบร้อยแล้ว!")
                    st.rerun()
                    
                if col_del.button("🗑️ ลบแบบร่างนี้ออกระบบ", use_container_width=True):
                    if firebase_config.delete_draft(draft_data["id"]):
                        st.success("🗑️ ลบแบบร่างเรียบร้อย!")
                        st.rerun()
        else:
            st.info("💡 สังกัดของท่านยังไม่มีแบบร่างใดบันทึกไว้ในระบบ Cloud")
            
        # Draft Save button
        if st.button("💾 เซฟแบบร่างปัจจุบัน (Save to Cloud)", use_container_width=True):
            proj_id = st.session_state.projectId.strip()
            if not proj_id:
                st.error("❌ กรุณาระบุรหัสโครงการ (Project ID) ที่แท็บ 1 ก่อนกดบันทึกแบบร่าง")
            else:
                # Collect states
                sections = {s: _pc(s) for s in ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']}
                fields = {}
                for s in ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']:
                    if s == 'B': f_ids = ['b1', 'b2', 'b4', 'b5', 'b6', 'b7']
                    elif s == 'C': f_ids = ['c1', 'c2', 'c3', 'c4', 'c6', 'c7']
                    elif s == 'D': f_ids = ['d1', 'd2', 'd4', 'd5']
                    elif s == 'E': f_ids = ['e1', 'e2', 'e6', 'e7', 'e9', 'e10', 'e11']
                    elif s == 'F': f_ids = ['f1', 'f2', 'f3', 'f4', 'f5']
                    elif s == 'G': f_ids = ['g1', 'g2', 'g3', 'g4']
                    elif s == 'H': f_ids = ['h1', 'h2', 'h3']
                    elif s == 'I': f_ids = ['i1', 'i2', 'i3']
                    elif s == 'J': f_ids = ['j1', 'j2', 'j3', 'j4']
                    elif s == 'K': f_ids = ['k1', 'k2', 'k3']
                    for fid in f_ids:
                        fields[fid] = _pv(fid, FIELD_DEFAULTS.get(fid, 0.0))
                
                draft_payload = {
                    "project_name": st.session_state.projectName,
                    "organization": st.session_state.organization,
                    "report_type": st.session_state.reportType,
                    "sections": sections,
                    "fields": fields
                }
                if firebase_config.save_draft(st.session_state.employee_id, proj_id, draft_payload):
                    st.toast("💾 บันทึกแบบร่างขึ้นระบบคลาวด์เรียบร้อยแล้ว!")
                    st.rerun()
    else:
        st.info("❌ ฟังก์ชัน Cloud Drafts ทำงานได้ในโหมดออนไลน์เท่านั้น (ปัจจุบันไม่สามารถเชื่อมต่อ Firebase ได้)")

    # 2. Main Submit controls
    st.markdown("---")
    st.markdown("#### 📤 ยื่นส่งรายงานประเมินผลโครงการ")
    
    submit_clicked = st.button("📤 ส่งและพิมพ์รายงานการประเมิน (Submit & Print)", type="primary", use_container_width=True)
    
    if submit_clicked:
        proj_id = st.session_state.projectId.strip()
        proj_name = st.session_state.projectName.strip()
        
        if not proj_id or not proj_name:
            st.error("❌ กรุณาระบุ 'รหัสโครงการ' และ 'ชื่อโครงการ' ให้สมบูรณ์ในแท็บ 1 ก่อนจัดทำรายงาน")
        elif total_impact == 0 and total_investment == 0:
            st.error("❌ มูลค่าผลลัพธ์การประเมินเป็น 0 บาท กรุณากรอกข้อมูลในมิติต่าง ๆ ในแท็บ 2 หรือ 3 อย่างน้อยหนึ่งหมวด")
        else:
            # Payload formulation
            eval_payload = {
                "employee_id": st.session_state.employee_id,
                "organization": st.session_state.organization,
                "project_id": proj_id,
                "project_name": proj_name,
                "report_type": st.session_state.reportType,
                "meta_krrn": st.session_state.meta_krrn,
                "meta_krid": st.session_state.meta_krid,
                "meta_krrn_related": st.session_state.meta_krrn_related,
                "meta_patent_id": st.session_state.meta_patent_id,
                "total_impact": total_impact,
                "total_investment": total_investment,
                "sections_checked": [s for s in ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K'] if _pc(s)],
                "b8_impact": results.get("B", 0.0),
                "c8_impact": results.get("C", 0.0),
                "d6_impact": results.get("D", 0.0),
                "e12_impact": results.get("E", 0.0),
                "f6_impact": results.get("F", 0.0),
                "g5_impact": results.get("G", 0.0),
                "h4_investment": results.get("H", 0.0),
                "i4_investment": results.get("I", 0.0),
                "j5_investment": results.get("J", 0.0),
                "k4_impact": results.get("K", 0.0),
            }
            
            # Fire database write
            save_success = False
            if firebase_config.is_db_connected():
                if firebase_config.submit_evaluation(eval_payload):
                    st.success("✅ บันทึกข้อมูลไปยังคลาวด์ Firebase สำเร็จ!")
                    save_success = True
                else:
                    st.error("❌ ไม่สามารถบันทึกข้อมูลไปยัง Firebase ได้ โปรดตรวจสอบการเชื่อมต่อ")
            else:
                st.warning("⚠️ ทำงานในโหมด Offline: ข้อมูลถูกส่งไปยัง Google Sheets เท่านั้น (ไม่บันทึกลงฐานข้อมูลหลัก)")
                
            # Log to Sheets
            sheets_payload = {
                "type": "preimpact",
                "organization": st.session_state.organization,
                "employeeId": st.session_state.employee_id,
                "projectId": proj_id,
                "projectName": proj_name,
                "reportType": st.session_state.reportType,
                "metaKRRN": st.session_state.meta_krrn,
                "metaKRID": st.session_state.meta_krid,
                "metaKRRNRelated": st.session_state.meta_krrn_related,
                "metaPatentId": st.session_state.meta_patent_id,
                "sectionB": str(results.get("B", "")) if st.session_state.chk_B else "",
                "sectionC": str(results.get("C", "")) if st.session_state.chk_C else "",
                "sectionD": str(results.get("D", "")) if st.session_state.chk_D else "",
                "sectionE": str(results.get("E", "")) if st.session_state.chk_E else "",
                "sectionF": str(results.get("F", "")) if st.session_state.chk_F else "",
                "sectionG": str(results.get("G", "")) if st.session_state.chk_G else "",
                "sectionH": str(results.get("H", "")) if st.session_state.chk_H else "",
                "sectionI": str(results.get("I", "")) if st.session_state.chk_I else "",
                "sectionJ": str(results.get("J", "")) if st.session_state.chk_J else "",
                "sectionK": str(results.get("K", "")) if st.session_state.chk_K else "",
                "totalImpact": str(total_impact),
                "totalInvestment": str(total_investment)
            }
            try:
                requests.post(GOOGLE_SHEET_URL, json=sheets_payload, timeout=8)
            except Exception as e:
                print(f"Sheets integration logging skipped or failed: {e}")
                
            st.toast("ส่งรายงานประเมินและสำรองข้อมูลไปยังคลาวด์เรียบร้อยแล้ว!")
            
            # Print output template
            st.markdown(f"""
            <div class="report-container">
                <div class="report-header">
                    <div class="report-title">รายงานการประมาณการผลลัพธ์และผลกระทบโครงการวิจัย (Pre-Impact)</div>
                    <div class="report-meta">วันที่รายงาน: {datetime.now().strftime('%Y-%m-%d')}</div>
                    <div class="report-meta">ผู้ประเมิน: {st.session_state.employee_id} ({st.session_state.organization})</div>
                </div>
                
                <div class="report-section">
                    <h4>ข้อมูลโครงการ</h4>
                    <div class="report-row"><span class="label">รหัสโครงการ (Project ID):</span><span class="value">{proj_id}</span></div>
                    <div class="report-row"><span class="label">ชื่อโครงการ (Project Name):</span><span class="value">{proj_name}</span></div>
                    <div class="report-row"><span class="label">รูปแบบช่วงเวลาที่บันทึก:</span><span class="value">{st.session_state.reportType}</span></div>
                    <div class="report-row"><span class="label">เลขที่ KRRN ผลงาน 3P:</span><span class="value">{st.session_state.meta_krrn or 'ไม่มี'}</span></div>
                    <div class="report-row"><span class="label">เลขที่ KRID ผลงาน 3P:</span><span class="value">{st.session_state.meta_krid or 'ไม่มี'}</span></div>
                    <div class="report-row"><span class="label">เลขที่ KRRN ที่เกี่ยวข้อง:</span><span class="value">{st.session_state.meta_krrn_related or 'ไม่มี'}</span></div>
                    <div class="report-row"><span class="label">เลขที่สิทธิบัตร/อนุสิทธิบัตร:</span><span class="value">{st.session_state.meta_patent_id or 'ไม่มี'}</span></div>
                </div>
            """, unsafe_allow_html=True)
            
            sections_map = {
                'B': ('[Impact] ลดการนำเข้าต่างประเทศ (Section B)', 'b8_impact', 'บาท'),
                'C': ('[Impact] เพิ่มกำไร/รายได้ลูกค้า (Section C)', 'c8_impact', 'บาท'),
                'D': ('[Impact] ประหยัดค่าใช้จ่ายลูกค้า (Section D)', 'd6_impact', 'บาท'),
                'E': ('[Impact] เพิ่มประสิทธิภาพลูกค้า (Section E)', 'e12_impact', 'บาท'),
                'F': ('[Impact] ลดความรุนแรงความเสี่ยง (Section F)', 'f6_impact', 'บาท'),
                'G': ('[Impact] ทักษะบุคลากรเพิ่ม (Section G)', 'g5_impact', 'บาท'),
                'H': ('[Investment] ลงทุนวิจัยต่อยอด (Section H)', 'h4_investment', 'บาท'),
                'I': ('[Investment] ลงทุนในกระบวนการผลิตและบริการ (Section I)', 'i4_investment', 'บาท'),
                'J': ('[Investment] จ้างงานเพิ่ม (Section J)', 'j5_investment', 'บาท'),
                'K': ('[Impact] เปรียบเทียบก่อน-หลัง (Section K)', 'k4_impact', 'บาท'),
            }
            
            st.markdown("<div class='report-section'><h4>รายละเอียดมูลค่าประเมินแยกรายหมวด</h4>", unsafe_allow_html=True)
            for s, (title, payload_key, unit) in sections_map.items():
                if _pc(s):
                    val = eval_payload[payload_key]
                    st.markdown(f'<div class="report-row highlight"><span class="label">🔹 {title}:</span><span class="value">{val:,.2f} {unit}</span></div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="report-total-section">
                    <div class="report-total-row impact"><span class="label">มูลค่า Pre-Impact รวมทั้งหมด:</span><span class="value">{total_impact:,.2f} บาท</span></div>
                    <div class="report-total-row investment"><span class="label">มูลค่า Pre-Investment รวมทั้งหมด:</span><span class="value">{total_investment:,.2f} บาท</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.info("💡 ท่านสามารถบันทึกหรือพิมพ์หน้ารายงานนี้ได้โดยการกดคีย์ลัด **Ctrl + P** บนคีย์บอร์ดของท่าน (ระบบได้จัดเตรียมโครงสร้างหน้าสำหรับการพิมพ์ในรูปแบบ PDF หรือกระดาษ A4 ไว้อย่างเหมาะสมแล้ว)")

    st.markdown("---")
    if st.button("⬅️ ย้อนกลับ (Back)", key="btn_back_tab4", use_container_width=True):
        st.session_state.active_calc_tab = TABS_LIST[2]
        st.rerun()
