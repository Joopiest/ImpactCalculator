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
        st.sidebar.markdown("<div style='font-size: 0.75rem; color: #10b981; margin-bottom: 1rem;'>🟢 เชื่อมต่อคลาวด์ Firebase สำเร็จ</div>", unsafe_allow_html=True)
    else:
        st.sidebar.markdown("<div style='font-size: 0.75rem; color: #ef4444; margin-bottom: 1rem;'>🔴 ไม่พบการเชื่อมต่อ Firebase (ทำงานในระบบ Local)</div>", unsafe_allow_html=True)

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
        st.session_state.authenticated = False
        st.session_state.employee_id = ""
        st.session_state.organization = ""
        st.session_state.checklist_passed = False
        st.session_state.checklist_data = {}
        st.rerun()
        
    pg.run()
