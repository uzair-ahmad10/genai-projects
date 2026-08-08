import streamlit as st
import time
from src.pipeline import run_research_pipeline

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="ResearchMind",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# CUSTOM CSS TO MATCH SCREENSHOT
# ==========================================
st.markdown("""
<style>
    /* Force dark theme background */
    .stApp {
        background-color: #0b0c10 !important;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    /* Hide top header and padding */
    header {visibility: hidden;}
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px !important;
    }

    /* Custom Input Field Styling */
    div[data-baseweb="input"] {
        background-color: #1a1b23 !important;
        border: 1px solid #2d303e !important;
        border-radius: 10px !important;
    }
    div[data-baseweb="input"] > input {
        color: white !important;
        padding: 14px !important;
        font-size: 16px !important;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: #ff7a00 !important;
    }

    /* Custom Button Styling */
    .stButton > button {
        background: linear-gradient(90deg, #ff8c00 0%, #ff6a00 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 24px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        letter-spacing: 0.5px !important;
        width: 100%;
        transition: transform 0.2s, box-shadow 0.2s !important;
        box-shadow: 0 4px 14px rgba(255, 122, 0, 0.2) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 122, 0, 0.4) !important;
    }

    /* Pipeline Cards Styling */
    .pipeline-card {
        background-color: #111217;
        border: 1px solid #1f2129;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        transition: all 0.3s ease;
    }
    .pipeline-card.done {
        border-left: 3px solid #10b981;
        background-color: #111815;
    }
    .pipeline-card.active {
        border-color: #ff7a00;
        box-shadow: 0 0 15px rgba(255, 122, 0, 0.1);
    }
    
    .card-title {
        color: #ffffff;
        font-weight: 600;
        font-size: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
    }
    .card-num { color: #ff7a00; margin-right: 12px; font-weight: 700; }
    .card-status-done { color: #10b981; font-size: 12px; font-weight: 700; letter-spacing: 1px;}
    .card-status-pending { color: #4b5563; font-size: 12px; font-weight: 700; letter-spacing: 1px;}
    .card-desc { color: #8b92a5; font-size: 14px; margin-left: 32px; }
    
    /* Result container */
    .results-container {
        background-color: #111217;
        border: 1px solid #1f2129;
        border-radius: 12px;
        padding: 30px;
        margin-top: 40px;
        color: #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# HEADER SECTION
# ==========================================
st.markdown("""
<div style="text-align: center; margin-bottom: 70px; margin-top: 40px;">
    <p style="color: #ff7a00; font-size: 11px; letter-spacing: 3px; font-weight: 700; text-transform: uppercase; margin-bottom: 15px;">Multi-Agent AI System</p>
    <h1 style="font-size: 5rem; font-weight: 900; margin: 0; padding: 0; letter-spacing: -2px; display: flex; justify-content: center; align-items: center;">
        <span style="color: #f8fafc; background: linear-gradient(180deg, #ffffff 0%, #a0aec0 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Research</span>
        <span style="color: #ff7a00;">Mind</span>
    </h1>
    <p style="color: #8b92a5; font-size: 15px; max-width: 550px; margin: 25px auto 0 auto; line-height: 1.6;">
        Four specialized AI agents collaborate — searching, scraping, writing, and critiquing — to deliver a polished research report on any topic.
    </p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# MAIN LAYOUT
# ==========================================
col_left, col_right = st.columns([1.1, 1], gap="large")

# State Management
if "pipeline_state" not in st.session_state:
    st.session_state.pipeline_state = "idle" # idle, running, done
if "results" not in st.session_state:
    st.session_state.results = None

with col_left:
    st.markdown('<div style="height: 60px;"></div>', unsafe_allow_html=True) # Spacer matching image
    st.markdown('<p style="color: #ff7a00; font-size: 12px; font-weight: 700; letter-spacing: 1px; margin-bottom: 8px;">RESEARCH TOPIC</p>', unsafe_allow_html=True)
    
    topic = st.text_input("Topic", label_visibility="collapsed", placeholder="Quantum computing breakthroughs in 2025")
    
    st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
    
    run_button = st.button("⚡ Run Research Pipeline", use_container_width=True)
    
    st.markdown("""
    <div style="margin-top: 20px; display: flex; align-items: center; gap: 10px;">
        <span style="color: #4b5563; font-size: 12px; font-weight: 600;">TRY ➔</span>
        <span style="background-color: #1a1b23; color: #8b92a5; padding: 6px 12px; border-radius: 6px; font-size: 12px; border: 1px solid #2d303e;">LLM agents 2025</span>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown('<h2 style="color: #ffffff; font-size: 24px; font-weight: 600; margin-bottom: 25px;">Pipeline</h2>', unsafe_allow_html=True)
    
    # Render Pipeline Visuals based on state
    if st.session_state.pipeline_state == "idle":
        st.markdown("""
        <div class="pipeline-card"><div class="card-title"><span class="card-num">01</span> Search Agent <span class="card-status-pending">PENDING</span></div><div class="card-desc">Gathers recent web information</div></div>
        <div class="pipeline-card"><div class="card-title"><span class="card-num">02</span> Reader Agent <span class="card-status-pending">PENDING</span></div><div class="card-desc">Scrapes & extracts deep content</div></div>
        <div class="pipeline-card"><div class="card-title"><span class="card-num">03</span> Writer Agent <span class="card-status-pending">PENDING</span></div><div class="card-desc">Drafts a comprehensive report</div></div>
        <div class="pipeline-card"><div class="card-title"><span class="card-num">04</span> Critic Agent <span class="card-status-pending">PENDING</span></div><div class="card-desc">Evaluates and scores the draft</div></div>
        """, unsafe_allow_html=True)
        
    elif st.session_state.pipeline_state == "running":
        # Because the backend blocks, we just show a generalized running state
        st.markdown("""
        <div class="pipeline-card active"><div class="card-title"><span class="card-num">01-04</span> Agents Working <span style="color: #ff7a00; font-size: 12px; font-weight: bold;">⚡ PROCESSING...</span></div><div class="card-desc">Running the multi-agent pipeline...</div></div>
        """, unsafe_allow_html=True)
        
    elif st.session_state.pipeline_state == "done":
        st.markdown("""
        <div class="pipeline-card done"><div class="card-title"><div><span class="card-num">01</span> Search Agent</div> <span class="card-status-done">✓ DONE</span></div><div class="card-desc">Gathers recent web information</div></div>
        <div class="pipeline-card done"><div class="card-title"><div><span class="card-num">02</span> Reader Agent</div> <span class="card-status-done">✓ DONE</span></div><div class="card-desc">Scrapes & extracts deep content</div></div>
        <div class="pipeline-card done"><div class="card-title"><div><span class="card-num">03</span> Writer Agent</div> <span class="card-status-done">✓ DONE</span></div><div class="card-desc">Drafts a comprehensive report</div></div>
        <div class="pipeline-card done"><div class="card-title"><div><span class="card-num">04</span> Critic Agent</div> <span class="card-status-done">✓ DONE</span></div><div class="card-desc">Evaluates and scores the draft</div></div>
        """, unsafe_allow_html=True)

# ==========================================
# EXECUTION LOGIC
# ==========================================
if run_button:
    if not topic.strip():
        st.error("Please enter a research topic.")
    else:
        st.session_state.pipeline_state = "running"
        st.rerun() # Rerun to show the "running" UI state

# If state is running, actually execute the backend
if st.session_state.pipeline_state == "running":
    try:
        # Call the existing backend function
        st.session_state.results = run_research_pipeline(topic)
        st.session_state.pipeline_state = "done"
        st.rerun() # Rerun to show the "done" UI state and results
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.session_state.pipeline_state = "idle"

# ==========================================
# RESULTS DISPLAY
# ==========================================
if st.session_state.pipeline_state == "done" and st.session_state.results:
    res = st.session_state.results
    
    st.markdown("<div class='results-container'>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color: #ff7a00; margin-bottom: 20px;'>Report: {topic}</h3>", unsafe_allow_html=True)
    
    # Use tabs for a clean result layout matching the dark theme
    tab1, tab2, tab3 = st.tabs(["📝 Final Report", "🎯 Critic Evaluation", "🔬 Raw Data"])
    
    with tab1:
        st.markdown(res.get('report', 'No report generated.'))
    
    with tab2:
        st.markdown(res.get('feedback', 'No feedback provided.'))
        
    with tab3:
        st.markdown("**Search Results:**")
        st.code(res.get('search_results', ''), language="text")
        st.markdown("**Scraped Content:**")
        st.code(res.get('scraped_content', '')[:1500] + "\n...[truncated for view]", language="text")
        
    st.markdown("</div>", unsafe_allow_html=True)