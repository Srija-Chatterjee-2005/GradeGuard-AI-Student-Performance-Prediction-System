import streamlit as st

def load_premium_css():
    st.markdown("""
    <style>

    /* ===== BACKGROUND ===== */
    .stApp {
        background:
        radial-gradient(circle at 20% 20%, rgba(34,211,238,0.15), transparent 30%),
        radial-gradient(circle at 80% 80%, rgba(139,92,246,0.18), transparent 30%),
        linear-gradient(135deg, #020617, #0f172a, #1e1b4b);
        background-attachment: fixed;
        color: white;
    }

    .block-container {
        padding-top: 1.5rem;
    }

    /* ===== HERO ===== */
    .hero {
        padding: 55px;
        border-radius: 35px;
        background: linear-gradient(135deg, #020617, #1e1b4b, #312e81);
        box-shadow: 0 40px 140px rgba(0,0,0,0.7);
        position: relative;
        overflow: hidden;
    }

    .hero::after {
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(120deg, transparent, rgba(255,255,255,0.1), transparent);
        animation: shimmer 5s infinite;
    }

    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }

    .hero h1 {
        font-size: 72px;
        font-weight: 900;
        background: linear-gradient(90deg, #22d3ee, #8b5cf6, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* ===== KPI CARDS ===== */
    .kpi-card {
        padding: 28px;
        border-radius: 28px;
        background:
        linear-gradient(135deg, rgba(34,211,238,0.18), rgba(139,92,246,0.18));
        border: 1px solid rgba(255,255,255,0.15);
        box-shadow: 0 25px 90px rgba(0,0,0,0.5);
        transition: 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .kpi-card::before {
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(120deg, transparent, rgba(255,255,255,0.12), transparent);
        transform: translateX(-100%);
        animation: shimmer 6s infinite;
    }

    .kpi-card:hover {
        transform: scale(1.05);
        box-shadow: 0 0 45px rgba(34,211,238,0.6);
    }

    .kpi-title {
        font-size: 14px;
        color: #cbd5e1;
    }

    .kpi-value {
        font-size: 40px;
        font-weight: 900;
    }

    /* ===== SECTION BOX ===== */
    .section-box {
        padding: 30px;
        border-radius: 30px;
        background: rgba(15,23,42,0.85);
        border: 1px solid rgba(34,211,238,0.25);
        box-shadow: 0 20px 70px rgba(0,0,0,0.5);
        margin-bottom: 25px;
    }

    /* ===== DIVIDER ===== */
    .premium-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #22d3ee, #8b5cf6, #ec4899, transparent);
        margin: 35px 0;
    }

    /* ===== BUTTON ===== */
    .stButton>button {
        background: linear-gradient(90deg, #22d3ee, #8b5cf6);
        border-radius: 12px;
        border: none;
        font-weight: bold;
        color: white;
        padding: 10px 20px;
    }

    .stButton>button:hover {
        box-shadow: 0 0 30px rgba(34,211,238,0.6);
    }

    /* ===== SIDEBAR ===== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #020617, #1e1b4b);
        border-right: 1px solid rgba(34,211,238,0.2);
    }

    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(#22d3ee, #8b5cf6);
        border-radius: 10px;
    }
                
    span[data-baseweb="tag"] {
        background: linear-gradient(90deg, #ec4899, #8b5cf6, #22d3ee) !important;
        color: white !important;
        border-radius: 12px !important;
        box-shadow: 0 0 14px rgba(236,72,153,0.45) !important;
    }

    .main-hero-v2 {
    padding: 58px 62px;
    border-radius: 38px;
    background:
        radial-gradient(circle at 12% 20%, rgba(250,204,21,0.32), transparent 22%),
        radial-gradient(circle at 88% 18%, rgba(236,72,153,0.35), transparent 24%),
        radial-gradient(circle at 50% 100%, rgba(34,211,238,0.28), transparent 30%),
        linear-gradient(135deg, #4c0519 0%, #831843 28%, #581c87 58%, #0f172a 100%);
        border: 1px solid rgba(255,255,255,0.20);
        box-shadow: 0 35px 120px rgba(236,72,153,0.32);
        margin-bottom: 28px;
    }

    .main-hero-v2 h1 {
        font-size: 78px;
        font-weight: 900;
        letter-spacing: -1.5px;
        margin: 8px 0;
        color: #ffffff;
        text-shadow:
            0 0 18px rgba(255,255,255,0.45),
            0 0 38px rgba(236,72,153,0.45);
    }

    .main-hero-v2 p {
        color: #fff7ed;
        font-size: 17px;
        font-weight: 600;
    }

    .hero-badge {
        display: inline-block;
        padding: 9px 18px;
        border-radius: 999px;
        background: rgba(255,255,255,0.16);
        border: 1px solid rgba(255,255,255,0.25);
        color: #fef3c7;
        font-weight: 800;
        margin-bottom: 10px;
    }
                
                
    </style>
    """, unsafe_allow_html=True)

def hero():
    st.markdown("""
    <div class="main-hero-v2">
        <div class="hero-badge">🎓 AI Academic Intelligence Platform</div>
        <h1>GradeGuard AI</h1>
        <p>Engineering Student Performance Prediction • Attendance Compliance • Guardian Approval • Intervention Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

def kpi_card(title, value):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

def insight_box(title, text):
    st.markdown(f"""
    <div class="insight-box">
        <b style="color:#67e8f9;">{title}</b><br>
        <span style="color:#cbd5e1;">{text}</span>
    </div>
    """, unsafe_allow_html=True)

def premium_divider():
    st.markdown('<div class="premium-divider"></div>', unsafe_allow_html=True)

def progress_bar(label, value):
    value = max(0, min(100, int(value)))
    st.markdown(f"""
    <div style="margin-bottom:12px;">
        <div style="color:#cbd5e1; margin-bottom:6px;">{label}: <b>{value}%</b></div>
        <div class="progress-shell">
            <div class="progress-fill" style="width:{value}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def page_header(title, subtitle, theme="rose"):
    themes = {
        "rose": "linear-gradient(135deg, #be185d, #7e22ce, #312e81)",
        "sunset": "linear-gradient(135deg, #f97316, #db2777, #7c3aed)",
        "mint": "linear-gradient(135deg, #059669, #06b6d4, #4f46e5)",
        "gold": "linear-gradient(135deg, #ca8a04, #c026d3, #4338ca)",
        "galaxy": "linear-gradient(135deg, #581c87, #be185d, #0f172a)",
        "ocean": "linear-gradient(135deg, #0891b2, #2563eb, #9333ea)",
        "emerald": "linear-gradient(135deg, #047857, #0f766e, #7c3aed)",
    }

    bg = themes.get(theme, themes["rose"])

    st.markdown(f"""
    <div style="
        padding:30px 34px;
        border-radius:30px;
        background:{bg};
        box-shadow:0 24px 85px rgba(236,72,153,0.25);
        border:1px solid rgba(255,255,255,0.20);
        margin-bottom:25px;
    ">
        <h2 style="font-size:36px; font-weight:900; margin-bottom:8px; color:white;">
            {title}
        </h2>
        <p style="font-size:16px; color:#fff7ed; font-weight:600;">
            {subtitle}
        </p>
    </div>
    """, unsafe_allow_html=True)


def chart_box_start(theme="violet"):
    gradients = {
        "violet": "linear-gradient(135deg, rgba(139,92,246,0.22), rgba(15,23,42,0.90))",
        "pink": "linear-gradient(135deg, rgba(236,72,153,0.22), rgba(15,23,42,0.90))",
        "cyan": "linear-gradient(135deg, rgba(34,211,238,0.22), rgba(15,23,42,0.90))",
        "gold": "linear-gradient(135deg, rgba(250,204,21,0.18), rgba(15,23,42,0.90))",
        "green": "linear-gradient(135deg, rgba(16,185,129,0.20), rgba(15,23,42,0.90))",
    }

    bg = gradients.get(theme, gradients["violet"])

    st.markdown(f"""
    <div style="
        padding:18px;
        border-radius:26px;
        background:{bg};
        border:1px solid rgba(255,255,255,0.12);
        box-shadow:0 18px 55px rgba(0,0,0,0.38);
        margin-bottom:20px;
    ">
    """, unsafe_allow_html=True)


def chart_box_end():
    st.markdown("</div>", unsafe_allow_html=True)