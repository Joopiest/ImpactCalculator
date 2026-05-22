<p align="center">
  <h1 align="center">🚀 Impact & Investment Evaluation System</h1>
  <p align="center">
    <strong>ระบบประเมินผลกระทบและการลงทุนจากงานวิจัย สวทช.</strong><br/>
    <em>Pre-Impact & Pre-Investment Calculator for NSTDA R&D Projects</em>
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit"/>
  <img src="https://img.shields.io/badge/Firebase-Firestore-FFCA28?style=for-the-badge&logo=firebase&logoColor=black" alt="Firebase"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License"/>
  <img src="https://img.shields.io/badge/Theme-Dark_Space-6366f1?style=for-the-badge" alt="Theme"/>
</p>

---

## 📋 Overview | ภาพรวม

**Impact & Investment Evaluation System** is a Streamlit web application built for **NSTDA (National Science and Technology Development Agency)** researchers to quantitatively assess the **Pre-Impact** and **Pre-Investment** values of R&D projects.

**ระบบประเมินผลกระทบและการลงทุน** เป็นแอปพลิเคชันเว็บสำหรับนักวิจัย **สวทช.** เพื่อประเมินมูลค่า **ผลกระทบก่อนเกิด (Pre-Impact)** และ **การลงทุนก่อนเกิด (Pre-Investment)** ของโครงการวิจัยและพัฒนา

---

## ✨ Features | คุณสมบัติ

| | Feature | Description |
|---|---------|-------------|
| 📋 | **Readiness Checklist** | 2-section validation (Basic Criteria + Project Characteristics) before calculation |
| 🧮 | **10-Category Calculator** | 7 Impact categories (B-G, K) + 3 Investment categories (H-J) with precise formulas |
| ☁️ | **Real-time Cloud Sync** | Auto-save, load, and delete drafts on Firebase Firestore instantly |
| ⚡ | **Smart State Management** | JavaScript click-traps for browser autofill and shadow keys to prevent data loss |
| 📊 | **Interactive Dashboard** | Plotly-powered analytics with pie charts, bar charts, timeline, and searchable tables |
| 🔐 | **Organization Login** | Session-based auth supporting NSTDA, NECTEC, BIOTEC, MTEC, NANOTEC, ENTEC, Guest |
| 🌙 | **Premium Dark Theme** | Space-themed UI with glassmorphism effects and smooth animations |
| 🇹🇭 | **Thai Language Support** | Full Thai UI with Google Fonts (Plus Jakarta Sans + Noto Sans Thai) |
| 📄 | **Google Sheets Backup** | Dual-write to Firestore + Google Sheets for data redundancy |
| 📖 | **Built-in Glossary** | Definitions page with expandable sections for every formula and coefficient |
| 🔄 | **Offline Fallback** | Dashboard shows mock data when Firebase is unavailable |

---

## 📸 Screenshots

<!-- 
Add screenshots here:
![Home Page](screenshots/home.png)
![Calculator](screenshots/calculator.png)
![Dashboard](screenshots/dashboard.png)
-->

> 📌 Screenshots coming soon. Run the app locally to preview the UI.

---

## 🚀 Quick Start | เริ่มต้นอย่างรวดเร็ว

### Prerequisites

- Python 3.9+
- Firebase project with Firestore enabled

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Joopiest/ImpactCalculator.git
cd ImpactCalculator

# 2. Create virtual environment
python -m venv venv

# 3. Activate (Windows)
venv\Scripts\activate
# Activate (macOS/Linux)
# source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Add Firebase credentials
# Place serviceAccountKey.json in the project root

# 6. Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501` 🎉

---

## 🛠️ Tech Stack | เทคโนโลยี

| Layer | Technology | Version |
|-------|-----------|---------|
| **Framework** | [Streamlit](https://streamlit.io) | ≥ 1.35.0 |
| **Database** | [Firebase Firestore](https://firebase.google.com/docs/firestore) | ≥ 6.5.0 |
| **Data Processing** | [Pandas](https://pandas.pydata.org) | ≥ 2.0.0 |
| **Visualization** | [Plotly](https://plotly.com/python) | ≥ 5.15.0 |
| **Fonts** | [Google Fonts](https://fonts.google.com) | Plus Jakarta Sans, Noto Sans Thai |
| **Hosting** | [Streamlit Cloud](https://share.streamlit.io) | — |

---

## 📁 Project Structure | โครงสร้างโปรเจกต์

```
ImpactCalculator/
├── 📄 app.py                   # Main entry point (auth gate, nav, CSS)
├── 📄 firebase_config.py       # Firebase Admin SDK + CRUD operations
├── 📄 requirements.txt         # Python dependencies
├── 📄 README.md                # This file
│
├── 📁 .streamlit/
│   └── config.toml             # Dark theme configuration
│
├── 📁 css/
│   └── style.css               # Premium dark space theme + glassmorphism
│
├── 📁 pages/
│   ├── home.py                 # Landing page with feature cards & live stats
│   ├── checklist.py            # 2-section readiness assessment
│   ├── calculator.py           # Main calculator (882 lines, 4 tabs)
│   ├── dashboard.py            # Analytics with Plotly charts
│   └── definitions.py          # Glossary & reference
│
└── 📁 docs/
    ├── USER_MANUAL.md          # User manual (Thai + English)
    ├── TECHNICAL_REPORT.md     # Technical architecture report
    └── DEPLOYMENT_GUIDE.md     # Deployment instructions
```

---

## 📚 Documentation | เอกสาร

| Document | Language | Description |
|----------|----------|-------------|
| 📘 [User Manual](docs/USER_MANUAL.md) | Thai + English | Complete user guide with step-by-step instructions |
| 📗 [Technical Report](docs/TECHNICAL_REPORT.md) | English | Architecture, formulas, database schema, deployment details |
| 📙 [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) | English + Thai | Local setup, Cloud deployment, Firebase configuration |

---

## 🧮 Calculation Categories | หมวดการคำนวณ

### Pre-Impact (ผลกระทบก่อนเกิด)

| Section | Category | Formula |
|---------|----------|---------|
| **B** | Import Substitution | (Foreign Price − NSTDA Price) × Spec Ratio × Qty × α × β |
| **C** | Revenue Enhancement | Net Profit Increase × α × β |
| **D** | Cost Reduction | Cost Savings × α × β |
| **E** | Efficiency | Salary/min × Time Saved × Frequency × α × β |
| **F** | Risk Mitigation | Damage Value × Probability × Severity × α × β |
| **G** | Skill Upgrade | Trainees × Course Value × α × β |
| **K** | Other Impact | Value × α × β |

### Pre-Investment (การลงทุนก่อนเกิด)

| Section | Category | Formula |
|---------|----------|---------|
| **H** | R&D Investment | Investment × α × β |
| **I** | Process Investment | Investment × α × β |
| **J** | Additional Hiring | Salary × Work Ratio × α × β |

> **α** = Activity Coefficient (1.0 / 0.6 / 0.3) · **β** = Contribution Ratio (0–1)

---

## 🤝 Contributing | การมีส่วนร่วม

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'feat: add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Commit Message Convention

```
feat:     New feature
fix:      Bug fix
docs:     Documentation changes
style:    Formatting, missing semicolons, etc.
refactor: Code restructuring
test:     Adding tests
chore:    Maintenance tasks
```

---

## 📄 License | สัญญาอนุญาต

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2026 NSTDA / NECTEC

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 👥 Team | ทีมพัฒนา

| Role | Organization |
|------|-------------|
| **Development** | NSTDA / NECTEC |
| **Research Methodology** | NSTDA Impact Assessment Division |

---

## 🙏 Acknowledgments | กิตติกรรมประกาศ

- **NSTDA** — for the impact evaluation framework and methodology
- **Streamlit** — for the powerful Python web app framework
- **Firebase** — for reliable cloud database services
- **Plotly** — for interactive data visualization
- All NSTDA researchers who provided feedback and testing

---

## 🔗 Links | ลิงก์

| Resource | URL |
|----------|-----|
| 🌐 **GitHub** | [github.com/Joopiest/ImpactCalculator](https://github.com/Joopiest/ImpactCalculator) |
| 🔒 **GitLab (Internal)** | [git.nstda.or.th/NECTEC-Roks/joopfirebase_gitlab](https://git.nstda.or.th/NECTEC-Roks/joopfirebase_gitlab) |
| 🏢 **NSTDA** | [nstda.or.th](https://www.nstda.or.th) |

---

<p align="center">
  Made with ❤️ by NSTDA / NECTEC
</p>
