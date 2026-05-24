# 🧠 Antigravity IDE Learning Note: Streamlit Persistence & Autofill

**Session Date:** May 23, 2026
**Project:** Impact & Investment Evaluation System (JoopFirebase)

---

## 1. Problem: Data Loss during Tab Switching
### 🔍 Root Cause
In Streamlit, when a user switches tabs, any widgets in the hidden tab are **unmounted** and their keys are deleted from `st.session_state`. If the user returns to that tab, the widgets are re-rendered with default values unless specifically restored. 

### 🛠️ Solution: Top-Level Shadow Key Cloning
*   **The Logic:** At the very top of the script (before any other logic runs), iterate through all existing keys in `st.session_state`.
*   **Persistent Shadow Keys:** Clone any keys starting with `val_` or `chk_` into a "Shadow Key" (e.g., `_p_val_...`).
*   **Why it works:** Because this loop runs at the **start** of a rerun (before Streamlit processes the "delete unmounted widgets" cleanup), it catches the values from the *previous* active tab just in time.
*   **Implementation:**
    ```python
    for _k, _v in list(st.session_state.items()):
        if _k.startswith("val_") or _k.startswith("chk_"):
            st.session_state[f"_p_{_k}"] = _v
    ```

---

## 2. Problem: Browser Autofill & Delayed Tab Switching
### 🔍 Root Cause
1.  **Autofill Detection:** Browser autofill (Chrome/Edge/Password Managers) often injects values into `<input>` tags without triggering standard JavaScript `input` or `change` events. Streamlit's React frontend doesn't "see" these values.
2.  **Detached Element Clicks:** The click-trap navigation engine intercepts clicks on buttons/tabs, blurs the active input, waits 450ms, and then triggers the original click. However, since the blur event triggers a rerun, Streamlit re-renders components. The original clicked element becomes **detached** from the DOM tree, and clicking a detached element does not bubble to React.

### 🛠️ Solution: Event Interception & Fresh DOM Lookups
*   **Aggressive Sync:** Dispatch synthetic `input`, `change`, and `blur` events using React value setters inside the parent window context.
*   **Click-Trap Event Blocking:** Use `e.stopPropagation()` and `e.preventDefault()` on intercepted clicks to block instant navigation, allowing the blur events to process first.
*   **Fresh DOM Node Lookup:** Save the element text and `data-testid` before unmounting. In the `setTimeout` callback, query the *active* DOM tree to find the newly-rendered matching element instead of clicking the detached reference.
*   **Implementation Key:**
    ```javascript
    window.parent.document.addEventListener('click', (e) => {
        const target = e.target.closest('button, [role="button"], [role="tab"], ...');
        if (target && !target.hasAttribute('data-sync-delayed')) {
            e.stopPropagation();
            e.preventDefault();
            
            // Sync current active element values
            if (window.parent._syncStreamlitInputsNow) {
                window.parent._syncStreamlitInputsNow(true, false);
            }
            
            const savedText = target.textContent;
            const savedTestId = target.getAttribute('data-testid');
            
            window.parent.setTimeout(() => {
                const doc = window.parent.document;
                let found = null;
                // Query fresh active DOM elements matching the saved text or ID
                const elements = doc.querySelectorAll('button, [role="button"], [role="tab"], ...');
                for (let el of elements) {
                    if (el.textContent === savedText) { found = el; break; }
                }
                if (!found && savedTestId) {
                    found = doc.querySelector(`[data-testid="${savedTestId}"]`);
                }
                if (!found) found = target; // Fallback
                
                found.setAttribute('data-sync-delayed', 'true');
                found.click();
                found.removeAttribute('data-sync-delayed');
            }, 450);
        }
    }, true);
    ```

---

## 3. Problem: Streamlit Rerun Callback Bypassing
### 🔍 Root Cause
Streamlit is single-threaded per session. When multiple events are queued (e.g. typing in a field then immediately clicking a navigation tab), Streamlit aborts the first rerun and processes the new rerun. In doing so, widget `on_change` callbacks (such as `sync_project_meta` setting the alignment flag `_cloud_loaded_{projectId} = True`) can be bypassed or skipped, leaving the app in an unaligned state.

### 🛠️ Solution: Defensive Main-Flow Fallback
*   Do **NOT** rely solely on `on_change` callbacks for setting critical workflow flags.
*   Implement a check in the main execution flow that executes on every rerun to verify and set states defensively.
*   **Implementation:**
    ```python
    proj_id = st.session_state.get("projectId", "").strip().upper()
    if proj_id and firebase_config.is_db_connected():
        cache_flag = f"_cloud_loaded_{proj_id}"
        if cache_flag not in st.session_state:
            # Query Firestore defensively to see if it is a fresh project
            has_draft = firebase_config.check_project_draft(st.session_state.employee_id, proj_id)
            has_eval = firebase_config.check_project_submitted(proj_id)
            if not has_draft and not has_eval:
                st.session_state[cache_flag] = True
    ```

---

## 4. Feature: Unique Project ID Enforcement & Conflicts
### 🛠️ Solution: "Retrieve to Overwrite" Workflow
*   **Conflict Detection:** Check Firestore when a Project ID is entered.
*   **State Alignment:** Conflict resolution buttons ("Load Draft", "Delete & Start Fresh", "Retrieve to Overwrite") must explicitly set the `_cloud_loaded_{projectId} = True` flag in their callbacks to align states and enable autosave.

---

## 5. Problem: Ghost State Resurgence and Exclusivity Cascades (The Revisit Bug)
### 🔍 Root Cause
1. **Ghost States on Revisit:** When a user navigates between tabs, Streamlit garbage collects unrendered widgets. Upon return, if the session state wasn't perfectly synchronized, widgets (e.g., Checkbox B) might be initialized with a stale `True` value.
2. **Exclusivity Cascade:** If the app has an exclusivity rule (e.g., "If B is checked, C must be unchecked"), the ghost state of B triggers the rule, auto-unchecking C. This causes Section C's UI and text inputs to disappear, giving the illusion of data loss.
3. **Missing Payload Keys:** The `get_current_state_payload` function had hardcoded lists of keys to save to Firestore. Some keys (e.g., `c6`, `c7`) were missing, so loading a draft failed to restore them.

### 🛠️ Solution: Hard Read-Time Lock & Payload Auditing
*   **Read-Time Exclusivity Enforcement:** Instead of only enforcing rules on click events (`on_change`), enforce them inside the central read function (`_pc()`). Before returning a widget's value, verify its validity against conflicting states. If invalid, forcefully overwrite it to `False` in `st.session_state` immediately.
*   **Implementation:**
    ```python
    def _pc(section):
        val = ... # Read from session state or shadow key
        
        # Hard Exclusivity Enforcement
        if section == 'B' and val:
            for s in ['C', 'D', 'E', 'F', 'G']:
                if st.session_state.get(f"_p_chk_{s}") or st.session_state.get(f"chk_{s}"):
                    st.session_state[p_key] = False
                    return False
        return val
    ```
*   **Payload Auditing:** Ensure that the dictionary used for Firestore synchronization explicitly maps all UI fields (e.g., `c1, c2, c3, c4, c6, c7`).
