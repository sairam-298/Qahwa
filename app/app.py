import os
import sys
import base64
from datetime import datetime, timedelta
from PIL import Image
import streamlit as st

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from scripts.agent import route_query
    from scripts.booking import bookingscheck
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()

# ===== Styling Variables =====
LOGO_PATH = "D:\\qar\\qahwalogo.png"
HERO_IMAGE_PATH = r"D:\\qar\\hero2.png"
# Updated color scheme - warmer, more cohesive
DARK_BROWN = "#2C1810"
MEDIUM_BROWN = "#4A2C17"
GOLDEN_YELLOW = "#D4AF37"
WARM_CREAM = "#F5F1E8"
LIGHT_BROWN = "#8B6F47"
COFFEE_GRADIENT = "linear-gradient(135deg, #4A2C17 0%, #6B4423 30%, #8B6F47 70%, #A67C52 100%)"

# ===== Streamlit Config and CSS =====
st.set_page_config(page_title="Qahwa", page_icon="☕")

st.markdown(f"""
    <style>
        /* Import elegant fonts */
        @import url('https://fonts.googleapis.com/css2?family=Crimson+Text:ital,wght@0,400;0,600;1,400&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap');
        
        /* Global app styling */
        .stApp {{
            background: {COFFEE_GRADIENT};
            color: {WARM_CREAM};
            min-height: 100vh;
            font-family: 'Libre Baskerville', serif;
        }}

        /* Remove default Streamlit elements */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        /* Remove top padding and whitespace */
        .main .block-container {{
            padding-top: 0rem !important;
            padding-bottom: 2rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 100% !important;
        }}

        /* Remove any default margins */
        .stApp > div:first-child {{
            margin-top: 0 !important;
        }}

        /* Sidebar styling */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {DARK_BROWN} 0%, {MEDIUM_BROWN} 100%);
            border-right: 2px solid {GOLDEN_YELLOW};
        }}

        section[data-testid="stSidebar"] * {{
            color: {WARM_CREAM} !important;
        }}

        /* Hero section - full width, no white spaces */
        .hero-wrapper {{
            position: relative;
            left: 50%;
            right: 50%;
            margin-left: -50vw;
            margin-right: -50vw;
            margin-top: -1rem;
            margin-bottom: 0;
            width: 100vw;
            background: {DARK_BROWN};
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }}

        .hero-wrapper img {{
            width: 100%;
            height: 400px;
            object-fit: cover;
            display: block;
            border-bottom: 3px solid {GOLDEN_YELLOW};
        }}

        /* Main content container */
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

        /* Typography */
        .main-content h1 {{
            color: {GOLDEN_YELLOW} !important;
            font-family: 'Crimson Text', serif !important;
            font-size: 3rem !important;
            font-weight: 600 !important;
            text-align: center !important;
            margin-bottom: 1rem !important;
            text-shadow: 2px 2px 4px rgba(44, 24, 16, 0.3);
        }}

        .main-content h2, .main-content h3 {{
            color: {DARK_BROWN} !important;
            font-family: 'Crimson Text', serif !important;
            margin-top: 2rem !important;
            margin-bottom: 1rem !important;
        }}

        .main-content p, .main-content div {{
            color: {DARK_BROWN} !important;
            line-height: 1.6 !important;
        }}

        /* Elegant tagline */
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

        /* Radio buttons styling */
        .stRadio > label {{
            color: {DARK_BROWN} !important;
            font-weight: 600 !important;
            font-size: 1.3rem !important;
            font-family: 'Crimson Text', serif !important;
            margin-bottom: 1rem !important;
        }}

        .stRadio > div {{
            background: rgba(139, 111, 71, 0.08);
            padding: 1.2rem;
            border-radius: 15px;
            border: 1px solid rgba(139, 111, 71, 0.15);
            backdrop-filter: blur(3px);
        }}

        .stRadio > div > label {{
            color: {DARK_BROWN} !important;
            font-size: 1.1rem !important;
            font-weight: 500 !important;
        }}

        /* Form elements */
        .stTextInput > label, .stSelectbox > label {{
            color: {DARK_BROWN} !important;
            font-weight: 600 !important;
            font-family: 'Libre Baskerville', serif !important;
        }}

        .stTextInput > div > div > input {{
            background-color: rgba(255, 255, 255, 0.9) !important;
            color: {DARK_BROWN} !important;
            border: 2px solid rgba(212, 175, 55, 0.3) !important;
            border-radius: 8px !important;
        }}

        .stTextInput > div > div > input:focus {{
            border-color: {GOLDEN_YELLOW} !important;
            box-shadow: 0 0 0 2px rgba(212, 175, 55, 0.2) !important;
        }}

        /* Selectbox styling - fix for invisible text */
        .stSelectbox > div > div {{
            background-color: rgba(255, 255, 255, 0.9) !important;
        }}

        .stSelectbox > div > div > div {{
            color: {DARK_BROWN} !important;
        }}

        /* Target the selected value specifically */
        .stSelectbox > div > div > div[data-baseweb="select"] > div {{
            color: {DARK_BROWN} !important;
        }}

        /* Target the dropdown options */
        .stSelectbox > div > div > div[data-baseweb="select"] > div > div {{
            color: {DARK_BROWN} !important;
        }}

        /* Alternative more specific targeting */
        div[data-testid="stSelectbox"] > div > div > div {{
            color: {DARK_BROWN} !important;
        }}

        div[data-testid="stSelectbox"] > div > div > div > div {{
            color: {DARK_BROWN} !important;
        }}

        /* Ensure dropdown menu items are also visible */
        .stSelectbox ul {{
            background-color: rgba(255, 255, 255, 0.95) !important;
        }}

        .stSelectbox ul li {{
            color: {DARK_BROWN} !important;
        }}

        /* More specific selectbox content targeting */
        .stSelectbox div[role="combobox"] {{
            color: {DARK_BROWN} !important;
        }}

        .stSelectbox div[role="combobox"] > div {{
            color: {DARK_BROWN} !important;
        }}

        /* Button styling */
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

        /* Form submit button */
        .stForm .stButton > button {{
            background: linear-gradient(135deg, {GOLDEN_YELLOW} 0%, #B8860B 100%) !important;
            color: white !important;
            width: 100% !important;
            font-size: 1.1rem !important;
        }}

        /* Feature section */
        .feature-section {{
            background: rgba(245, 241, 232, 0.85);
            backdrop-filter: blur(5px);
            padding: 2.5rem;
            border-radius: 20px;
            box-shadow: 0 6px 25px rgba(44, 24, 16, 0.15);
            margin: 2rem auto;
            border: 1px solid rgba(139, 111, 71, 0.15);
            max-width: 1000px;
        }}
        
        .feature-section h3 {{
            color: {GOLDEN_YELLOW} !important;
            font-family: 'Crimson Text', serif !important;
            font-size: 1.5rem !important;
            margin-bottom: 0.8rem !important;
            text-shadow: 1px 1px 2px rgba(44, 24, 16, 0.2);
        }}

        .feature-section p {{
            color: {DARK_BROWN} !important;
            font-size: 1rem !important;
            line-height: 1.6 !important;
        }}

        /* Success/Error messages */
        .stSuccess {{
            background-color: rgba(212, 175, 55, 0.1) !important;
            border: 1px solid {GOLDEN_YELLOW} !important;
            color: {DARK_BROWN} !important;
        }}

        /* Spinner */
        .stSpinner {{
            color: {GOLDEN_YELLOW} !important;
        }}

        /* Remove any remaining white backgrounds */
        .stMarkdown, .stText {{
            background: transparent !important;
        }}

        /* Ensure no white spaces in columns */
        .element-container {{
            background: transparent !important;
        }}

        /* Custom divider */
        hr {{
            border: none !important;
            height: 2px !important;
            background: linear-gradient(90deg, transparent, {GOLDEN_YELLOW}, transparent) !important;
            margin: 2rem 0 !important;
        }}
    </style>
""", unsafe_allow_html=True)

# ===== Sidebar =====
with st.sidebar:
    st.markdown("---")
    if os.path.exists(LOGO_PATH):
        image = Image.open(LOGO_PATH)
        st.image(image, use_container_width=True)

    st.markdown("---")

    # Fixed HTML rendering for sidebar
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
        box-shadow: 0 3px 15px rgba(0, 0, 0, 0.2);
    ">
        At <span style="color: {GOLDEN_YELLOW}; font-weight: bold;">Qahwa</span>, we curate the finest 
        <em>Arabic coffee seeds</em> — like the citrusy 
        <span style="color: {GOLDEN_YELLOW}; font-weight: bold;">Yemeni Mokha</span> — with select blends 
        from Ethiopia and Mexico.
        <br><br>
        Choose from elegant <span style="color: {GOLDEN_YELLOW}; font-weight: bold;">small (100g)</span>, <span style="color: {GOLDEN_YELLOW}; font-weight: bold;">medium (250g)</span>, 
        <span style="color: {GOLDEN_YELLOW}; font-weight: bold;">large (500g)</span>, and 
        <span style="color: {GOLDEN_YELLOW}; font-weight: bold;">extra large (1kg)</span> packs 
        for every brewing mood.
        <br><br>
        Join our 
        <span style="color: #E6D3A3; font-style: italic;">weekend brewing workshops</span> 
        to master the perfect Arabic pour.
    </div>
    """, unsafe_allow_html=True)

# ===== Hero Image Section =====
if os.path.exists(HERO_IMAGE_PATH):
    with open(HERO_IMAGE_PATH, "rb") as img_file:
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
        placeholder="e.g., Tell me about your coffee bean catalog, pricing, or brewing methods...",
        help="Ask us anything about our products, prices, or Arabic coffee!"
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
            • Duration: 2 hours of hands-on brewing experience<br>
            • Available: Friday, Saturday & Sunday<br>
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
            name = st.text_input("Your Name *", help="Enter your full name")
            date = st.selectbox(
                "Select a Date *", 
                valid_dates, 
                format_func=lambda d: d.strftime('%A, %d %B %Y')
            )
        
        with col2:
            email = st.text_input("Your Email *", help="We'll send confirmation here")
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
                st.success(f"🎉 {confirmation}")

st.markdown('</div>', unsafe_allow_html=True)

# ===== Feature Highlights =====
st.markdown("---")

st.markdown('<div class="feature-section">', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🌱 Premium Origins")
    st.markdown("Authentic Arabic coffee sourced directly from the highlands of Yemen, the birthplace of coffee culture, complemented by carefully selected beans from Ethiopia and Mexico.")

with col2:
    st.markdown("### 📦 Perfect Portions")
    st.markdown("From intimate 100g samplers perfect for trying new blends, to generous 1kg bulk packs for the true coffee connoisseur who has found their perfect roast.")

with col3:
    st.markdown("### ☕ Expert Guidance")
    st.markdown("Learn the ancient art of Arabic coffee preparation from master brewers in our immersive weekend workshops, where tradition meets modern technique.")

st.markdown('</div>', unsafe_allow_html=True)