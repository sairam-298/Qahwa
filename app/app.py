import os
import sys
import base64
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from PIL import Image
import streamlit as st

# For Windows compatibility
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# App Imports
try:
    from scripts.agent import route_query
    from scripts.booking import bookingscheck
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

# ===== Paths =====
LOGO_PATH = PROJECT_ROOT / "img" / "qahwalogo.png"
HERO_IMAGE_PATH = PROJECT_ROOT / "img" / "hero2.png"

# ===== Theme Colors =====
DARK_BROWN = "#2C1810"
MEDIUM_BROWN = "#4A2C17"
GOLDEN_YELLOW = "#D4AF37"
WARM_CREAM = "#F5F1E8"
LIGHT_BROWN = "#8B6F47"
COFFEE_GRADIENT = "linear-gradient(135deg, #4A2C17 0%, #6B4423 30%, #8B6F47 70%, #A67C52 100%)"

# ===== Page Config =====
st.set_page_config(page_title="Qahwa", page_icon="☕")

# ===== Custom CSS Styling =====
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Crimson+Text:ital,wght@0,400;0,600;1,400&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap');

.stApp {{
    background: {COFFEE_GRADIENT};
    color: {WARM_CREAM};
    min-height: 100vh;
    font-family: 'Libre Baskerville', serif;
}}

#MainMenu, footer, header {{visibility: hidden;}}

.main .block-container {{
    padding-top: 0rem !important;
    padding-bottom: 2rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    max-width: 100% !important;
}}

.stApp > div:first-child {{margin-top: 0 !important;}}

section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {DARK_BROWN} 0%, {MEDIUM_BROWN} 100%);
    border-right: 2px solid {GOLDEN_YELLOW};
}}

section[data-testid="stSidebar"] * {{
    color: {WARM_CREAM} !important;
}}

.hero-wrapper {{
    position: relative;
    width: 100vw;
    margin-left: -50vw;
    margin-right: -50vw;
    left: 50%;
    right: 50%;
    background: {DARK_BROWN};
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}}

.hero-wrapper img {{
    width: 100%;
    height: 400px;
    object-fit: cover;
    border-bottom: 3px solid {GOLDEN_YELLOW};
}}

.main-content {{
    background: rgba(245, 241, 232, 0.85);
    backdrop-filter: blur(5px);
    margin: 2rem auto;
    padding: 2.5rem;
    border-radius: 20px;
    box-shadow: 0 6px 25px rgba(44, 24, 16, 0.15);
    border: 1px solid rgba(212, 175, 55, 0.2);
    max-width: 1000px;
}}

.main-content h1 {{
    color: {GOLDEN_YELLOW};
    font-family: 'Crimson Text', serif;
    font-size: 3rem;
    font-weight: 600;
    text-align: center;
    margin-bottom: 1rem;
    text-shadow: 2px 2px 4px rgba(44, 24, 16, 0.3);
}}

.elegant-tagline {{
    text-align: center;
    font-family: 'Crimson Text', serif;
    color: {DARK_BROWN};
    font-size: 1.4rem;
    font-style: italic;
    font-weight: 600;
    margin: 2rem 0;
    line-height: 1.8;
    padding: 1.5rem 2rem;
    border-left: 2px solid rgba(139, 111, 71, 0.3);
    border-right: 2px solid rgba(139, 111, 71, 0.3);
    background: rgba(139, 111, 71, 0.06);
    border-radius: 15px;
    backdrop-filter: blur(3px);
}}

.stButton > button {{
    background: linear-gradient(135deg, {GOLDEN_YELLOW} 0%, #B8860B 100%) !important;
    color: white !important;
    border: none !important;
    font-weight: 600 !important;
    font-family: 'Libre Baskerville', serif !important;
    padding: 0.6rem 2rem !important;
    border-radius: 25px !important;
    box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3) !important;
    transition: all 0.3s ease !important;
}}

.stButton > button:hover {{
    background: linear-gradient(135deg, #B8860B 0%, {GOLDEN_YELLOW} 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(212, 175, 55, 0.4) !important;
}}

</style>
""", unsafe_allow_html=True)

# ===== Sidebar =====
with st.sidebar:
    st.markdown("---")
    if LOGO_PATH.exists():
        logo_img = Image.open(str(LOGO_PATH))
        st.image(logo_img, use_container_width=True)
    st.markdown("---")
    st.markdown(f"""
    <div style="
        font-family: 'Crimson Text', serif;
        color: {WARM_CREAM};
        font-size: 1rem;
        line-height: 1.7;
        padding: 1.5rem;
        background: rgba(44, 24, 16, 0.3);
        border-radius: 12px;
        border: 1px solid rgba(212, 175, 55, 0.2);
        backdrop-filter: blur(5px);
        text-align: left;
    ">
        At <span style="color: {GOLDEN_YELLOW}; font-weight: bold;">Qahwa</span>, we curate the finest 
        <em>Arabic coffee seeds</em> — like the citrusy 
        <span style="color: {GOLDEN_YELLOW}; font-weight: bold;">Yemeni Mokha</span> — with select blends 
        from Ethiopia and Mexico.
        <br><br>
        Choose from elegant <strong>small (100g)</strong>, <strong>medium (250g)</strong>, 
        <strong>large (500g)</strong>, and 
        <strong>extra large (1kg)</strong> packs for every brewing mood.
        <br><br>
        Join our 
        <span style="color: #E6D3A3; font-style: italic;">weekend brewing workshops</span> 
        to master the perfect Arabic pour.
    </div>
    """, unsafe_allow_html=True)

# ===== Hero Image =====
if HERO_IMAGE_PATH.exists():
    with open(str(HERO_IMAGE_PATH), "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    st.markdown(
        f"""
        <div class="hero-wrapper">
            <img src="data:image/png;base64,{encoded}" alt="Qahwa Coffee Experience" />
        </div>
        """, unsafe_allow_html=True
    )
else:
    st.markdown("""
        <div class="hero-wrapper">
            <div style="height: 400px; display: flex; align-items: center; justify-content: center; color: #D4AF37; font-size: 2rem;">
                ☕ Qahwa Coffee Experience ☕
            </div>
        </div>
    """, unsafe_allow_html=True)

# ===== Main Content =====
st.markdown('<div class="main-content">', unsafe_allow_html=True)
st.title("☕ Welcome to Qahwa!")

st.markdown("""
    <div class="elegant-tagline">
        "Where every cup tells a story of ancient traditions and modern excellence"
    </div>
""", unsafe_allow_html=True)

mode = st.radio("What would you like to do?", ["Ask a question", "Book a workshop"])

if mode == "Ask a question":
    st.subheader("💬 Ask Qahwa about Arabic Coffee, Pricing, or Products")
    
    user_query = st.text_input(
        label="Your Question",
        key="search_input",
        placeholder="e.g., Tell me about your coffee bean catalog, pricing, or brewing methods..."
    )

    if user_query:
        with st.spinner("Brewing your answer... ☕"):
            answer = route_query(user_query)
        st.markdown(f"""
            <div style="
                background: rgba(212, 175, 55, 0.1);
                padding: 1.5rem;
                border-radius: 10px;
                border-left: 4px solid #D4AF37;
                margin-top: 1rem;
            ">
                <strong>Qahwa says:</strong><br><br>
                {answer}
            </div>
        """, unsafe_allow_html=True)

else:
    st.subheader("📅 Book your Coffee Brewing Workshop")
    
    st.markdown("""
        <div style="
            background: rgba(212, 175, 55, 0.1);
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(212, 175, 55, 0.3);
        ">
            <strong>Workshop Details:</strong><br>
            • Duration: 2 hours<br>
            • Days: Friday, Saturday, Sunday<br>
            • Learn traditional Arabic coffee preparation techniques
        </div>
    """, unsafe_allow_html=True)

    time_slots = ["9:00 AM", "10:45 AM", "4:00 PM", "5:45 PM"]

    def is_valid_workshop_day(date):
        return date.weekday() in [4, 5, 6]  # Friday, Saturday, Sunday

    valid_dates = [
        datetime.today() + timedelta(days=i)
        for i in range(15)
        if is_valid_workshop_day(datetime.today() + timedelta(days=i))
    ]

    with st.form("booking_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Your Name *")
            date = st.selectbox(
                "Select a Date *", 
                valid_dates, 
                format_func=lambda d: d.strftime('%A, %d %B %Y')
            )
        with col2:
            email = st.text_input("Your Email *")
            time = st.selectbox("Choose a Time Slot *", time_slots)

        submitted = st.form_submit_button("✅ Confirm Booking")
        if submitted:
            if not name or not email:
                st.error("Please fill in all required fields (*)")
            else:
                user_input = (
                    f"My name is {name}. I'd like to book the Coffee Brewing Workshop on {date.strftime('%d/%m/%Y')} "
                    f"at {time}. My email is {email}."
                )
                with st.spinner("Booking your workshop slot..."):
                    confirmation = bookingscheck(user_input)
                st.success(confirmation)

st.markdown('</div>', unsafe_allow_html=True)
