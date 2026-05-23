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

## 2. Problem: Browser Autofill Not Registering
### 🔍 Root Cause
Browser autofill (Chrome/Edge/Password Managers) often injects values into `<input>` tags without triggering standard JavaScript `input` or `change` events. Streamlit's React frontend doesn't "see" these values, so they never reach the Python backend.

### 🛠️ Solution: Aggressive JavaScript Sync Engine
*   **React Value Setter Override:** Standard `.value = val` assignments are ignored by React's internal state trackers. We must use the native property descriptor setter.
*   **Cross-Iframe Events:** Since Streamlit components run in iframes, we must use `window.parent.Event` to ensure the main Streamlit window hears the triggers.
*   **Click-Trap Navigation:** Intercept clicks on navigation buttons and tabs. Prevent the click, force a manual `blur()` and `sync` on all inputs, wait 450ms, then resume the click.
*   **Implementation Key:**
    ```javascript
    const EventConstructor = window.parent.Event;
    const nativeSetter = Object.getOwnPropertyDescriptor(window.parent.HTMLInputElement.prototype, 'value');
    nativeSetter.set.call(input, val);
    input.dispatchEvent(new EventConstructor('input', { bubbles: true }));
    input.dispatchEvent(new EventConstructor('blur', { bubbles: true }));
    ```

---

## 3. Problem: StreamlitAPIException (State Conflict)
### 🔍 Root Cause
Trying to programmatically update a widget-linked key (e.g., `st.session_state.wid_projectId = val`) *after* that widget has already been rendered on the current screen. Streamlit throws an exception to prevent inconsistent UI states.

### 🛠️ Solution: Defensive Callback Pattern
*   Perform all state normalization (like `.upper()` or formatting) inside the `on_change` callback function, **not** inside the main page flow or button blocks.
*   Use `try-except` blocks around widget key assignments to prevent app crashes during unexpected race conditions.

---

## 4. Feature: Unique Project ID Enforcement
### 🛠️ Solution: "Retrieve to Overwrite" Workflow
*   **Step 1:** Check Firestore immediately when a Project ID is entered.
*   **Step 2:** If ID exists, present a choice: **"Delete & Start Fresh"** or **"Retrieve to Overwrite"**.
*   **Step 3:** Loading data is done by populating both the Widget Keys (for UI) and Shadow Keys (for persistence).
*   **Step 4:** Locked Autosave: Prevent `autosave_to_cloud` from firing until the user has explicitly resolved the conflict via the provided buttons.

---

**Note to Antigravity IDE:** When dealing with high-stakes data entry in Streamlit, always prioritize **Shadow Key Cloning** over standard widget state. Direct browser-to-backend communication via synthetic JS events is required for a professional "Autofill" experience.
