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

## 5. Problem: Checklist Lockout after Refresh / Switching Pages
### 🔍 Root Cause
1.  **Page Switch Reset:** Checklist checkbox variables (`chk_a1` through `chk_b5_text`) were initialized to defaults (`False` / `""`) on every load of `pages/checklist.py` without attempting to read from shadow keys.
2.  **No Firestore Backup:** Checklist state was excluded from the Firestore draft object, causing it to be lost upon page refresh. Once refreshed, the checklist was treated as not passed, locking the user out of the Calculator page.

### 🛠️ Solution: Checklist State Mapping & Shadow Sync
*   **Firestore Mapping:** Save `"checklist_passed"` and `"checklist_data"` keys in the Firestore draft.
*   **Checklist Page Shadow Restore:** Initialize checklist variables in `pages/checklist.py` using shadow keys:
    ```python
    if "chk_a1" not in st.session_state:
        st.session_state.chk_a1 = st.session_state.get("_p_chk_a1", False)
    ```
*   **Cloud Load Restoration:** Update `cloud_load_on_startup()` in the calculator page and history loading in `app.py` to restore both active checklist widget keys and shadow backup keys.

---

## 6. Optimization: Intelligent Click-Trap Event Interception
### 🔍 Root Cause
Unconditional 450ms click delay applied to all buttons matching the `isNavBtn` regex. This caused annoying delays for normal navigation when no inputs had changed, yet missed non-matching buttons or checkbox interactions, resulting in race conditions.

### 🛠️ Solution: Conditional Click-Trap Interception
*   **State Change Checker:** Add a lightweight helper `checkIfInputsHaveChanges()` that compares current input values against `data-last-synced` in the DOM without mutative side-effects.
*   **Zero-Delay Default Navigation:** If no unsynced changes are detected, allow clicks to proceed instantly.
*   **Targeted Interception:** If changes exist, stop propagation, prevent default, trigger a full React sync/blur, and click the element after 450ms.

