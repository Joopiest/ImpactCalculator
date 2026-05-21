# 🚀 Deployment Guide — Impact & Investment Evaluation System
# คู่มือการติดตั้งและ Deploy ระบบประเมินผลกระทบและการลงทุน

> **Version:** 1.0  
> **Last Updated:** May 2026  
> **Audience:** Developers, System Administrators  

---

## Table of Contents

- [1. Prerequisites](#1-prerequisites)
- [2. Local Development Setup](#2-local-development-setup)
- [3. Streamlit Cloud Deployment](#3-streamlit-cloud-deployment)
- [4. Firebase Project Setup](#4-firebase-project-setup)
- [5. Configuring Streamlit Secrets](#5-configuring-streamlit-secrets)
- [6. GitHub Repository Management](#6-github-repository-management)
- [7. Environment Variables](#7-environment-variables)
- [8. Troubleshooting Deployment Issues](#8-troubleshooting-deployment-issues)
- [9. Updating and Redeploying](#9-updating-and-redeploying)
- [10. Security Best Practices](#10-security-best-practices)
- [11. Monitoring and Maintenance](#11-monitoring-and-maintenance)

---

## 1. Prerequisites

### Required Software

| Software | Version | Purpose | Download |
|----------|---------|---------|----------|
| **Python** | 3.9 or higher | Runtime environment | [python.org](https://www.python.org/downloads/) |
| **pip** | Latest | Package manager | Included with Python |
| **Git** | 2.30+ | Version control | [git-scm.com](https://git-scm.com/) |
| **Node.js** | 16+ (optional) | For some dev tools | [nodejs.org](https://nodejs.org/) |

### Required Accounts

| Account | Purpose | URL |
|---------|---------|-----|
| **GitHub** | Source code hosting | [github.com](https://github.com) |
| **Google Cloud** | Firebase services | [console.cloud.google.com](https://console.cloud.google.com) |
| **Firebase** | Database & authentication | [console.firebase.google.com](https://console.firebase.google.com) |
| **Streamlit Cloud** | Production hosting | [share.streamlit.io](https://share.streamlit.io) |

### คำอธิบายภาษาไทย (Thai Explanation)

> **สิ่งที่ต้องเตรียม:**
> - ติดตั้ง Python เวอร์ชัน 3.9 ขึ้นไป
> - ติดตั้ง Git สำหรับจัดการโค้ด
> - สร้างบัญชี GitHub, Google Cloud, Firebase, และ Streamlit Cloud
> - เตรียม Firebase Service Account JSON credentials

---

## 2. Local Development Setup

### Step 1: Clone the Repository

```bash
# Clone from GitHub
git clone https://github.com/Joopiest/ImpactCalculator.git
cd ImpactCalculator

# Or clone from internal GitLab
git clone https://git.nstda.or.th/NECTEC-Roks/joopfirebase_gitlab.git
cd joopfirebase_gitlab
```

### Step 2: Create a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Contents of `requirements.txt`:**
```
streamlit>=1.35.0
firebase-admin>=6.5.0
pandas>=2.0.0
plotly>=5.15.0
```

### Step 4: Set Up Firebase Credentials (Local)

1. Download your Firebase service account JSON key (see [Section 4](#4-firebase-project-setup))
2. Place the file in the project root directory
3. Name it `serviceAccountKey.json` (or update the path in `firebase_config.py`)

```
ImpactCalculator/
├── serviceAccountKey.json    ← Place here
├── app.py
├── firebase_config.py
└── ...
```

### Step 5: Configure Local Streamlit Secrets (Optional)

Create the file `.streamlit/secrets.toml` for local secrets:

```bash
# Create directory if it doesn't exist
mkdir -p .streamlit
```

Create `.streamlit/secrets.toml`:
```toml
[firebase]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "firebase-adminsdk-xxxxx@your-project-id.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40your-project-id.iam.gserviceaccount.com"
```

> ⚠️ **Important:** Add `.streamlit/secrets.toml` and `serviceAccountKey.json` to your `.gitignore` to prevent accidental commits of credentials.

### Step 6: Run the Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501` in your default browser.

### Step 7: Verify

- ✅ Login page displays correctly
- ✅ Firebase connection indicator shows "Connected" (green)
- ✅ All 5 pages accessible via sidebar
- ✅ Dark theme renders properly

### ขั้นตอนภาษาไทย (Thai Step-by-Step)

> **การติดตั้งแบบ Local:**
> 1. โคลนโปรเจกต์จาก GitHub: `git clone https://github.com/Joopiest/ImpactCalculator.git`
> 2. สร้าง Virtual Environment: `python -m venv venv`
> 3. เปิดใช้งาน: `venv\Scripts\activate` (Windows) หรือ `source venv/bin/activate` (Mac/Linux)
> 4. ติดตั้ง Dependencies: `pip install -r requirements.txt`
> 5. วาง Firebase credential JSON ไว้ในโฟลเดอร์โปรเจกต์
> 6. รันแอป: `streamlit run app.py`
> 7. เปิด `http://localhost:8501` ในเบราว์เซอร์

---

## 3. Streamlit Cloud Deployment

### Step 1: Prepare GitHub Repository

Ensure your GitHub repository (`Joopiest/ImpactCalculator`) contains:

```
✅ app.py                    (entry point)
✅ requirements.txt          (dependencies)
✅ .streamlit/config.toml    (theme config)
✅ firebase_config.py        (Firebase module)
✅ css/style.css             (styling)
✅ pages/*.py                (page modules)
❌ serviceAccountKey.json    (DO NOT commit!)
❌ .streamlit/secrets.toml   (DO NOT commit!)
```

### Step 2: Connect to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **"New app"**
4. Select:
   - **Repository:** `Joopiest/ImpactCalculator`
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. Click **"Advanced settings"** before deploying

### Step 3: Configure Secrets in Streamlit Cloud

In the **"Advanced settings"** panel → **Secrets** section, paste your Firebase credentials in TOML format:

```toml
[firebase]
type = "service_account"
project_id = "your-firebase-project-id"
private_key_id = "abc123def456"
private_key = "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASC...\n-----END PRIVATE KEY-----\n"
client_email = "firebase-adminsdk-xxxxx@your-project-id.iam.gserviceaccount.com"
client_id = "123456789012345678901"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40your-project-id.iam.gserviceaccount.com"
```

> ⚠️ **Critical:** The `private_key` value must have `\n` literal characters (not actual newlines) for proper TOML parsing.

### Step 4: Set Python Version (Optional)

If needed, you can pin the Python version by adding a `runtime.txt` file to the repo root:

```
python-3.11
```

### Step 5: Deploy

1. Click **"Deploy!"**
2. Wait for the build process (1-3 minutes)
3. Streamlit Cloud will provide a URL like: `https://your-app.streamlit.app`

### Step 6: Verify Deployment

- ✅ App loads at the assigned URL
- ✅ Login page renders with dark theme
- ✅ Firebase connection status shows "Connected"
- ✅ Submit a test evaluation and verify it appears in Firestore
- ✅ Dashboard loads data correctly

### ขั้นตอน Deploy บน Cloud ภาษาไทย

> **การ Deploy บน Streamlit Cloud:**
> 1. เข้าไปที่ [share.streamlit.io](https://share.streamlit.io) แล้วล็อกอินด้วย GitHub
> 2. คลิก "New app" → เลือก Repository, Branch, และ Main file
> 3. คลิก "Advanced settings" → วาง Firebase credentials ในช่อง Secrets (รูปแบบ TOML)
> 4. คลิก "Deploy!" → รอ 1-3 นาที
> 5. ตรวจสอบว่าแอปทำงานถูกต้อง

---

## 4. Firebase Project Setup

### Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Click **"Add project"** (or **"Create a project"**)
3. Enter project name (e.g., `impact-calculator`)
4. Disable Google Analytics (optional, not needed for this app)
5. Click **"Create Project"**

### Step 2: Enable Firestore Database

1. In the Firebase console, go to **"Build" → "Firestore Database"**
2. Click **"Create database"**
3. Select **"Start in production mode"**
4. Choose a Cloud Firestore location closest to your users:
   - For Thailand: `asia-southeast1` (Singapore) or `asia-southeast2` (Jakarta)
5. Click **"Enable"**

### Step 3: Create Service Account

1. Go to **"Project settings"** (gear icon) → **"Service accounts"**
2. Click **"Generate new private key"**
3. Click **"Generate key"** — a JSON file will be downloaded
4. **Save this file securely** — it provides full admin access to your Firebase project

### Step 4: Set Up Firestore Security Rules

In **"Build" → "Firestore Database" → "Rules"**, set:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Deny all client-side access (server-side Admin SDK bypasses these rules)
    match /{document=**} {
      allow read, write: if false;
    }
  }
}
```

> **Note:** Since the app uses the Firebase Admin SDK (server-side), all operations bypass Firestore rules. The rules above deny all client-side access for security.

### Step 5: Initialize Collections

The app will automatically create the `evaluations` and `drafts` collections when the first document is written. No manual initialization needed.

### การตั้งค่า Firebase ภาษาไทย

> **ขั้นตอนการตั้งค่า Firebase:**
> 1. ไปที่ [Firebase Console](https://console.firebase.google.com) → สร้าง Project ใหม่
> 2. เปิด Firestore Database → เลือก Production Mode
> 3. เลือก Location: `asia-southeast1` (สิงคโปร์) สำหรับประเทศไทย
> 4. สร้าง Service Account → ดาวน์โหลด JSON key
> 5. ตั้งค่า Security Rules ให้ปิดการเข้าถึงจาก Client-side
> 6. ⚠️ เก็บ JSON key ไว้อย่างปลอดภัย ห้ามอัปโหลดขึ้น Git!

---

## 5. Configuring Streamlit Secrets

### Understanding the Secret Format

Streamlit Secrets uses **TOML format**. The Firebase service account JSON must be converted to TOML.

### JSON to TOML Conversion

**Original JSON (from Firebase Console):**
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "key-id-here",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEv...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk@your-project.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

**Converted TOML (for Streamlit Secrets):**
```toml
[firebase]
type = "service_account"
project_id = "your-project-id"
private_key_id = "key-id-here"
private_key = "-----BEGIN PRIVATE KEY-----\nMIIEv...\n-----END PRIVATE KEY-----\n"
client_email = "firebase-adminsdk@your-project.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

### Key Conversion Rules

| Rule | Description |
|------|-------------|
| Wrap in `[firebase]` section | All keys go under the `[firebase]` TOML section |
| Remove curly braces | TOML doesn't use `{}` |
| Remove commas | TOML uses newlines, not commas |
| Keep `\n` in private_key | Newlines must be literal `\n` within the string |
| Use double quotes | All string values in double quotes |

### Where to Configure

| Environment | Location |
|-------------|----------|
| **Streamlit Cloud** | App Settings → Secrets (web UI) |
| **Local Development** | `.streamlit/secrets.toml` file |

### Accessing Secrets in Code

```python
import streamlit as st

# Access Firebase credentials
firebase_config = dict(st.secrets["firebase"])
# Returns a dictionary matching the service account JSON structure
```

---

## 6. GitHub Repository Management

### Repository Information

| Property | Value |
|----------|-------|
| **Primary (GitHub)** | [github.com/Joopiest/ImpactCalculator](https://github.com/Joopiest/ImpactCalculator) |
| **Mirror (GitLab)** | [git.nstda.or.th/NECTEC-Roks/joopfirebase_gitlab](https://git.nstda.or.th/NECTEC-Roks/joopfirebase_gitlab) |
| **Default Branch** | `main` |

### Branching Strategy

```
main ─────────────────────────────────── (production, auto-deploys)
  │
  ├── feature/new-export-function ────── (feature branches)
  ├── fix/dashboard-loading-error ────── (bug fixes)
  └── docs/update-user-manual ────────── (documentation)
```

### Recommended Workflow

```bash
# 1. Create feature branch
git checkout -b feature/my-new-feature

# 2. Make changes and commit
git add .
git commit -m "feat: add new export functionality"

# 3. Push to GitHub
git push origin feature/my-new-feature

# 4. Create Pull Request on GitHub
# 5. Review and merge to main
# 6. Streamlit Cloud auto-deploys from main
```

### Setting Up Dual Remotes

```bash
# Add GitHub remote
git remote add github https://github.com/Joopiest/ImpactCalculator.git

# Add GitLab remote
git remote add gitlab https://git.nstda.or.th/NECTEC-Roks/joopfirebase_gitlab.git

# Push to both
git push github main
git push gitlab main
```

### Essential `.gitignore`

```gitignore
# Firebase credentials
serviceAccountKey.json
*.json.bak

# Streamlit secrets
.streamlit/secrets.toml

# Python
__pycache__/
*.py[cod]
*$py.class
venv/
.env

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

---

## 7. Environment Variables

### Configuration Reference

| Variable / Config | Location | Purpose |
|-------------------|----------|---------|
| `[firebase]` section | `st.secrets` or `.streamlit/secrets.toml` | Firebase service account credentials |
| `primaryColor` | `.streamlit/config.toml` | UI accent color (#6366f1) |
| `backgroundColor` | `.streamlit/config.toml` | Main background (#090d16) |
| `secondaryBackgroundColor` | `.streamlit/config.toml` | Card/sidebar background (#111827) |
| `textColor` | `.streamlit/config.toml` | Primary text color (#e5e7eb) |

### `.streamlit/config.toml` (Theme Configuration)

```toml
[theme]
primaryColor = "#6366f1"
backgroundColor = "#090d16"
secondaryBackgroundColor = "#111827"
textColor = "#e5e7eb"
font = "sans serif"
```

### Runtime Configuration

| Setting | Default | Override |
|---------|---------|---------|
| Port | 8501 | `streamlit run app.py --server.port 8080` |
| Address | localhost | `streamlit run app.py --server.address 0.0.0.0` |
| Headless | false | `streamlit run app.py --server.headless true` |
| Browser | auto-open | `--server.headless true` to disable |

---

## 8. Troubleshooting Deployment Issues

### Issue 1: `ModuleNotFoundError: No module named 'firebase_admin'`

**Cause:** Dependencies not installed correctly.

**Solution:**
```bash
pip install -r requirements.txt
# Or specifically:
pip install firebase-admin>=6.5.0
```

**On Streamlit Cloud:** Ensure `requirements.txt` is in the repository root.

---

### Issue 2: Firebase Connection Failed / `DefaultCredentialsError`

**Cause:** Firebase credentials not found or invalid.

**Solution (Local):**
- Verify `serviceAccountKey.json` exists in the project root
- Check the JSON file is valid (not truncated)
- Try: `python -c "import json; json.load(open('serviceAccountKey.json'))"`

**Solution (Cloud):**
- Go to Streamlit Cloud → App Settings → Secrets
- Verify the `[firebase]` section is present and correctly formatted
- Check that `private_key` has `\n` literals, not actual newlines

---

### Issue 3: `StreamlitAPIException: st.secrets has no attribute 'firebase'`

**Cause:** Secrets not configured in Streamlit Cloud.

**Solution:**
1. Go to your app on [share.streamlit.io](https://share.streamlit.io)
2. Click the three dots (**⋮**) → **Settings**
3. Go to **Secrets** tab
4. Paste the TOML-formatted Firebase credentials
5. Click **Save** → Reboot app

---

### Issue 4: App Shows Blank Page or Spinner

**Cause:** Python version mismatch or dependency conflict.

**Solution:**
- Add `runtime.txt` to repo root with: `python-3.11`
- Pin exact versions in requirements.txt if needed
- Check Streamlit Cloud logs: App Settings → Logs

---

### Issue 5: Dark Theme Not Applying

**Cause:** `.streamlit/config.toml` missing or wrong format.

**Solution:**
Ensure the file exists at `.streamlit/config.toml` with correct syntax:
```toml
[theme]
primaryColor = "#6366f1"
backgroundColor = "#090d16"
secondaryBackgroundColor = "#111827"
textColor = "#e5e7eb"
```

---

### Issue 6: CSS Styles Not Loading

**Cause:** `css/style.css` path incorrect or file missing.

**Solution:**
- Verify `css/style.css` exists in the repository
- Check that `app.py` reads the CSS with the correct relative path
- Ensure the CSS file is committed to Git

---

### Issue 7: Google Sheets Logging Fails

**Cause:** Google Sheets API not enabled or credentials insufficient.

**Solution:**
1. Go to Google Cloud Console → APIs & Services
2. Enable **Google Sheets API**
3. Ensure the Firebase service account has access to the target spreadsheet
4. Share the Google Sheet with the service account email

---

### Issue 8: Firestore `PERMISSION_DENIED`

**Cause:** Service account doesn't have Firestore permissions.

**Solution:**
1. Go to Google Cloud Console → IAM & Admin
2. Find your service account
3. Ensure it has the **Cloud Datastore User** or **Firebase Admin** role
4. Or use the Firebase Admin SDK which bypasses rules

---

### Issue 9: `git push` Rejected to GitHub

**Cause:** Branch protection or authentication issues.

**Solution:**
```bash
# Force push (⚠️ use carefully)
git push --force origin main

# Or create a new branch and merge via PR
git checkout -b fix/update
git push origin fix/update
# Then create a Pull Request on GitHub
```

---

### Issue 10: App Crashes with `RecursionError`

**Cause:** Streamlit's re-execution model causing infinite loops.

**Solution:**
- Check for circular widget callbacks
- Ensure Shadow Keys pattern is implemented correctly
- Add early return guards: `if 'key' not in st.session_state: return`

---

### Issue 11: Streamlit Cloud Build Timeout

**Cause:** Large dependencies or network issues during build.

**Solution:**
- Minimize dependencies in `requirements.txt`
- Pin exact versions to avoid resolution time
- Remove unnecessary packages
- Retry the deployment (transient network issues)

---

### Issue 12: Charts Not Rendering in Dashboard

**Cause:** No data in Firestore or Plotly version issue.

**Solution:**
- Check if `evaluations` collection has documents in Firestore
- Verify Plotly version: `pip show plotly`
- Dashboard falls back to mock data when Firebase is disconnected — check the connection indicator

---

## 9. Updating and Redeploying

### Streamlit Cloud (Automatic)

Streamlit Cloud automatically redeploys when you push to the configured branch:

```bash
# Make your changes
git add .
git commit -m "feat: add new feature"
git push origin main
# → Streamlit Cloud auto-redeploys within 1-2 minutes
```

### Manual Reboot (Streamlit Cloud)

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Find your app
3. Click **⋮** → **Reboot app**

### Updating Dependencies

```bash
# Update requirements.txt with new versions
pip install --upgrade streamlit firebase-admin pandas plotly

# Freeze current versions
pip freeze > requirements.txt

# Or manually update version pins in requirements.txt
```

### Rollback

```bash
# View recent commits
git log --oneline -10

# Revert to a specific commit
git revert <commit-hash>
git push origin main
# → Streamlit Cloud auto-redeploys with reverted changes
```

### การอัปเดตและ Redeploy ภาษาไทย

> **วิธีอัปเดตแอป:**
> 1. แก้ไขโค้ดตามต้องการ
> 2. `git add .` → `git commit -m "ข้อความอธิบาย"` → `git push origin main`
> 3. Streamlit Cloud จะ Deploy ใหม่อัตโนมัติภายใน 1-2 นาที
> 4. หากต้องการ Rollback: ใช้ `git revert <commit-hash>` แล้ว push ใหม่

---

## 10. Security Best Practices

### Credential Management

| Practice | Description |
|----------|-------------|
| ✅ Use `st.secrets` | Never hardcode credentials in source code |
| ✅ Add to `.gitignore` | Prevent accidental commits of secret files |
| ✅ Rotate keys periodically | Generate new service account keys quarterly |
| ✅ Limit permissions | Use minimum required IAM roles |
| ❌ Never commit JSON keys | Service account keys must never be in Git history |
| ❌ Never share keys publicly | Treat service account keys like passwords |

### If Credentials Are Compromised

1. **Immediately** revoke the compromised key in Google Cloud Console
2. Generate a new service account key
3. Update Streamlit Cloud secrets with the new key
4. Update local `.streamlit/secrets.toml`
5. Review Firestore for unauthorized access
6. If committed to Git, use `git filter-branch` or BFG Repo-Cleaner to remove from history

### Firestore Security

- Keep Firestore rules restrictive (deny all client access)
- Use Admin SDK for all server-side operations
- Enable Firestore audit logging in Google Cloud

---

## 11. Monitoring and Maintenance

### Streamlit Cloud Monitoring

| What to Monitor | How |
|----------------|-----|
| App status | Streamlit Cloud dashboard |
| Error logs | App Settings → Logs |
| Memory usage | Streamlit Cloud metrics |
| Deployment status | Streamlit Cloud dashboard |

### Firebase Monitoring

| What to Monitor | How |
|----------------|-----|
| Firestore reads/writes | Firebase Console → Usage |
| Storage usage | Firebase Console → Firestore → Usage |
| Error rates | Google Cloud Console → Error Reporting |
| Billing | Google Cloud Console → Billing |

### Regular Maintenance Tasks

| Task | Frequency | Description |
|------|-----------|-------------|
| Update dependencies | Monthly | Check for security patches |
| Rotate credentials | Quarterly | Generate new service account keys |
| Review Firestore data | Monthly | Check for orphaned drafts |
| Check Streamlit Cloud logs | Weekly | Monitor for errors |
| Backup Firestore | Monthly | Export data for disaster recovery |
| Update documentation | As needed | Keep docs in sync with code changes |

### Firestore Backup

```bash
# Export Firestore data (requires gcloud CLI)
gcloud firestore export gs://your-backup-bucket/$(date +%Y%m%d)

# Import Firestore data
gcloud firestore import gs://your-backup-bucket/20260520
```

### Health Check Checklist

- [ ] App loads successfully at production URL
- [ ] Firebase connection shows "Connected"
- [ ] Login works with all organization options
- [ ] Checklist unlocks calculator correctly
- [ ] Calculator saves and loads drafts
- [ ] Evaluation submission succeeds
- [ ] Dashboard displays real data
- [ ] Dark theme renders correctly
- [ ] No console errors in browser

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│           QUICK DEPLOYMENT REFERENCE            │
├─────────────────────────────────────────────────┤
│                                                 │
│  LOCAL DEV:                                     │
│    git clone <repo>                             │
│    python -m venv venv                          │
│    venv\Scripts\activate                        │
│    pip install -r requirements.txt              │
│    streamlit run app.py                         │
│                                                 │
│  CLOUD DEPLOY:                                  │
│    1. Push to GitHub main branch                │
│    2. Connect repo on share.streamlit.io        │
│    3. Add Firebase secrets (TOML format)        │
│    4. Deploy!                                   │
│                                                 │
│  UPDATE:                                        │
│    git add . && git commit && git push          │
│    → Auto-redeploy on Streamlit Cloud           │
│                                                 │
│  URLS:                                          │
│    GitHub: github.com/Joopiest/ImpactCalculator │
│    GitLab: git.nstda.or.th/NECTEC-Roks/...     │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

> **Document Version:** 1.0  
> **Last Updated:** May 2026  
> **Maintained by:** NSTDA / NECTEC Development Team
