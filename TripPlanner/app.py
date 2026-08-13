import os
import time
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# =======================================================================================================
# OPTIONAL IMPORT — the app should still load and look nice even if crewai isn't installed yet
# =======================================================================================================
try:
    from crewai import Process, Agent, Task, Crew, LLM
    from crewai_tools import SerperDevTool, ScrapeWebsiteTool
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False


# =======================================================================================================
# PAGE CONFIG
# =======================================================================================================
st.set_page_config(
    page_title="Surprise Trip Planner",
    page_icon="🎈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =======================================================================================================
# STYLING — light blue & white, with a few slow-drifting balloons & flowers in the background
# =======================================================================================================
CUSTOM_CSS = """
<style>
.stApp {
    background: linear-gradient(160deg, #eaf6ff 0%, #f7fcff 45%, #ffffff 100%);
}

/* ---------- Floating decorations (subtle, slow) ---------- */
.floaters {
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    overflow: hidden;
    pointer-events: none;
    z-index: 0;
}
.floater {
    position: absolute;
    bottom: -10%;
    font-size: 2.2rem;
    opacity: 0.16;
    animation-name: floatUp;
    animation-timing-function: ease-in-out;
    animation-iteration-count: infinite;
}
.f1 { left: 6%;  animation-duration: 26s; animation-delay: 0s; }
.f2 { left: 22%; animation-duration: 32s; animation-delay: 4s; font-size: 1.8rem; }
.f3 { left: 48%; animation-duration: 28s; animation-delay: 8s; }
.f4 { left: 72%; animation-duration: 34s; animation-delay: 2s; font-size: 1.9rem; }
.f5 { left: 88%; animation-duration: 30s; animation-delay: 6s; }

@keyframes floatUp {
    0%   { transform: translateY(0) rotate(0deg);     opacity: 0; }
    8%   { opacity: 0.16; }
    92%  { opacity: 0.16; }
    100% { transform: translateY(-115vh) rotate(18deg); opacity: 0; }
}

/* ---------- Hero ---------- */
.hero-wrap {
    position: relative;
    z-index: 1;
    text-align: center;
    padding: 1.2rem 0 0.6rem 0;
}
.hero-title {
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(90deg, #2f8fd1, #6fc3f0);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    margin-bottom: 0.2rem;
}
.hero-sub {
    color: #4d7ea8;
    font-size: 1.05rem;
    font-weight: 400;
}

/* ---------- Form card ---------- */
div[data-testid="stForm"] {
    background: #ffffff;
    border-radius: 22px;
    padding: 1.8rem 2.2rem;
    border: 1px solid #dbeefc;
    box-shadow: 0 8px 24px rgba(110, 175, 220, 0.16);
    position: relative;
    z-index: 1;
}

/* ---------- Bordered containers (results, packing, countdown) ---------- */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 18px !important;
    border-color: #dbeefc !important;
    box-shadow: 0 6px 18px rgba(110, 175, 220, 0.13);
    position: relative;
    z-index: 1;
}

/* ---------- Buttons ---------- */
.stButton > button, .stFormSubmitButton > button {
    background: linear-gradient(90deg, #6fc3f0, #4aa8e0);
    color: white;
    border: none;
    border-radius: 30px;
    padding: 0.55rem 1.6rem;
    font-weight: 600;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
    box-shadow: 0 4px 12px rgba(74, 168, 224, 0.35);
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    transform: translateY(-1px) scale(1.02);
    box-shadow: 0 6px 16px rgba(74, 168, 224, 0.45);
    color: white;
}

/* ---------- Misc text ---------- */
h1, h2, h3 { color: #1c5d8c; }
div[data-testid="stMetricValue"] { color: #1976d2; }
.footer-note {
    text-align: center;
    color: #7fa9c9;
    font-size: 0.85rem;
    margin-top: 2rem;
    position: relative;
    z-index: 1;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.markdown(
    """
    <div class="floaters">
        <span class="floater f1">🎈</span>
        <span class="floater f2">🌸</span>
        <span class="floater f3">🎈</span>
        <span class="floater f4">🌷</span>
        <span class="floater f5">🌼</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-wrap">
        <div class="hero-title">🎈 Surprise Trip Planner 🌸</div>
        <div class="hero-sub">Tell us a little about you — our AI travel agents will dream up the rest.</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =======================================================================================================
# SESSION STATE
# =======================================================================================================
if "itinerary" not in st.session_state:
    st.session_state.itinerary = None
if "packing_list" not in st.session_state:
    st.session_state.packing_list = []
if "trip_meta" not in st.session_state:
    st.session_state.trip_meta = {}


# =======================================================================================================
# SIDEBAR — API KEYS
# =======================================================================================================
with st.sidebar:
    st.markdown("### 🔑 API Keys")
    st.caption("Stored only for this session — never written to disk.")

    openrouter_key = st.text_input(
        "OpenRouter API key",
        value=os.environ.get("OPENROUTER_API_KEY", ""),
        type="password",
    )
    serper_key = st.text_input(
        "Serper API key",
        value=os.environ.get("SERPER_API_KEY", ""),
        type="password",
    )

    if openrouter_key:
        os.environ["OPENROUTER_API_KEY"] = openrouter_key
    if serper_key:
        os.environ["SERPER_API_KEY"] = serper_key

    st.markdown(
        "Free keys: [OpenRouter](https://openrouter.ai/keys) · "
        "[Serper](https://serper.dev)"
    )

    if not CREWAI_AVAILABLE:
        st.warning("`crewai` isn't installed yet. Run:\n\n`pip install -r requirements.txt`")


# =======================================================================================================
# PACKING CHECKLIST GENERATOR — the "extra" travel-agent touch
# =======================================================================================================
INTEREST_TAGS = [
    "Beach 🏖️", "Hiking ⛰️", "Food 🍜", "Culture 🏛️", "Nightlife 🌃",
    "Adventure 🪂", "Relaxation 🧘", "Shopping 🛍️", "Nature 🌿", "Romance 💕",
]

PACKING_DB = {
    "beach":       ["Swimsuit 🩱", "Reef-safe sunscreen ☀️", "Beach towel", "Flip-flops"],
    "hiking":      ["Hiking boots 🥾", "Moisture-wicking socks", "Light rain jacket", "Refillable water bottle"],
    "food":        ["Stretchy pants 😄", "Antacids (just in case)", "Reusable food container"],
    "culture":     ["Modest clothing for temples/sites", "Small notebook & pen", "Portable charger"],
    "nightlife":   ["A statement outfit ✨", "Comfortable shoes for dancing"],
    "adventure":   ["Compact first-aid kit", "Quick-dry clothing", "Action camera"],
    "relaxation":  ["Cozy loungewear", "Travel pillow", "A good book 📖"],
    "shopping":    ["Foldable extra bag", "Packing cubes"],
    "nature":      ["Insect repellent", "Mini binoculars", "Light layers"],
    "romance":     ["Something special for date night 💕", "Camera for memories"],
}

DEFAULT_ITEMS = [
    "Passport & travel docs 🛂", "Phone charger & adapter",
    "Refillable water bottle", "Light jacket", "Toiletries bag",
]


def generate_packing_list(interests_str: str):
    lower = interests_str.lower()
    items = list(DEFAULT_ITEMS)
    for key, extras in PACKING_DB.items():
        if key in lower:
            for item in extras:
                if item not in items:
                    items.append(item)
    return items


# =======================================================================================================
# CREW BUILDER — mirrors the original agents/tasks, built fresh per run
# =======================================================================================================
def build_crew():
    web_search_tool = SerperDevTool()
    scraper_tool = ScrapeWebsiteTool()

    llm = LLM(model="openrouter/nvidia/nemotron-3-ultra-550b-a55b:free", stream=True)

    activity_planner = Agent(
        role="Personalized Activity Planner",
        goal="Analyze user preferences and suggest an exciting surprise destination along with a curated list of themed activities.",
        backstory="You are a master of surprises and a world-renowned travel planner. You excel at reading between the lines of traveler preferences to uncover the perfect secret destination and unique experiences they wouldn't find on their own.",
        verbose=True,
        tools=[web_search_tool, scraper_tool],
        allow_delegation=False,
        llm=llm,
    )

    restaurant_scout = Agent(
        role="Restaurant and Scenic Location Scout",
        goal="Discover top-rated, hidden gem restaurants and breathtaking scenic spots at the chosen destination.",
        backstory="You are an elite food critic and location scout. You know how to find places that offer not just a meal, but an unforgettable experience with stunning views.",
        tools=[web_search_tool, scraper_tool],
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )

    itinerary_compiler = Agent(
        role="Itinerary Compiler",
        goal="Compile all research into a cohesive, perfectly timed surprise travel itinerary.",
        backstory="You are a meticulous logistician and master storyteller. You take raw ideas, locations, and restaurants, and weave them into a flawless, daily itinerary that maximizes joy and minimizes travel friction.",
        tools=[],
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )

    activity_planning_task = Task(
        description="Analyze the traveler's origin ({origin}), travel dates ({travel_dates}), and interests ({interests}). Suggest 3 potential surprise destinations. Choose the best one and list 5 unique activities tailored to their interests.",
        expected_output="A final selected destination and a detailed list of 5 personalized activities.",
        agent=activity_planner,
    )

    restaurant_scout_task = Task(
        description="Based on the final destination chosen by the Activity Planner, find 3 incredible restaurants and 2 scenic spots. Focus on places that match the traveler's core interests: {interests}.",
        expected_output="A curated list of 3 restaurants and 2 scenic locations, including brief descriptions and reasons for selection.",
        agent=restaurant_scout,
    )

    itinerary_compilation_task = Task(
        description="Take the destination, activities, restaurants, and scenic spots from the previous tasks. Create a detailed, day-by-day itinerary for {travel_dates}. Include travel logistics originating from {origin}.",
        expected_output="A beautifully formatted, detailed daily itinerary document in Markdown format.",
        agent=itinerary_compiler,
    )

    def task_done(task_output):
        label = getattr(task_output, "description", "Step")[:70]
        status_box.write(f"✅ {label}…")

    crew = Crew(
        agents=[activity_planner, restaurant_scout, itinerary_compiler],
        tasks=[activity_planning_task, restaurant_scout_task, itinerary_compilation_task],
        process=Process.sequential,
        verbose=True,
        task_callback=task_done,
    )
    return crew


# =======================================================================================================
# MAIN FORM
# =======================================================================================================
with st.form("trip_form"):
    col1, col2 = st.columns(2)
    with col1:
        origin = st.text_input("🛫 Traveling from", placeholder="e.g., New York, USA")
        start_date = st.date_input("📅 Start date")
    with col2:
        chosen_tags = st.multiselect("💖 What do you love?", INTEREST_TAGS, default=[])
        end_date = st.date_input("📅 End date")

    extra_interests = st.text_input("Anything else you love? (optional)", placeholder="e.g., live jazz, street art")

    submitted = st.form_submit_button("🎈 Plan My Surprise Trip", use_container_width=True)


# =======================================================================================================
# HANDLE SUBMISSION
# =======================================================================================================
if submitted:
    interests_str = ", ".join(tag.split(" ")[0] for tag in chosen_tags)
    if extra_interests:
        interests_str = f"{interests_str}, {extra_interests}" if interests_str else extra_interests

    if not origin or not interests_str:
        st.warning("Please fill in your origin and at least one interest before we start planning.")
    elif end_date < start_date:
        st.warning("Your end date is before your start date — mind double-checking it?")
    elif not CREWAI_AVAILABLE:
        st.error("`crewai` isn't installed. Run `pip install -r requirements.txt` and refresh the page.")
    elif not os.environ.get("OPENROUTER_API_KEY") or not os.environ.get("SERPER_API_KEY"):
        st.error("Please add your OpenRouter and Serper API keys in the sidebar first.")
    else:
        travel_dates_str = f"{start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}"

        with st.status("🧞 Our AI travel agents are working their magic…", expanded=True) as status_box:
            status_box.write("🗺️ Activity Planner is dreaming up destinations…")
            status_box.write("🍽️ Restaurant Scout is on standby…")
            status_box.write("📝 Itinerary Compiler is sharpening its pencil…")

            try:
                crew = build_crew()
                result = crew.kickoff(
                    inputs={
                        "origin": origin,
                        "travel_dates": travel_dates_str,
                        "interests": interests_str,
                    }
                )
                st.session_state.itinerary = result.raw
                st.session_state.packing_list = generate_packing_list(interests_str)
                st.session_state.trip_meta = {
                    "origin": origin,
                    "start_date": start_date,
                    "end_date": end_date,
                    "interests": interests_str,
                }
                status_box.update(label="✅ Your surprise itinerary is ready!", state="complete")
            except Exception as e:
                status_box.update(label="❌ Something went wrong", state="error")
                st.error(f"The trip planning crew ran into an issue: {e}")

        if st.session_state.itinerary:
            st.balloons()


# =======================================================================================================
# RESULTS
# =======================================================================================================
if st.session_state.itinerary:
    meta = st.session_state.trip_meta
    days_to_go = (meta["start_date"] - datetime.now().date()).days

    col_main, col_side = st.columns([2, 1])

    with col_main:
        with st.container(border=True):
            st.markdown("### 🗺️ Your Surprise Itinerary")
            st.markdown(st.session_state.itinerary)

            dl1, dl2 = st.columns(2)
            with dl1:
                st.download_button(
                    "⬇️ Download as Markdown",
                    data=st.session_state.itinerary,
                    file_name="surprise_itinerary.md",
                    use_container_width=True,
                )
            with dl2:
                st.download_button(
                    "⬇️ Download as Text",
                    data=st.session_state.itinerary,
                    file_name="surprise_itinerary.txt",
                    use_container_width=True,
                )

    with col_side:
        with st.container(border=True):
            st.markdown("### ⏳ Countdown")
            if days_to_go > 0:
                st.metric("Days to go", days_to_go)
            elif days_to_go == 0:
                st.metric("Today's the day!", "🎉")
            else:
                st.metric("Trip dates", "in the past")

        with st.container(border=True):
            st.markdown("### 🧳 Smart Packing Checklist")
            st.caption("Auto-built from your interests — tick items off as you pack.")
            for item in st.session_state.packing_list:
                st.checkbox(item, key=f"pack_{item}")

st.markdown(
    '<div class="footer-note">Made with 💙 for wandering hearts</div>',
    unsafe_allow_html=True,
)
