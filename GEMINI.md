# 🌌 Project Mandates: JoopFirebase

## 🛠️ Critical Technical Rules
The following architectural patterns are MANDATORY for this project. Before modifying state management or UI sync logic, you MUST read the learning note:
👉 [LEARNING_NOTE_ANTIGRAVITY.md](./NAPAT_github_deploy/LEARNING_NOTE_ANTIGRAVITY.md)

### 1. State Persistence
- **Rule:** ALWAYS use the "Top-Level Shadow Key Cloning" pattern found in `pages/calculator.py`. 
- **Reason:** To prevent data loss when Streamlit unmounts widgets during tab switches.

### 2. Browser Autofill
- **Rule:** Capturing autofill requires the aggressive JS sync engine located in `app.py` and `pages/calculator.py`.
- **Constraint:** Do NOT simplify the JS sync logic; it requires `window.parent.Event` and native prototype overrides to work within Streamlit's iframe architecture.

### 3. Conflict Resolution
- **Rule:** Project IDs must be unique. Follow the "Retrieve to Overwrite" workflow defined in the documentation.

### 4. Modification Timestamp
- **Rule:** Before committing or pushing any code changes, ALWAYS update the latest edit timestamp inside the sidebar user profile in `app.py`.
- **Format:** Use the format `🕒 แก้ไขล่าสุด: [วัน] พ.ค. [ปี ค.ศ.] - [เวลา] น.` with the actual local time of the modification (e.g. `23 พ.ค. 2026 - 16:06 น.`).
