#!/usr/bin/env python3
"""
PrivaGuard - Personal Data Removal & Protection Tool
Single-file Streamlit app. Everything stays local on your device.
"""

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

DB_FILE = "privaguard.db"

# ============================================================
# DATABASE SETUP
# ============================================================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS exposures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT NOT NULL,
        data_types TEXT,
        risk_level TEXT,
        status TEXT DEFAULT 'Active',
        notes TEXT,
        created_at TEXT
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS removal_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exposure_id INTEGER,
        jurisdiction TEXT,
        request_text TEXT,
        status TEXT DEFAULT 'Draft',
        sent_date TEXT,
        response_notes TEXT
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS email_config (
        id INTEGER PRIMARY KEY,
        smtp_server TEXT,
        smtp_port INTEGER,
        email TEXT,
        password TEXT
    )''')
    
    conn.commit()
    conn.close()

init_db()

# ============================================================
# EMAIL HELPER FUNCTIONS
# ============================================================
def get_email_config():
    conn = sqlite3.connect(DB_FILE)
    row = conn.execute("SELECT * FROM email_config WHERE id=1").fetchone()
    conn.close()
    if row:
        return {
            "smtp_server": row[1],
            "smtp_port": row[2],
            "email": row[3],
            "password": row[4]
        }
    return None

def save_email_config(smtp_server, smtp_port, email, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM email_config")
    c.execute("""INSERT INTO email_config (id, smtp_server, smtp_port, email, password)
                 VALUES (1, ?, ?, ?, ?)""", (smtp_server, smtp_port, email, password))
    conn.commit()
    conn.close()

def send_email_via_smtp(to_email, subject, body, config):
    try:
        msg = MIMEMultipart()
        msg['From'] = config['email']
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
        server.starttls()
        server.login(config['email'], config['password'])
        server.sendmail(config['email'], to_email, msg.as_string())
        server.quit()
        return True, "✅ Email sent successfully!"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

# ============================================================
# STREAMLIT UI
# ============================================================
st.set_page_config(page_title="PrivaGuard • Personal", page_icon="🛡️", layout="centered")

st.title("🛡️ PrivaGuard")
st.caption("Personal data removal & protection tool • Everything stays on your device")

# Sidebar - Email Configuration
with st.sidebar:
    st.header("📧 Email Configuration")
    config = get_email_config()
    
    if config:
        st.success(f"Configured: {config['email']}")
    else:
        st.warning("No email configured yet")
    
    with st.expander("Setup / Update Email"):
        with st.form("email_form"):
            smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com")
            smtp_port = st.number_input("SMTP Port", value=587)
            user_email = st.text_input("Your Email Address")
            user_password = st.text_input("Password or App Password", type="password")
            
            if st.form_submit_button("Save Configuration"):
                if user_email and user_password:
                    save_email_config(smtp_server, smtp_port, user_email, user_password)
                    st.success("Email configuration saved!")
                    st.rerun()
                else:
                    st.error("Please enter email and password.")

# ============================================================
# MAIN TABS
# ============================================================
tab_dashboard, tab_exposures, tab_requests, tab_protection, tab_settings = st.tabs([
    "Dashboard", "Exposures", "Requests", "Protection", "Settings"
])

# ============================================================
# TAB 1: DASHBOARD
# ============================================================
with tab_dashboard:
    st.header("Your Privacy Dashboard")
    
    conn = sqlite3.connect(DB_FILE)
    exp_df = pd.read_sql("SELECT * FROM exposures", conn)
    req_df = pd.read_sql("SELECT * FROM removal_requests", conn)
    conn.close()
    
    col1, col2, col3 = st.columns(3)
    active_count = len(exp_df[exp_df['status'] == 'Active']) if not exp_df.empty else 0
    in_progress = len(req_df[req_df['status'].isin(['Draft', 'Sent'])]) if not req_df.empty else 0
    
    col1.metric("Active Exposures", active_count)
    col2.metric("Requests In Progress", in_progress)
    col3.metric("Total Requests Created", len(req_df) if not req_df.empty else 0)
    
    st.divider()
    st.subheader("Quick Start")
    st.write("1. Add exposures in the **Exposures** tab")
    st.write("2. Generate & send requests in the **Requests** tab")
    st.write("3. Track habits in the **Protection** tab")

# ============================================================
# TAB 2: EXPOSURES
# ============================================================
with tab_exposures:
    st.header("📍 Track Your Data Exposures")
    
    with st.form("add_exposure", clear_on_submit=True):
        source = st.text_input("Source / Website / Broker", placeholder="e.g. Spokeo, BeenVerified")
        data_types = st.text_input("Data Exposed", placeholder="Name, address, phone, relatives...")
        risk = st.select_slider("Risk Level", options=["Low", "Medium", "High"], value="Medium")
        notes = st.text_area("Notes (optional)")
        
        if st.form_submit_button("Add Exposure"):
            if source.strip():
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute("""INSERT INTO exposures (source, data_types, risk_level, notes, created_at)
                             VALUES (?, ?, ?, ?, ?)""",
                          (source.strip(), data_types, risk, notes, datetime.now().isoformat()))
                conn.commit()
                conn.close()
                st.success(f"Added: {source}")
                st.rerun()
    
    st.divider()
    st.subheader("Your Current Exposures")
    
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT id, source, data_types, risk_level, status, notes FROM exposures ORDER BY created_at DESC", conn)
    conn.close()
    
    if not df.empty:
        for _, row in df.iterrows():
            with st.container(border=True):
                cols = st.columns([4, 1.5, 1])
                cols[0].markdown(f"**{row['source']}**")
                if row['data_types']:
                    cols[0].caption(row['data_types'])
                
                status_options = ["Active", "Removed", "In Progress", "Monitoring"]
                current_index = status_options.index(row['status']) if row['status'] in status_options else 0
                new_status = cols[1].selectbox("Status", status_options, index=current_index, key=f"status_{row['id']}")
                
                if new_status != row['status']:
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    c.execute("UPDATE exposures SET status = ? WHERE id = ?", (new_status, row['id']))
                    conn.commit()
                    conn.close()
                    st.rerun()
                
                if cols[2].button("🗑️ Delete", key=f"del_{row['id']}"):
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    c.execute("DELETE FROM exposures WHERE id = ?", (row['id'],))
                    conn.commit()
                    conn.close()
                    st.rerun()
    else:
        st.info("No exposures added yet.")

# ============================================================
# TAB 3: REQUESTS (Generate + Send Email)
# ============================================================
with tab_requests:
    st.header("✉️ Generate & Send Removal Requests")
    
    conn = sqlite3.connect(DB_FILE)
    exposures = pd.read_sql("SELECT id, source FROM exposures WHERE status != 'Removed'", conn)
    conn.close()
    
    if exposures.empty:
        st.warning("Add some exposures first in the Exposures tab.")
    else:
        selected = st.selectbox("Select Exposure", exposures['source'].tolist())
        jurisdiction = st.selectbox("Jurisdiction", 
            ["Florida Digital Bill of Rights (FDBR)", "California CCPA", "General US State Law", "GDPR-style"])
        
        if st.button("Generate Request Template"):
            template = f"""Subject: Request for Deletion of My Personal Information

Dear Privacy Team,

I request deletion of my personal information under {jurisdiction}.

My details:
- Full Name: [Your Full Legal Name]
- Email: [Your Email]
- Other identifiers: [Add phones, addresses, relatives if needed]

This applies to records from: {selected}

Please delete all my data and confirm in writing.

Thank you,
[Your Full Name]
[Your Email]
Date: {datetime.now().strftime('%Y-%m-%d')}"""

            st.text_area("Copy and customize this template:", template, height=280)
            
            st.divider()
            st.subheader("Send via Email (Optional)")
            recipient = st.text_input("Recipient Email (leave blank to send to yourself)", 
                                      value=get_email_config()['email'] if get_email_config() else "")
            
            if st.button("📤 Send Email Now"):
                config = get_email_config()
                if not config:
                    st.error("Please configure your email in the sidebar first.")
                else:
                    to_addr = recipient if recipient.strip() else config['email']
                    success, msg = send_email_via_smtp(to_addr, "Request for Deletion of My Personal Information", template, config)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)

# ============================================================
# TAB 4: PROTECTION
# ============================================================
with tab_protection:
    st.header("🛡️ Ongoing Protection Habits")
    st.write("Check off habits as you go.")
    
    habits = [
        "Use DuckDuckGo Email Protection for free aliases (@duck.com)",
        "Use DuckDuckGo Private Browser or Brave with tracker blocking",
        "Enable 2FA / Passkeys on important accounts",
        "Review and limit app permissions on your phone",
        "Use a reputable VPN on public Wi-Fi",
        "Limit personal information shared publicly online",
        "Regularly search your name + location and request new removals"
    ]
    
    for i, habit in enumerate(habits):
        st.checkbox(habit, key=f"habit_{i}")

# ============================================================
# TAB 5: SETTINGS
# ============================================================
with tab_settings:
    st.header("⚙️ Settings & Data Control")
    
    st.subheader("Local Data Storage")
    st.write("All data is stored locally in `privaguard.db` on your device only.")
    
    if st.button("🗑️ Delete ALL Data (Full Reset)", type="secondary"):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        init_db()
        st.success("All data deleted. Fresh start ready.")
        st.rerun()
    
    st.divider()
    st.subheader("Email Configuration")
    if st.button("Clear Email Configuration"):
        conn = sqlite3.connect(DB_FILE)
        conn.execute("DELETE FROM email_config")
        conn.commit()
        conn.close()
        st.success("Email configuration cleared.")
        st.rerun()

st.divider()
st.caption("PrivaGuard Personal • Built for you • June 2026")
