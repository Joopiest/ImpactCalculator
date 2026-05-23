import streamlit as st
import streamlit.components.v1 as components
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

# Inject background JavaScript to automatically detect browser autofill on input fields
# and dispatch synthetic events so Streamlit's React frontend registers the values.
components.html(
    '''
    <script>
        const syncStreamlitInputs = (forceBlur, skipActive) => {
            const doc = window.parent.document;
            const inputs = doc.querySelectorAll('input, textarea, select');
            let hasChanges = false;
            
            inputs.forEach(input => {
                if (skipActive && input === doc.activeElement) {
                    return;
                }

                const val = input.value;
                const lastVal = input.getAttribute('data-last-synced') || '';
                
                if (val !== lastVal) {
                    input.setAttribute('data-last-synced', val);
                    hasChanges = true;
                    
                    const EventConstructor = window.parent.Event;
                    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.parent.HTMLInputElement.prototype, 'value');
                    const nativeTextAreaValueSetter = Object.getOwnPropertyDescriptor(window.parent.HTMLTextAreaElement.prototype, 'value');
                    
                    if (input.tagName === 'INPUT' && nativeInputValueSetter && nativeInputValueSetter.set) {
                        nativeInputValueSetter.set.call(input, val);
                    } else if (input.tagName === 'TEXTAREA' && nativeTextAreaValueSetter && nativeTextAreaValueSetter.set) {
                        nativeTextAreaValueSetter.set.call(input, val);
                    }
                    
                    input.dispatchEvent(new EventConstructor('input', { bubbles: true }));
                    input.dispatchEvent(new EventConstructor('change', { bubbles: true }));
                    input.dispatchEvent(new EventConstructor('blur', { bubbles: true }));
                }
            });

            if (forceBlur) {
                const active = doc.activeElement;
                if (active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA' || active.tagName === 'SELECT')) {
                    active.blur();
                }
            }
            return hasChanges;
        };

        // Always update the sync reference on the parent window to point to the active iframe
        window.parent._syncStreamlitInputsNow = syncStreamlitInputs;

        if (!window.parent._autofillInterval) {
            let lastSync = 0;
            const syncLoop = (now) => {
                if (now - lastSync > 200) {
                    if (window.parent._syncStreamlitInputsNow) {
                        window.parent._syncStreamlitInputsNow(false, true);
                    }
                    lastSync = now;
                }
                window.parent.requestAnimationFrame(syncLoop);
            };
            window.parent.requestAnimationFrame(syncLoop);
            window.parent._autofillInterval = true;
            
            window.parent.document.addEventListener('click', (e) => {
                const target = e.target.closest('button, [role="button"], [role="option"], [role="tab"], [data-testid="stSegmentedControlItem"], [data-testid="stSidebarNavLink"], label');
                if (target) {
                    const btnText = target.textContent || '';
                    const isNavBtn = btnText.includes('Next') || 
                                      btnText.includes('Back') || 
                                      btnText.includes('ขั้นตอนถัดไป') || 
                                      btnText.includes('ย้อนกลับ') || 
                                      btnText.includes('บันทึก') || 
                                      btnText.includes('เซฟ') || 
                                      btnText.includes('Save') || 
                                      btnText.includes('Details') || 
                                      btnText.includes('Pre-Impact') || 
                                      btnText.includes('Pre-Investment') || 
                                      btnText.includes('Summary') || 
                                      btnText.includes('Submit') || 
                                      btnText.includes('Drafts') || 
                                      btnText.includes('โหลด') || 
                                      btnText.includes('Load') ||
                                      btnText.includes('เข้าสู่ระบบ') ||
                                      btnText.includes('ข้อมูลโครงการ') ||
                                      btnText.includes('ประเมิน') ||
                                      btnText.includes('สถิติ') ||
                                      btnText.includes('Dashboard') ||
                                      btnText.includes('ส่งรายงาน');
                    if (isNavBtn && !target.hasAttribute('data-sync-delayed')) {
                        e.stopPropagation();
                        e.preventDefault();
                        if (window.parent._syncStreamlitInputsNow) {
                            window.parent._syncStreamlitInputsNow(true, false);
                        }
                        target.setAttribute('data-sync-delayed', 'true');
                        window.parent.setTimeout(() => {
                            target.click();
                            target.removeAttribute('data-sync-delayed');
                        }, 400);
                    }
                }
            }, true);
        }
    </script>
    ''',
    height=0,
    width=0
)

# 4. Auth Gate
if not st.session_state.authenticated:
    # Hide sidebar completely on login page
    st.markdown("<style>[data-testid='stSidebar'] { display: none; }</style>", unsafe_allow_html=True)
    
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
                    st.session_state.just_logged_in = True
                    st.success("🔓 เข้าสู่ระบบสำเร็จ กำลังดาวน์โหลดข้อมูล...")
                    st.rerun()
                    
        st.markdown("<div style='text-align: center; margin: 0.5rem 0; color: #64748b; font-size: 0.9rem;'>หรือ</div>", unsafe_allow_html=True)
        if st.button("⚡ ทดลองใช้งานในฐานะผู้มาเยือน (Explore as Guest)", use_container_width=True, type="secondary"):
            st.session_state.authenticated = True
            st.session_state.organization = "Guest"
            st.session_state.employee_id = "Guest"
            st.session_state.just_logged_in = True
            st.success("🔓 เข้าสู่ระบบในฐานะผู้มาเยือนสำเร็จ...")
            st.rerun()

else:
    # 5. Sidebar Navigation Profile & Logout
    st.sidebar.markdown(f"""
    <div class="user-profile-card">
        <span style="font-size: 0.8rem; color: #94a3b8;">ผู้เข้าใช้งาน (User):</span>
        <div style="font-weight: 800; font-size: 1.1rem; color: #818cf8; margin-top: 0.25rem;">👤 {st.session_state.employee_id}</div>
        <div style="font-size: 0.9rem; color: #06b6d4; margin-top: 0.25rem; font-weight: 500;">🏢 สังกัด: {st.session_state.organization}</div>
        <div style="font-size: 0.75rem; color: #a1a1aa; margin-top: 0.5rem; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 0.25rem;">🕒 แก้ไขล่าสุด: 23 พ.ค. 2026 - 17:00 น.</div>
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

                    # Extract loaded values
                    proj_id = item_data.get("project_id", "")
                    proj_name = item_data.get("project_name", "")
                    rep_type = item_data.get("report_type", "รายปี")
                    meta_krrn = item_data.get("meta_krrn", "")
                    meta_krid = item_data.get("meta_krid", "")
                    meta_krrn_related = item_data.get("meta_krrn_related", "")
                    meta_patent_id = item_data.get("meta_patent_id", "")

                    # Set session state keys
                    st.session_state.projectId   = proj_id
                    st.session_state.projectName  = proj_name
                    st.session_state.reportType   = rep_type
                    st.session_state.meta_krrn         = meta_krrn
                    st.session_state.meta_krid         = meta_krid
                    st.session_state.meta_krrn_related = meta_krrn_related
                    st.session_state.meta_patent_id    = meta_patent_id
                    
                    # Set checklist keys so user is not blocked and checklist shows passed
                    st.session_state.checklist_passed = True
                    st.session_state.checklist_data = {
                        "chk_a1": True,
                        "chk_a2": False,
                        "chk_b1": True,
                        "chk_b2": False,
                        "chk_b3": False,
                        "chk_b4": False,
                        "chk_b5": False,
                        "chk_b5_text": ""
                    }
                    st.session_state.chk_a1 = True
                    st.session_state.chk_a2 = False
                    st.session_state.chk_b1 = True
                    st.session_state.chk_b2 = False
                    st.session_state.chk_b3 = False
                    st.session_state.chk_b4 = False
                    st.session_state.chk_b5 = False
                    st.session_state.chk_b5_text = ""
                    
                    # Set widget keys to prevent race conditions on next rerun
                    st.session_state["wid_projectId"]   = proj_id
                    st.session_state["wid_projectName"]  = proj_name
                    st.session_state["wid_reportType"]   = rep_type
                    st.session_state["wid_meta_krrn"]         = meta_krrn
                    st.session_state["wid_meta_krid"]         = meta_krid
                    st.session_state["wid_meta_krrn_related"] = meta_krrn_related
                    st.session_state["wid_meta_patent_id"]    = meta_patent_id
                    
                    # Handle section checkboxes (both widget and persistent shadow keys)
                    sections = item_data.get("sections", {})
                    if selection["type"] == "evaluation":
                        # If it was a submission, we need to map the list back to checkboxes
                        checked_list = item_data.get("sections_checked", [])
                        sections = {s: (s in checked_list) for s in ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']}
                    
                    for s in ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']:
                        val_s = sections.get(s, False)
                        st.session_state[f"chk_{s}"] = val_s
                        st.session_state[f"_p_chk_{s}"] = val_s
                        
                    # Handle field values (both widget and persistent shadow keys)
                    fields = item_data.get("fields", {})
                    field_defaults = {
                        'b1': 0.0, 'b2': 0.0, 'b4': 100.0, 'b5': 1.0, 'b6': "รับจ้างวิจัย (1.0)", 'b7': 100.0,
                        'c1': 0.0, 'c2': 0.0, 'c3': 0.0, 'c4': 0.0, 'c6': "รับจ้างวิจัย (1.0)", 'c7': 100.0,
                        'd1': 0.0, 'd2': 0.0, 'd4': "รับจ้างวิจัย (1.0)", 'd5': 100.0,
                        'e1': 0.0, 'e2': 8.0, 'e6': 0.0, 'e7': 0.0, 'e9': 1.0, 'e10': "รับจ้างวิจัย (1.0)", 'e11': 100.0,
                        'f1': 0.0, 'f2': 100.0, 'f3': 100.0, 'f4': "รับจ้างวิจัย (1.0)", 'f5': 100.0,
                        'g1': 1.0, 'g2': 0.0, 'g3': "รับจ้างวิจัย (1.0)", 'g4': 100.0,
                        'h1': 0.0, 'h2': "รับจ้างวิจัย (1.0)", 'h3': 100.0,
                        'i1': 0.0, 'i2': "รับจ้างวิจัย (1.0)", 'i3': 100.0,
                        'j1': 0.0, 'j2': 100.0, 'j3': "รับจ้างวิจัย (1.0)", 'j4': 100.0,
                        'k1': 0.0, 'k2': "รับจ้างวิจัย (1.0)", 'k3': 100.0
                    }
                    for k, v in field_defaults.items():
                        loaded_val = fields.get(k, v)
                        st.session_state[f"val_{k}"] = loaded_val
                        st.session_state[f"_p_val_{k}"] = loaded_val
                        
                    # Switch to Calculator page and Tab 1 immediately
                    target_tab = "📋 1. ข้อมูลโครงการ (Details)"
                    st.session_state.active_calc_tab = target_tab
                    st.session_state.segmented_calc_tab = target_tab
                    st.session_state.last_active_tab = target_tab
                    
                    # Set cloud loaded flag so calculator's cloud_load_on_startup doesn't overwrite
                    st.session_state[f"_cloud_loaded_{proj_id}"] = True
                    st.session_state["last_loaded_projectId"] = proj_id
                    
                    st.sidebar.success(f"✅ โหลดข้อมูลสำเร็จ!")
                    st.switch_page("pages/calculator.py")
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
    
    # Redirect immediately to Checklist if just logged in
    if st.session_state.get("just_logged_in"):
        st.session_state.just_logged_in = False
        st.switch_page("pages/checklist.py")
        
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
        # Clear all persistent shadow keys
        keys_to_clear.extend([k for k in st.session_state.keys() if k.startswith("_p_") or k.startswith("val_") or k.startswith("chk_") or k.startswith("wid_")])
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
                
        st.rerun()
        
    pg.run()
