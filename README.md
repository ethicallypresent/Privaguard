# PrivaGuard - Personal Data Removal & Protection Tool

A simple, local-first Streamlit app that helps you track where your personal data is exposed, generate professional removal requests, and optionally send them via email.

Everything runs on your own device. No cloud. No accounts. No data leaves your computer or phone.

## Features

- Track data exposures (data brokers, people search sites, etc.)
- Update status of each exposure (Active, Removed, In Progress, Monitoring)
- Generate ready-to-use removal request templates (Florida FDBR, CCPA, GDPR, etc.)
- Send removal requests directly via email from the app
- Simple ongoing protection habit checklist
- Full local data control with one-click reset
- Clean, mobile-friendly interface

## Quick Start

### 1. Install Python (if needed)
Download from: https://www.python.org/downloads/

### 2. Clone or Download

### 3. Set up and run
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run privaguard.py

Email Sending (Optional)
To send requests directly from the app:
1.  Open the app → Sidebar → Email Configuration
2.  For Gmail users:
	•  Turn on 2-Step Verification
	•  Create an App Password (Google Account → Security → App passwords)
	•  Use smtp.gmail.com and port 587
3.  Enter your email + App Password and save
Your credentials are stored only locally on your device.
How to Use
1.  Exposures tab → Add sources where your data appears
2.  Requests tab → Select an exposure → Generate template → Send via email (or copy manually)
3.  Protection tab → Check off privacy habits
4.  Dashboard → See your progress at a glance
5.  Settings tab → Reset all data if needed
Important Notes
•  This is a personal tool for your own use.
•  Data removal is best-effort. Some brokers may re-add data later.
•  Always review and customize the generated templates with your real information.
•  The app does not automatically verify deletion.






