import streamlit as st
import os
import firebase_config

# 1. Page Configuration
st.set_page_config(
    page_title="Impact & Investment Evaluation",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Session State Initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "employee_id" not in st.session_state:
    st.session_state.employee_id = ""
if "organization" not in st.session_state:
    st.session_state.organization = ""
if "checklist_passed" not in st.session_state:
    st.session_state.checklist_passed = False
if "checklist_data" not in st.session_state:
    st.session_state.checklist_data = {}

# 3. Inject Custom CSS
def load_css():
    css_path = os.path.join("css", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    else:
        st.warning("Custom CSS file not found.")

load_css()

# 4. Auth Gate
if not st.session_state.authenticated:
    # Beautiful auth screen
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""
        <div class="auth-card">
            <div class="icon" style="font-size: 3rem;">🌌</div>
            <div class="auth-title">Impact & Investment Evaluation</div>
            <div class="auth-subtitle">ระบบประเมินผลลัพธ์และผลกระทบงานวิจัย (Pre-Impact)</div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            st.markdown("<h4 style='text-align: center; color: #3b82f6; margin-bottom: 1.5rem;'>ลงชื่อเข้าใช้งาน</h4>", unsafe_allow_html=True)
            
            org = st.selectbox(
                "หน่วยงาน / สังกัด (Organization)",
                ["NSTDA", "NECTEC", "BIOTEC", "MTEC", "NANOTEC", "ENTEC", "Guest"],
                index=1 # NECTEC default
            )
            
            emp_id = ""
            if org != "Guest":
                emp_id = st.text_input("รหัสพนักงาน (Employee ID)", value="", help="ป้อนรหัสพนักงานอย่างน้อย 3 หลัก")
            else:
                st.info("สำหรับผู้มาเยือน (Guest) ไม่จำเป็นต้องระบุรหัสพนักงาน")
                
            submit_button = st.form_submit_value = st.form_submit_button("เข้าสู่ระบบ (Log In)", use_container_width=True)
            
            if submit_button:
                if org != "Guest" and len(emp_id.strip()) < 3:
                    st.error("❌ กรุณากรอกรหัสพนักงานอย่างน้อย 3 ตัวอักษร")
                else:
                    st.session_state.authenticated = True
                    st.session_state.organization = org
                    st.session_state.employee_id = emp_id.strip() if org != "Guest" else "Guest"
                    st.success("🔓 เข้าสู่ระบบสำเร็จ กำลังดาวน์โหลดข้อมูล...")
                    st.rerun()
                    
        st.markdown("<div style='text-align: center; margin: 0.5rem 0; color: #64748b; font-size: 0.9rem;'>หรือ</div>", unsafe_allow_html=True)
        if st.button("⚡ ทดลองใช้งานในฐานะผู้มาเยือน (Explore as Guest)", use_container_width=True, type="secondary"):
            st.session_state.authenticated = True
            st.session_state.organization = "Guest"
            st.session_state.employee_id = "Guest"
            st.success("🔓 เข้าสู่ระบบในฐานะผู้มาเยือนสำเร็จ...")
            st.rerun()

else:
    # 5. Sidebar Navigation Profile & Logout
    st.sidebar.markdown(f"""
    <div class="user-profile-card">
        <span style="font-size: 0.8rem; color: #94a3b8;">ผู้เข้าใช้งาน (User):</span>
        <div style="font-weight: 800; font-size: 1.1rem; color: #818cf8; margin-top: 0.25rem;">👤 {st.session_state.employee_id}</div>
        <div style="font-size: 0.9rem; color: #06b6d4; margin-top: 0.25rem; font-weight: 500;">🏢 สังกัด: {st.session_state.organization}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Firestore Connection Alert
    if firebase_config.is_db_connected():
        st.sidebar.markdown("<div style='font-size: 0.75rem; color: #10b981; margin-bottom: 0.5rem;'>🟢 เชื่อมต่อคลาวด์ Firebase สำเร็จ</div>", unsafe_allow_html=True)
    else:
        st.sidebar.markdown("<div style='font-size: 0.75rem; color: #ef4444; margin-bottom: 0.5rem;'>🔴 ไม่พบการเชื่อมต่อ Firebase (ทำงานในระบบ Local)</div>", unsafe_allow_html=True)

    # ── HISTORY & DRAFTS (sidebar) ──────────────────────────────────────────
    if firebase_config.is_db_connected():
        st.sidebar.markdown("---")
        st.sidebar.markdown("<div style='font-size:0.8rem; font-weight:700; color:#818cf8; margin-bottom:0.5rem;'>📂 ประวัติงานของฉัน (My History)</div>", unsafe_allow_html=True)
        
        # Load both Drafts and Evaluations
        drafts = firebase_config.load_drafts(st.session_state.employee_id)
        evals = firebase_config.load_user_evaluations(st.session_state.employee_id)
        
        options_map = {}
        for d in drafts:
            label = f"📝 [ร่าง] {d['project_id']} — {d['project_name']}"
            options_map[label] = {"data": d, "type": "draft"}
        for e in evals:
            label = f"✅ [ส่งแล้ว] {e['project_id']} — {e['project_name']}"
            options_map[label] = {"data": e, "type": "evaluation"}
            
        if options_map:
            selected_label = st.sidebar.selectbox(
                "เลือกรายการเพื่อโหลดใหม่:",
                ["— เลือกรายการ —"] + list(options_map.keys()),
                key="sidebar_history_selector",
                label_visibility="collapsed"
            )
            
            if selected_label != "— เลือกรายการ —":
                selection = options_map[selected_label]
                item_data = selection["data"]
                
                if st.sidebar.button("🔄 โหลดข้อมูลนี้", use_container_width=True, key="sidebar_load_btn", type="primary"):
                    # DEBUG: Trace the data coming from Firestore
                    try:
                        with open("firestore_debug.log", "a", encoding="utf-8") as f:
                            f.write(f"\n--- LOADING {selection['type'].upper()} ---\n")
                            f.write(f"Project ID: {item_data.get('project_id')}\n")
                            f.write(f"Fields found: {list(item_data.get('fields', {}).keys())}\n")
                    except: pass

                    st.session_state.projectId   = item_data.get("project_id", "")
                    st.session_state.projectName  = item_data.get("project_name", "")
                    st.session_state.reportType   = item_data.get("report_type", "รายปี")
                    
                    # Metadata fields
                    st.session_state.meta_krrn         = item_data.get("meta_krrn", "")
                    st.session_state.meta_krid         = item_data.get("meta_krid", "")
                    st.session_state.meta_krrn_related = item_data.get("meta_krrn_related", "")
                    st.session_state.meta_patent_id    = item_data.get("meta_patent_id", "")
                    
                    # Handle section checkboxes
                    sections = item_data.get("sections", {})
                    if selection["type"] == "evaluation":
                        # If it was a submission, we need to map the list back to checkboxes
                        checked_list = item_data.get("sections_checked", [])
                        sections = {s: (s in checked_list) for s in ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']}
                    
                    for s in ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']:
                        st.session_state[f"chk_{s}"] = sections.get(s, False)
                        st.session_state[f"_p_chk_{s}"] = sections.get(s, False)
                        
                    # Handle field values
                    fields = item_data.get("fields", {})
                    if selection["type"] == "evaluation":
                        # If it was a submission, map the individual impact fields back to inputs
                        # Note: This is a partial restoration since evaluation doesn't store all raw inputs,
                        # but we can try to restore the main ones if they were saved in the evaluation payload.
                        # For now, we trust the 'fields' dict if it exists.
                        pass
                    
                    for k, v in fields.items():
                        st.session_state[f"val_{k}"] = v
                        st.session_state[f"_p_val_{k}"] = v
                        
                    # Switch to Calculator page and first tab
                    target_tab = "📋 1. ข้อมูลโครงการ (Details)"
                    st.session_state.active_calc_tab = target_tab
                    st.session_state.segmented_calc_tab = target_tab
                    st.sidebar.success(f"✅ โหลดข้อมูลสำเร็จ! กรุณาไปที่หน้าเครื่องประเมิน")
                    st.rerun()
        else:
            st.sidebar.caption("ยังไม่มีประวัติการบันทึกหรือส่งรายงาน")

    # 6. Page Routing
    pages = [
        st.Page("pages/home.py", title="หน้าแรก", icon="🏠"),
        st.Page("pages/checklist.py", title="Checklist ความพร้อม", icon="📋"),
        st.Page("pages/calculator.py", title="เครื่องประเมิน Pre-Impact", icon="🧮"),
        st.Page("pages/dashboard.py", title="Dashboard สถิติ", icon="📊"),
        st.Page("pages/definitions.py", title="คำนิยาม & ความรู้", icon="📖")
    ]
    
    pg = st.navigation(pages)
    
    # Render Logout Button at bottom of sidebar
    if st.sidebar.button("ออกจากระบบ (Log Out)", use_container_width=True, type="secondary"):
        # Clear all user and project data
        keys_to_clear = [
            "authenticated", "employee_id", "organization", 
            "checklist_passed", "checklist_data",
            "projectId", "projectName", "reportType",
            "meta_krrn", "meta_krid", "meta_krrn_related", "meta_patent_id",
            "active_calc_tab", "segmented_calc_tab", "last_active_tab"
        ]
        # Also clear all widget and persistent keys
        for k in list(st.session_state.keys()):
            if k.startswith(("wid_", "val_", "chk_", "_p_")):
                keys_to_clear.append(k)
        
        for k in keys_to_clear:
            if k in st.session_state:
                del st.session_state[k]
                
        st.rerun()
        
    pg.run()
