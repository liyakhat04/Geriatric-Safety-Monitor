"""
Geriatric Safety Monitor - Streamlit Application

"""

import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import base64
import time
import random
import string
from datetime import datetime

# --- Page Config ---
st.set_page_config(
    page_title="Geriatric Safety Monitor",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- Custom CSS ---
st.markdown("""
<style>
    /* Global */
    body { background-color: #F8F9FA; font-family: 'Inter', sans-serif; }
    .stApp { background-color: #F8F9FA; }

    /* Header */
    .app-header {
        background: white;
        border-bottom: 1px solid #E5E7EB;
        padding: 1rem 1.5rem;
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 1.5rem;
        border-radius: 0 0 16px 16px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    .header-icon {
        background: #4F46E5;
        padding: 8px;
        border-radius: 10px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }
    .app-title { font-size: 1.3rem; font-weight: 700; letter-spacing: -0.5px; color: #1A1A1A; }

    /* Cards */
    .card {
        background: white;
        border-radius: 24px;
        border: 1px solid #E5E7EB;
        padding: 1.5rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    .card-title {
        font-weight: 700;
        font-size: 1rem;
        color: #1A1A1A;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Safety Score Card */
    .score-card {
        background: #4F46E5;
        border-radius: 24px;
        padding: 1.5rem;
        color: white;
        box-shadow: 0 8px 24px rgba(79,70,229,0.3);
        margin-bottom: 1rem;
    }
    .score-value { font-size: 2.5rem; font-weight: 900; margin: 4px 0; }
    .score-label { font-size: 0.7rem; opacity: 0.8; }

    /* Alert items */
    .alert-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 0.75rem;
        background: #F9FAFB;
        border-radius: 12px;
        border: 1px solid #F3F4F6;
        margin-bottom: 8px;
    }
    .alert-icon-fall { background: #FEE2E2; color: #DC2626; border-radius: 8px; padding: 6px; }
    .alert-icon-move { background: #DBEAFE; color: #2563EB; border-radius: 8px; padding: 6px; }
    .alert-name { font-size: 0.85rem; font-weight: 700; color: #1A1A1A; }
    .alert-time { font-size: 0.7rem; color: #6B7280; }
    .alert-badge {
        font-size: 0.6rem;
        font-weight: 700;
        padding: 3px 8px;
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 6px;
        color: #374151;
    }

    /* Alert history cards */
    .alert-card {
        background: white;
        border-radius: 20px;
        border: 1px solid #E5E7EB;
        overflow: hidden;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
        transition: box-shadow 0.2s;
        margin-bottom: 1rem;
    }
    .alert-card-body { padding: 1.25rem; }
    .fall-badge { background: #FEE2E2; color: #DC2626; border-radius: 20px; padding: 3px 10px; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; }
    .move-badge { background: #DBEAFE; color: #2563EB; border-radius: 20px; padding: 3px 10px; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; }
    .incident-id { font-weight: 700; font-size: 1rem; color: #1A1A1A; margin: 8px 0; }

    /* Live badge */
    .live-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(239,68,68,0.85);
        color: white;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.65rem;
        font-weight: 700;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.6} }
    .live-dot { width: 6px; height: 6px; background: white; border-radius: 50%; }

    /* Camera offline */
    .camera-offline {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: black;
        border-radius: 20px;
        height: 320px;
        color: white;
        opacity: 0.6;
    }
    .camera-icon { font-size: 3rem; margin-bottom: 12px; }

    /* Report box */
    .report-box {
        background: #F9FAFB;
        border: 1px solid #F3F4F6;
        border-radius: 16px;
        padding: 1.5rem;
        min-height: 400px;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        line-height: 1.7;
        white-space: pre-wrap;
        color: #374151;
    }

    /* Analyzing banner */
    .analyzing-banner {
        display: flex;
        align-items: center;
        gap: 10px;
        color: #4F46E5;
        font-weight: 600;
        margin-bottom: 1rem;
        animation: pulse 1.5s infinite;
    }

    /* Button overrides */
    div[data-testid="stButton"] > button {
        border-radius: 14px;
        font-weight: 700;
        border: none;
        transition: all 0.15s;
    }

    /* Tab bar */
    div[data-testid="stTabs"] [data-testid="stTab"] {
        font-weight: 600;
        border-radius: 10px;
    }

    /* Remove Streamlit default padding excess */
    .block-container { padding-top: 1.5rem; }

    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 5rem 1rem;
        background: white;
        border-radius: 24px;
        border: 2px dashed #E5E7EB;
        color: #9CA3AF;
    }
    .empty-icon { font-size: 3rem; margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

# --- Session State Init ---
if "alerts" not in st.session_state:
    st.session_state.alerts = []
if "report" not in st.session_state:
    st.session_state.report = ""
if "is_monitoring" not in st.session_state:
    st.session_state.is_monitoring = False
if "is_analyzing" not in st.session_state:
    st.session_state.is_analyzing = False
if "captured_image" not in st.session_state:
    st.session_state.captured_image = None

# --- Header ---
st.markdown("""
<div class="app-header">
    <div class="header-icon">⚡</div>
    <div class="app-title">Geriatric Safety Monitor</div>
</div>
""", unsafe_allow_html=True)

# --- Gemini API Setup ---
def get_gemini_client():
    api_key = st.session_state.get("gemini_api_key", "")
    if api_key:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel("gemini-1.5-flash")
    return None

def gen_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))

# --- AI Analysis ---
def analyze_with_gemini(alert_type: str, image: Image.Image | None):
    model = get_gemini_client()
    if not model:
        return "[API key not set] Unable to generate AI analysis. Please enter your Gemini API key in the sidebar."
    try:
        prompt = (
            f"Analyze this potential {alert_type} event for a geriatric safety monitor. "
            "Provide a brief safety assessment and next steps for the caregiver."
        )
        if image:
            response = model.generate_content([prompt, image])
        else:
            response = model.generate_content(
                prompt + " (Note: No camera image was available for this analysis.)"
            )
        return response.text
    except Exception as e:
        return f"[Analysis Error] {str(e)}"

# --- Sidebar: API Key ---
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    api_key = st.text_input("Gemini API Key", type="password", placeholder="Enter your Gemini API key")
    if api_key:
        st.session_state.gemini_api_key = api_key
        st.success("API key set ✓")
    else:
        st.info("Enter your Gemini API key to enable AI analysis.")
    st.markdown("---")
    st.markdown("**Stats**")
    st.metric("Total Alerts", len(st.session_state.alerts))
    falls = sum(1 for a in st.session_state.alerts if a["type"] == "Fall")
    st.metric("Fall Events", falls)
    st.metric("Safety Score", "98%")

# --- Tabs ---
tab_monitor, tab_alerts, tab_reports = st.tabs(["📷 Monitor", "🔔 Alerts", "📄 Reports"])

# ===========================
# MONITOR TAB
# ===========================
with tab_monitor:
    col_main, col_side = st.columns([2, 1], gap="large")

    with col_main:
        # Camera / Image Area
        if st.session_state.is_monitoring:
            st.markdown('<div class="live-badge"><div class="live-dot"></div> LIVE MONITORING</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            # Capture widget
            img_file = st.camera_input("Live Camera Feed", label_visibility="collapsed")
            if img_file:
                img = Image.open(img_file)
                st.session_state.captured_image = img
        else:
            st.markdown("""
            <div class="camera-offline">
                <div class="camera-icon">📷</div>
                <p style="font-size:1rem; font-weight:500;">Camera Offline</p>
            </div>
            """, unsafe_allow_html=True)

        # Control Buttons
        st.markdown("<br>", unsafe_allow_html=True)
        btn_col1, btn_col2 = st.columns([2, 1])
        with btn_col1:
            label = "🛑 Stop Monitoring" if st.session_state.is_monitoring else "▶️ Start Monitoring"
            color = "secondary" if st.session_state.is_monitoring else "primary"
            if st.button(label, use_container_width=True, type=color):
                st.session_state.is_monitoring = not st.session_state.is_monitoring
                if not st.session_state.is_monitoring:
                    st.session_state.captured_image = None
                st.rerun()

        with btn_col2:
            sim_disabled = not st.session_state.is_monitoring
            if st.button("🚨 Simulate Fall", use_container_width=True, disabled=sim_disabled, type="primary"):
                # Create alert
                alert_id = gen_id()
                alert_time = datetime.now().strftime("%I:%M:%S %p")
                img = st.session_state.captured_image

                # Convert image to base64 for display storage
                img_b64 = None
                if img:
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG")
                    img_b64 = base64.b64encode(buf.getvalue()).decode()

                new_alert = {
                    "id": alert_id,
                    "time": alert_time,
                    "type": "Fall",
                    "status": "Active",
                    "image_b64": img_b64,
                    "image_pil": img,
                }
                st.session_state.alerts.insert(0, new_alert)

                # AI Analysis
                with st.spinner("🤖 Generating AI Analysis..."):
                    ai_text = analyze_with_gemini("Fall", img)

                st.session_state.report = (
                    f"[{alert_time}] Fall Detected:\n{ai_text}\n\n"
                    + st.session_state.report
                )
                st.success("⚠️ Fall alert triggered and logged!")
                st.rerun()

    with col_side:
        # Recent Activity Card
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🔔 Recent Activity</div>', unsafe_allow_html=True)

        recent = st.session_state.alerts[:5]
        if recent:
            for a in recent:
                icon = "🔴" if a["type"] == "Fall" else "🔵"
                st.markdown(f"""
                <div class="alert-item">
                    <span style="font-size:1.2rem">{icon}</span>
                    <div style="flex:1">
                        <div class="alert-name">{a["type"]} Detected</div>
                        <div class="alert-time">{a["time"]}</div>
                    </div>
                    <div class="alert-badge">{a["status"]}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<p style="color:#9CA3AF; text-align:center; font-style:italic; padding:2rem 0; font-size:0.85rem;">No activity detected</p>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Safety Score Card
        st.markdown("""
        <div class="score-card">
            <div style="font-weight:700; font-size:1rem;">Safety Score</div>
            <div class="score-value">98%</div>
            <div class="score-label">All systems operational. Environment is currently safe.</div>
        </div>
        """, unsafe_allow_html=True)

# ===========================
# ALERTS TAB
# ===========================
with tab_alerts:
    st.markdown("## Alert History")

    if not st.session_state.alerts:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">🔔</div>
            <p>No alerts recorded yet.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        cols = st.columns(3)
        for idx, a in enumerate(st.session_state.alerts):
            with cols[idx % 3]:
                badge_class = "fall-badge" if a["type"] == "Fall" else "move-badge"
                badge_html = f'<span class="{badge_class}">{a["type"]}</span>'

                st.markdown(f"""
                <div class="alert-card">
                """, unsafe_allow_html=True)

                # Show image if captured
                if a.get("image_b64"):
                    st.markdown(
                        f'<img src="data:image/jpeg;base64,{a["image_b64"]}" '
                        f'style="width:100%; height:180px; object-fit:cover;" alt="Alert Capture"/>',
                        unsafe_allow_html=True
                    )

                st.markdown(f"""
                <div class="alert-card-body">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        {badge_html}
                        <span style="font-size:0.7rem; color:#9CA3AF;">{a["time"]}</span>
                    </div>
                    <div class="incident-id">Incident #{a["id"].upper()}</div>
                </div>
                """, unsafe_allow_html=True)

                resolve_col1, resolve_col2 = st.columns(2)
                with resolve_col1:
                    st.button("View Details", key=f"view_{a['id']}", use_container_width=True)
                with resolve_col2:
                    if st.button("Resolve", key=f"res_{a['id']}", use_container_width=True, type="primary"):
                        for alert in st.session_state.alerts:
                            if alert["id"] == a["id"]:
                                alert["status"] = "Resolved"
                        st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

# ===========================
# REPORTS TAB
# ===========================
with tab_reports:
    rep_col1, rep_col2 = st.columns([3, 1])
    with rep_col1:
        st.markdown("## 📄 AI Safety Report")
    with rep_col2:
        if st.session_state.report:
            report_bytes = st.session_state.report.encode()
            st.download_button(
                "📥 Export Report",
                data=report_bytes,
                file_name=f"safety_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True,
            )

    if st.session_state.is_analyzing:
        st.markdown("""
        <div class="analyzing-banner">
            ⚡ Generating AI Analysis...
        </div>
        """, unsafe_allow_html=True)

    report_text = st.session_state.report or (
        "No safety events recorded. The environment is currently stable "
        "and no incidents have been flagged for analysis."
    )
    st.markdown(f'<div class="report-box">{report_text}</div>', unsafe_allow_html=True)
