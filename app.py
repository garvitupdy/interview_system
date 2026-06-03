import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from graph import app

st.set_page_config(
    page_title="FORGE - Interview Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,700&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,700;1,9..40,400&family=DM+Mono:wght@400;500&display=swap');

    /* ─── Global Reset ─── */
    html, body, [data-testid="stAppViewContainer"] {
        background: #0a0e27 !important;
    }
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(ellipse at 20% 50%, #1a1f3a 0%, #0a0e27 50%, #050812 100%) !important;
    }
    [data-testid="stHeader"] { background: transparent !important; }
    
    * { box-sizing: border-box; }

    /* ─── Typography ─── */
    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        font-weight: 700 !important;
    }
    p, span, div, label, button {
        font-family: 'DM Sans', sans-serif !important;
    }

    /* ─── Noise Overlay ─── */
    [data-testid="stAppViewContainer"]::before {
        content: '';
        position: fixed;
        inset: 0;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
        pointer-events: none;
        z-index: 0;
        opacity: 0.5;
    }

    /* ─── Hero Section ─── */
    .forge-hero {
        text-align: center;
        padding: 50px 20px 30px;
        position: relative;
        z-index: 1;
    }
    .forge-hero .eyebrow {
        font-family: 'DM Mono', monospace;
        font-size: 11px;
        letter-spacing: 4px;
        text-transform: uppercase;
        color: #00d4ff;
        margin-bottom: 16px;
        display: block;
        animation: fadeInDown 0.8s ease;
    }
    .forge-hero h1 {
        font-family: 'Playfair Display', serif !important;
        font-size: clamp(48px, 8vw, 72px);
        font-weight: 900;
        margin: 0 0 12px;
        background: linear-gradient(135deg, #00d4ff 0%, #0099ff 50%, #00ff88 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: fadeInUp 0.8s ease 0.1s both;
        letter-spacing: -1px;
    }
    .forge-hero .tagline {
        font-family: 'DM Sans', sans-serif;
        font-size: 15px;
        font-weight: 300;
        color: #8a92b3;
        letter-spacing: 0.5px;
        max-width: 500px;
        margin: 0 auto;
        animation: fadeInUp 0.8s ease 0.2s both;
    }

    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* ─── Glow Divider ─── */
    .glow-divider {
        width: 100%;
        height: 1px;
        background: linear-gradient(90deg, transparent, #00d4ff44, #00d4ff99, #00d4ff44, transparent);
        margin: 28px 0;
        position: relative;
    }

    /* ─── Sidebar ─── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1325 0%, #0a0e27 100%) !important;
        border-right: 1px solid rgba(0, 212, 255, 0.15) !important;
    }

    .sidebar-title {
        font-family: 'Playfair Display', serif !important;
        font-size: 18px !important;
        color: #00d4ff !important;
        margin-bottom: 20px !important;
        font-weight: 700 !important;
    }

    /* ─── Metrics Cards ─── */
    .metric-card {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.05) 0%, rgba(0, 153, 255, 0.03) 100%);
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 12px;
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.5), transparent);
    }

    .metric-label {
        font-family: 'DM Mono', monospace;
        font-size: 10px;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #6b7d99;
        margin-bottom: 6px;
    }
    .metric-value {
        font-family: 'Playfair Display', serif;
        font-size: 24px;
        font-weight: 700;
        color: #00d4ff;
        margin: 0;
    }

    /* ─── Status Indicator ─── */
    .status-ongoing {
        background: rgba(0, 255, 136, 0.1) !important;
        border: 1px solid rgba(0, 255, 136, 0.3) !important;
        color: #00ff88 !important;
    }
    .status-passed {
        background: rgba(0, 255, 136, 0.15) !important;
        border: 1px solid rgba(0, 255, 136, 0.4) !important;
        color: #00ff88 !important;
    }
    .status-rejected {
        background: rgba(255, 68, 68, 0.1) !important;
        border: 1px solid rgba(255, 68, 68, 0.3) !important;
        color: #ff4444 !important;
    }

    /* ─── Role Selection Cards ─── */
    .role-selection {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin: 28px 0;
    }
    .role-card {
        background: linear-gradient(145deg, rgba(19, 30, 58, 0.8) 0%, rgba(10, 14, 39, 0.6) 100%);
        border: 1.5px solid rgba(0, 212, 255, 0.2);
        border-radius: 14px;
        padding: 24px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .role-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(0, 212, 255, 0.1) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .role-card:hover {
        border-color: rgba(0, 212, 255, 0.6);
        background: linear-gradient(145deg, rgba(19, 30, 58, 1) 0%, rgba(10, 14, 39, 0.8) 100%);
        box-shadow: 0 0 24px rgba(0, 212, 255, 0.2);
        transform: translateY(-4px);
    }
    .role-card:hover::before {
        opacity: 1;
    }
    .role-icon {
        font-size: 32px;
        margin-bottom: 12px;
        display: block;
    }
    .role-title {
        font-family: 'Playfair Display', serif;
        font-size: 16px;
        font-weight: 700;
        color: #c9d1d9;
        margin: 0;
    }

    /* ─── Buttons ─── */
    [data-testid="stButton"] button {
        border-radius: 10px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
        font-size: 13px !important;
        letter-spacing: 0.5px !important;
        padding: 11px 24px !important;
        transition: all 0.25s ease !important;
        border: none !important;
        position: relative !important;
        overflow: hidden !important;
    }
    [data-testid="stButton"] button[kind="primary"] {
        background: linear-gradient(135deg, #00d4ff, #0099ff) !important;
        color: #0a0e27 !important;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.4) !important;
        font-weight: 600 !important;
    }
    [data-testid="stButton"] button[kind="primary"]:hover {
        box-shadow: 0 0 32px rgba(0, 212, 255, 0.6) !important;
        transform: translateY(-2px) !important;
    }
    [data-testid="stButton"] button[kind="secondary"] {
        background: rgba(255, 68, 68, 0.15) !important;
        color: #ff6b6b !important;
        border: 1px solid rgba(255, 68, 68, 0.3) !important;
    }
    [data-testid="stButton"] button[kind="secondary"]:hover {
        background: rgba(255, 68, 68, 0.25) !important;
        border-color: rgba(255, 68, 68, 0.6) !important;
        box-shadow: 0 0 16px rgba(255, 68, 68, 0.3) !important;
    }

    /* ─── Progress Bar ─── */
    [data-testid="stProgress"] > div > div > div {
        background: linear-gradient(90deg, #00d4ff, #0099ff, #00ff88) !important;
        box-shadow: 0 0 16px rgba(0, 212, 255, 0.5) !important;
    }

    /* ─── Chat Messages ─── */
    [data-testid="stChatMessage"] {
        position: relative;
        margin-bottom: 16px;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: linear-gradient(135deg, rgba(0, 153, 255, 0.12) 0%, rgba(0, 212, 255, 0.05) 100%);
        border: 1px solid rgba(0, 212, 255, 0.25);
        border-radius: 14px;
        padding: 16px;
        animation: slideInLeft 0.4s ease;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background: linear-gradient(135deg, rgba(0, 255, 136, 0.08) 0%, rgba(0, 212, 255, 0.05) 100%);
        border: 1px solid rgba(0, 255, 136, 0.25);
        border-radius: 14px;
        padding: 16px;
        animation: slideInRight 0.4s ease;
    }

    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-16px); }
        to { opacity: 1; transform: translateX(0); }
    }
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(16px); }
        to { opacity: 1; transform: translateX(0); }
    }

    [data-testid="chatAvatarIcon-user"] {
        background: linear-gradient(135deg, #0099ff, #00d4ff) !important;
    }
    [data-testid="chatAvatarIcon-assistant"] {
        background: linear-gradient(135deg, #00ff88, #00d4ff) !important;
    }

    /* ─── Chat Input ─── */
    [data-testid="stChatInput"] {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.05) 0%, rgba(0, 153, 255, 0.03) 100%) !important;
        border: 1.5px solid rgba(0, 212, 255, 0.25) !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: rgba(0, 212, 255, 0.6) !important;
        box-shadow: 0 0 16px rgba(0, 212, 255, 0.2) !important;
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.08) 0%, rgba(0, 153, 255, 0.05) 100%) !important;
    }
    [data-testid="stChatInput"] textarea {
        color: #c9d1d9 !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: #4b5563 !important;
    }

    /* ─── Spinners ─── */
    [data-testid="stSpinner"] {
        color: #00d4ff !important;
    }

    /* ─── Score Display ─── */
    .score-container {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.08) 0%, rgba(0, 153, 255, 0.05) 100%);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 16px;
        padding: 32px;
        text-align: center;
        margin: 24px 0;
    }
    .score-number {
        font-family: 'Playfair Display', serif;
        font-size: 64px;
        font-weight: 900;
        background: linear-gradient(135deg, #00d4ff, #00ff88);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
    }
    .score-label {
        font-family: 'DM Mono', monospace;
        font-size: 12px;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #6b7d99;
        margin-top: 8px;
    }

    /* ─── Success/Failure Messages ─── */
    .result-message {
        font-family: 'Playfair Display', serif;
        font-size: 28px;
        font-weight: 700;
        text-align: center;
        margin: 24px 0;
        line-height: 1.4;
    }
    .result-passed {
        background: linear-gradient(135deg, #00ff88 0%, #00d4ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .result-rejected {
        background: linear-gradient(135deg, #ff6b6b 0%, #ff9999 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* ─── Divider ─── */
    .divider {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.2), transparent);
        margin: 28px 0;
    }

    /* ─── Round Badge ─── */
    .round-badge {
        display: inline-block;
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(0, 153, 255, 0.1) 100%);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 100px;
        padding: 8px 20px;
        font-family: 'DM Mono', monospace;
        font-size: 11px;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #00d4ff;
        margin-bottom: 16px;
    }

    /* ─── Info Box ─── */
    [data-testid="stAlert"] {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.08) 0%, rgba(0, 153, 255, 0.05) 100%) !important;
        border: 1px solid rgba(0, 212, 255, 0.3) !important;
        border-radius: 12px !important;
        color: #a8c5dd !important;
    }
    [data-testid="stAlert"][data-testid*="error"] {
        background: linear-gradient(135deg, rgba(255, 68, 68, 0.08) 0%, rgba(255, 107, 107, 0.05) 100%) !important;
        border-color: rgba(255, 68, 68, 0.3) !important;
        color: #ffaaaa !important;
    }
    [data-testid="stAlert"][data-testid*="success"] {
        background: linear-gradient(135deg, rgba(0, 255, 136, 0.08) 0%, rgba(0, 212, 255, 0.05) 100%) !important;
        border-color: rgba(0, 255, 136, 0.3) !important;
        color: #a8ffcc !important;
    }

    /* ─── Main Container ─── */
    .main .block-container {
        padding-top: 0 !important;
        max-width: 1000px !important;
    }

    /* ─── Scrollbar ─── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(0, 212, 255, 0.3); border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(0, 212, 255, 0.6); }

    /* ─── Metric styling ─── */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.08) 0%, rgba(0, 153, 255, 0.05) 100%) !important;
        border: 1px solid rgba(0, 212, 255, 0.2) !important;
        border-radius: 12px !important;
        padding: 16px !important;
    }

    /* Hide branding */
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)



if "interview_started" not in st.session_state:
    st.session_state.interview_started = False

if "graph_state" not in st.session_state:
    st.session_state.graph_state = {}


def reset_interview():
    """Clears the session state to start fresh."""
    st.session_state.interview_started = False
    st.session_state.graph_state = {}
    st.rerun()




with st.sidebar:
    st.markdown('<p class="sidebar-title">⚡ FORGE Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    if st.session_state.interview_started:
        state = st.session_state.graph_state
        current_round = state.get("current_round", "Logical")
        q_count = state.get("question_count", 0)
        scores = state.get("scores", {"Logical": 0, "Technical": 0, "HR": 0})
        status = state.get("status", "ongoing")

        
        st.markdown(f'<p style="color: #8a92b3; font-size: 12px; margin: 0 0 16px; letter-spacing: 1px;"><strong>TARGET ROLE</strong></p>', unsafe_allow_html=True)
        st.markdown(f'<p style="color: #00d4ff; font-size: 15px; font-weight: 600; margin: 0 0 24px;">{state.get("target_role")}</p>', unsafe_allow_html=True)

        
        if status == "ongoing":
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">🟢 Current Round</div><div style="color: #00ff88; font-size: 14px; font-weight: 600;">{current_round}</div></div>',
                unsafe_allow_html=True
            )
        elif status == "passed":
            st.markdown(
                '<div class="metric-card status-passed"><div class="metric-label">✓ Status</div><div style="color: #00ff88; font-size: 14px; font-weight: 600;">HIRED</div></div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div class="metric-card status-rejected"><div class="metric-label">✗ Status</div><div style="color: #ff4444; font-size: 14px; font-weight: 600;">REJECTED</div></div>',
                unsafe_allow_html=True
            )

        
        st.markdown(f'<p style="color: #6b7d99; font-size: 11px; letter-spacing: 1px; margin: 20px 0 10px; text-transform: uppercase;">Question Progress</p>', unsafe_allow_html=True)
        st.progress(min(q_count / 5.0, 1.0))
        st.markdown(f'<p style="color: #4b5563; font-size: 11px; text-align: center; margin-top: 6px;">{q_count} / 5</p>', unsafe_allow_html=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        
        st.markdown('<p style="color: #8a92b3; font-size: 12px; margin: 0 0 16px; letter-spacing: 1px; text-transform: uppercase;"><strong>Scoreboard</strong></p>', unsafe_allow_html=True)

        for category in ["Logical", "Technical", "HR"]:
            score = scores.get(category, 0)
            st.markdown(
                f'''<div class="metric-card">
                    <div class="metric-label">{category}</div>
                    <div style="font-family: 'Playfair Display', serif; color: #00d4ff; font-size: 20px; font-weight: 700;">{score}<span style="color: #4b5563; font-size: 14px;">/50</span></div>
                </div>''',
                unsafe_allow_html=True
            )

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

    st.button("↻ Restart Interview", on_click=reset_interview, type="secondary", use_container_width=True)



if not st.session_state.interview_started:
    st.markdown("""
    <div class="forge-hero">
        <span class="eyebrow">AI-Powered Interview Platform</span>
        <h1>FORGE</h1>
        <p class="tagline">Master your interview skills through intelligent, adaptive questioning from advanced AI interviewers.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

    st.markdown('<p style="text-align: center; color: #8a92b3; font-size: 13px; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 28px;">Select Your Target Role</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    roles = [
        {"name": "AI Engineer", "icon": "🤖", "col": col1},
        {"name": "MERN Stack Web Developer", "icon": "💻", "col": col1},
        {"name": "Product Manager", "icon": "📊", "col": col2},
        {"name": "Sales Manager", "icon": "🎯", "col": col2},
    ]

    selected_role = None
    for role in roles:
        with role["col"]:
            if st.button(f'{role["icon"]}\n\n{role["name"]}', key=role["name"], use_container_width=True):
                selected_role = role["name"]

    if selected_role:
        st.session_state.graph_state = app.invoke({"target_role": selected_role, "chat_history": []})
        st.session_state.interview_started = True
        st.rerun()




elif st.session_state.interview_started:
    state = st.session_state.graph_state
    current_round = state.get("current_round", "Logical")
    q_count = state.get("question_count", 0)
    status = state.get("status", "ongoing")

    
    if status == "ongoing":
        st.markdown(f'<div class="round-badge" style="display: flex; justify-content: center; margin-bottom: 28px;">ROUND · {current_round.upper()}</div>', unsafe_allow_html=True)
        st.progress(min(q_count / 5.0, 1.0))

    
    if q_count > 0 and q_count % 5 == 1 and state.get("scores", {}).get("Logical") > 0:
        prev_round = state.get("scores", {})
        if "Technical" in prev_round:
            score = prev_round.get("Logical", 0)
            st.markdown(
                f'<div style="background: rgba(0, 255, 136, 0.1); border: 1px solid rgba(0, 255, 136, 0.3); border-radius: 12px; padding: 16px; text-align: center; margin-bottom: 20px;"><span style="color: #00ff88; font-weight: 600;">✓ Logical Round Complete</span> <span style="color: #6b7d99;">You scored {score}/50</span></div>',
                unsafe_allow_html=True
            )

    
    for msg in state.get("chat_history", []):
        if isinstance(msg, AIMessage):
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(msg.content)
        elif isinstance(msg, HumanMessage):
            with st.chat_message("user", avatar="👤"):
                st.markdown(msg.content)

    
    if status == "ongoing":
        if prompt := st.chat_input("Your answer...", key="chat_input"):
            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)

            with st.spinner("🔄 Evaluating response..."):
                st.session_state.graph_state = app.invoke({**state, "current_answer": prompt})
                st.rerun()

    
    else:
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        
        final_score = sum(state.get("scores", {}).values())
        scores_dict = state.get("scores", {})

        st.markdown(
            f'''<div class="score-container">
                <p class="score-number">{final_score}</p>
                <p class="score-label">Total Score</p>
            </div>''',
            unsafe_allow_html=True
        )

        
        score_cols = st.columns(3)
        for i, (category, score) in enumerate(scores_dict.items()):
            with score_cols[i]:
                st.markdown(
                    f'''<div style="background: rgba(0, 212, 255, 0.08); border: 1px solid rgba(0, 212, 255, 0.2); border-radius: 12px; padding: 18px; text-align: center;">
                        <p style="font-family: 'DM Mono', monospace; font-size: 10px; letter-spacing: 2px; text-transform: uppercase; color: #6b7d99; margin: 0 0 10px;">{category}</p>
                        <p style="font-family: 'Playfair Display', serif; font-size: 32px; font-weight: 700; color: #00d4ff; margin: 0;">{score}</p>
                        <p style="font-size: 11px; color: #4b5563; margin: 6px 0 0;">Out of 50</p>
                    </div>''',
                    unsafe_allow_html=True
                )

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        if status == "passed":
            st.balloons()
            st.markdown(
                '<p class="result-message result-passed">🎉 Congratulations! You\'ve been hired!</p>',
                unsafe_allow_html=True
            )
            st.markdown(
                '<p style="text-align: center; color: #a8ffcc; font-size: 14px;">Your interview performance was exceptional. Welcome to the team!</p>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<p class="result-message result-rejected">❌ Interview Not Successful</p>',
                unsafe_allow_html=True
            )
            st.markdown(
                '<p style="text-align: center; color: #ffaaaa; font-size: 14px;">Thank you for your time. We encourage you to practice and try again.</p>',
                unsafe_allow_html=True
            )