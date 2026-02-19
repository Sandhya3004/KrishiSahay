#!/usr/bin/env python3
"""
KrishiSahay - 3-Page Multilingual App with Dynamic Translation
Uses Google Translate API for on-the-fly translation
"""

import streamlit as st
import sys
import os
from datetime import datetime
import time
from pathlib import Path

# Add utils to path
sys.path.append('utils')

# Import modules
from dynamic_translator import get_translator, translate_text_cached
from rag_engine import RAGEngine
from gemini_llm import GeminiLLM

from weather_agent import WeatherAgent

# Page configuration
st.set_page_config(
    page_title="KrishiSahay",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS (with smaller language cards)
st.markdown("""
<style>
    /* Global styles */
    .stApp {
        background: linear-gradient(135deg, #f8faf8 0%, #e6f3e6 100%);
        font-family: 'Segoe UI', Roboto, sans-serif;
    }
    /* Cards */
    /* Language selection cards */
.lang-card {
    background: white;
    border-radius: 15px;
    padding: 1rem 0.5rem;
    text-align: center;
    box-shadow: 0 5px 15px rgba(0, 40, 0, 0.1);
    transition: transform 0.2s, box-shadow 0.2s;
    cursor: pointer;
    border: 2px solid transparent;
    margin: 0.3rem 0;
}
.lang-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 25px rgba(46, 125, 50, 0.2);
    border-color: #2e7d32;
}
.lang-card.selected {
    border-color: #2e7d32;
    background: #f1f9f1;
}
.lang-flag {
    font-size: 2.5rem;
    margin-bottom: 0.3rem;
}
.lang-name {
    font-size: 1.2rem;
    font-weight: 600;
    color: #1b5e20;
}
.lang-native {
    font-size: 0.9rem;
    color: #666;
    margin-top: 0.2rem;
}
    .card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 8px 20px rgba(0,40,0,0.08);
        margin-bottom: 1.5rem;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 25px rgba(46,125,50,0.15);
    }
    /* Headers */
    h1, h2, h3 {
        color: #1e4a1e;
        font-weight: 600;
    }
    /* Welcome header */
    .welcome-header {
        background: linear-gradient(145deg, #2e7d32, #4caf50);
        color: white;
        padding: 2rem;
        border-radius: 30px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 15px 30px rgba(46,125,50,0.3);
    }
    .welcome-header h1 {
        color: white;
        margin-bottom: 0.5rem;
    }
    .welcome-header p {
        font-size: 1.1rem;
        opacity: 0.9;
    }
    /* Language cards (already in your code) */
    /* Buttons */
    .stButton>button {
        border-radius: 50px !important;
        font-weight: 500 !important;
        padding: 0.6rem 1.5rem !important;
        background: #2e7d32 !important;
        color: white !important;
        border: none !important;
        transition: all 0.2s !important;
    }
    .stButton>button:hover {
        background: #1e5a22 !important;
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(46,125,50,0.3);
    }
    /* Input fields */
    .stTextArea>div>div>textarea, .stTextInput>div>div>input {
        border-radius: 15px !important;
        border: 1px solid #ddd !important;
        padding: 0.75rem !important;
        background: #fafafa;
    }
    /* Info cards (weather, tips) */
    .info-card {
        background: white;
        border-radius: 18px;
        padding: 1.2rem;
        box-shadow: 0 4px 12px rgba(0,20,0,0.05);
        margin: 1rem 0;
        border-left: 5px solid #2e7d32;
    }
    .info-card h4 {
        color: #1e4a1e;
        margin-top: 0;
    }
    /* Answer box */
    .answer-box {
        background: #f0f9f0;
        padding: 1.5rem;
        border-radius: 20px;
        border-left: 6px solid #2e7d32;
        margin: 1.5rem 0;
        box-shadow: 0 5px 15px rgba(0,20,0,0.05);
    }
    /* Quick questions */
    .quick-q-btn {
        background: #e8f5e9;
        border: 1px solid #a5d6a7;
        border-radius: 30px;
        padding: 0.5rem 1rem;
        text-align: center;
        cursor: pointer;
        transition: background 0.2s;
    }
    .quick-q-btn:hover {
        background: #c8e6c9;
    }
    /* Progress steps */
    .progress-step {
        display: inline-block;
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: #ddd;
        color: #666;
        line-height: 38px;
        text-align: center;
        margin: 0 10px;
        font-weight: bold;
    }
    .progress-step.active {
        background: #2e7d32;
        color: white;
    }
    .progress-step.completed {
        background: #4caf50;
        color: white;
    }
    .progress-line {
        width: 80px;
        height: 2px;
        background: #ddd;
        margin: 0 10px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# SESSION STATE INITIALIZATION
# ============================================
if 'page' not in st.session_state:
    st.session_state.page = 1
if 'language' not in st.session_state:
    st.session_state.language = 'en'
if 'farmer_name' not in st.session_state:
    st.session_state.farmer_name = ''
if 'mobile' not in st.session_state:
    st.session_state.mobile = ''
if 'email' not in st.session_state:
    st.session_state.email = ''
if 'state' not in st.session_state:
    st.session_state.state = ''
if 'district' not in st.session_state:
    st.session_state.district = ''
if 'crop' not in st.session_state:
    st.session_state.crop = ''
if 'temp_state' not in st.session_state:
    st.session_state.temp_state = ''  # for dynamic district update

# Weather-related variables
if 'selected_district' not in st.session_state:
    st.session_state.selected_district = "Agra"
if 'selected_crop' not in st.session_state:
    st.session_state.selected_crop = "Wheat"
if 'weather_data' not in st.session_state:
    st.session_state.weather_data = None
if 'current_alerts' not in st.session_state:
    st.session_state.current_alerts = []

# Other UI state
if 'last_response' not in st.session_state:
    st.session_state.last_response = ''
if 'last_question' not in st.session_state:
    st.session_state.last_question = ''
if 'show_answer' not in st.session_state:
    st.session_state.show_answer = False

# ============================================
# INITIALIZE COMPONENTS (cached)
# ============================================
@st.cache_resource
def init_components():
    translator = get_translator()
    rag = RAGEngine()
    llm = GeminiLLM()
    weather = WeatherAgent()
    return translator, rag, llm, weather

translator, rag_engine, llm, weather_agent = init_components()

# ============================================
# HELPER FUNCTIONS
# ============================================
def _(text):
    """Translate text to selected language"""
    if st.session_state.language == 'en' or not text:
        return text
    return translate_text_cached(text, st.session_state.language)

# Language data
LANGUAGES = {
'en': {'name': 'English', 'flag': '🇮🇳'},
'hi': {'name': 'हिन्दी', 'flag': '🇮🇳'},
'te': {'name': 'తెలుగు', 'flag': '🇮🇳'},
'ta': {'name': 'தமிழ்', 'flag': '🇮🇳'},
'kn': {'name': 'ಕನ್ನಡ', 'flag': '🇮🇳'},
'ml': {'name': 'മലയാളം', 'flag': '🇮🇳'},
'bn': {'name': 'বাংলা', 'flag': '🇮🇳'},
'mr': {'name': 'मराठी', 'flag': '🇮🇳'},
'gu': {'name': 'ગુજરાતી', 'flag': '🇮🇳'},
'pa': {'name': 'ਪੰਜਾਬੀ', 'flag': '🇮🇳'},
'or': {'name': 'ଓଡ଼ିଆ', 'flag': '🇮🇳'},
'as': {'name': 'অসমীয়া', 'flag': '🇮🇳'}
}

INDIAN_STATES = [
    "Andhra Pradesh", "Telangana", "Tamil Nadu", "Karnataka", "Kerala",
    "Maharashtra", "Gujarat", "Uttar Pradesh", "Madhya Pradesh", "Bihar",
    "West Bengal", "Punjab", "Haryana", "Rajasthan", "Delhi", "Odisha",
    "Assam", "Jharkhand", "Chhattisgarh", "Himachal Pradesh"
]

STATE_DISTRICTS = {
    "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Kurnool"],
    "Telangana": ["Hyderabad", "Warangal", "Nizamabad", "Karimnagar", "Khammam"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem"],
    "Karnataka": ["Bengaluru", "Mysuru", "Hubballi", "Mangaluru", "Belagavi"],
    "Kerala": ["Thiruvananthapuram", "Kochi", "Kozhikode", "Thrissur", "Kollam"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Agra", "Varanasi", "Meerut"],
    "Madhya Pradesh": ["Bhopal", "Indore", "Jabalpur", "Gwalior", "Ujjain"],
    "Bihar": ["Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Darbhanga"],
    "West Bengal": ["Kolkata", "Howrah", "Darjeeling", "Siliguri", "Durgapur"],
    "Punjab": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda"],
    "Haryana": ["Gurugram", "Faridabad", "Panipat", "Ambala", "Karnal"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Bikaner"],
    "Delhi": ["New Delhi", "North Delhi", "South Delhi", "East Delhi", "West Delhi"],
    "Odisha": ["Bhubaneswar", "Cuttack", "Rourkela", "Puri", "Sambalpur"],
    "Assam": ["Guwahati", "Dibrugarh", "Silchar", "Jorhat", "Tezpur"]
}
# ============================================
# PAGE 1: LANGUAGE SELECTION (with card styling)
# ============================================
if st.session_state.page == 1:
    
    # Progress indicator
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 2rem;">
            <span class="progress-step active">1</span>
            <span class="progress-line"></span>
            <span class="progress-step">2</span>
            <span class="progress-line"></span>
            <span class="progress-step">3</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="color: #2e7d32; font-size: 2.8rem; margin-bottom: 0;">🌾 KrishiSahay</h1>
        <p style="color: #1b5e20; font-size: 1.2rem;">Your AI Farming Assistant</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<h2 style='text-align: center; font-size: 1.8rem;'>{_('Select Your Language')}</h2>", unsafe_allow_html=True)
    
    # Language options – static native names, no translation
    lang_list = [
        ('en', '🇮🇳', 'English', 'English'),
        ('hi', '🇮🇳', 'हिन्दी', 'Hindi'),
        ('te', '🇮🇳', 'తెలుగు', 'Telugu'),
        ('ta', '🇮🇳', 'தமிழ்', 'Tamil'),
        ('kn', '🇮🇳', 'ಕನ್ನಡ', 'Kannada'),
        ('ml', '🇮🇳', 'മലയാളം', 'Malayalam'),
        ('bn', '🇮🇳', 'বাংলা', 'Bengali'),
        ('mr', '🇮🇳', 'मराठी', 'Marathi'),
        ('gu', '🇮🇳', 'ગુજરાતી', 'Gujarati'),
        ('pa', '🇮🇳', 'ਪੰਜਾਬੀ', 'Punjabi'),
        ('or', '🇮🇳', 'ଓଡ଼ିଆ', 'Odia'),
        ('as', '🇮🇳', 'অসমীয়া', 'Assamese')
    ]
    
    # Create rows of 3
    for i in range(0, len(lang_list), 3):
        cols = st.columns(3)
        for j, (code, flag, native, name) in enumerate(lang_list[i:i+3]):
            with cols[j]:
                selected = (st.session_state.language == code)
                # Card HTML
                card_html = f"""
                <div class="lang-card {'selected' if selected else ''}">
                    <div class="lang-flag">{flag}</div>
                    <div class="lang-name">{native}</div>
                    <div class="lang-native">{name}</div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
                # Hidden button to capture selection
                if st.button("Select", key=f"lang_{code}", use_container_width=True):
                    st.session_state.language = code
                    st.rerun()
    
    # Continue button
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button(_("Continue →"), use_container_width=True):
            st.session_state.page = 2
            st.rerun()
# ============================================
# PAGE 2: FARMER REGISTRATION (Immediate District Update, No Callback in Form)
# ============================================
elif st.session_state.page == 2:
    
    # Progress indicator
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 2rem;">
            <span class="progress-step completed">✓</span>
            <span class="progress-line"></span>
            <span class="progress-step active">2</span>
            <span class="progress-line"></span>
            <span class="progress-step">3</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="welcome-header">
        <h1>🌾 {_('Farmer Registration')}</h1>
        <p>{_('Please provide your details to personalize your experience')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize state and district session variables if not present
    if 'selected_state' not in st.session_state:
        st.session_state.selected_state = ''
    if 'selected_district' not in st.session_state:
        st.session_state.selected_district = ''
    
    # --- State and District dropdowns (outside form) ---
    st.markdown("### 📍 " + _("State") + " *")
    state_options = [_("Select a state")] + [_(s) for s in INDIAN_STATES]
    # Determine current index
    if st.session_state.selected_state and st.session_state.selected_state in INDIAN_STATES:
        current_state_index = state_options.index(_(st.session_state.selected_state))
    else:
        current_state_index = 0
        st.session_state.selected_state = ''
    
    selected_state_display = st.selectbox(
        label=_("State"),
        options=state_options,
        index=current_state_index,
        key="state_selector_outside",
        label_visibility="collapsed"
    )
    
    # Update selected_state based on choice
    if selected_state_display != _("Select a state"):
        # Find the English state name
        idx = state_options.index(selected_state_display) - 1
        st.session_state.selected_state = INDIAN_STATES[idx]
    else:
        st.session_state.selected_state = ''
        st.session_state.selected_district = ''  # reset district if state cleared
    
    st.markdown("### 🗺️ " + _("District") + " *")
    if st.session_state.selected_state:
        district_list = STATE_DISTRICTS.get(st.session_state.selected_state, [_("Select a district")] + [f"District {i}" for i in range(1,4)])
    else:
        district_list = [_("Select a state first")]
    
    translated_districts = [_(d) for d in district_list]
    
    # Find index of previously selected district
    district_idx = 0
    if st.session_state.selected_district and st.session_state.selected_district in district_list:
        district_idx = district_list.index(st.session_state.selected_district)
    
    selected_district_display = st.selectbox(
        label=_("District"),
        options=translated_districts,
        index=district_idx,
        key="district_selector_outside",
        disabled=not st.session_state.selected_state,
        label_visibility="collapsed"
    )
    
    # Update selected_district
    if selected_district_display and selected_district_display not in [_("Select a district"), _("Select a state first")]:
        st.session_state.selected_district = district_list[translated_districts.index(selected_district_display)]
    else:
        st.session_state.selected_district = ''
    
    st.markdown("---")
    
    # --- Main form for other fields ---
    with st.form("registration_form"):
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"### 📝 {_('Full Name')} *")
            name = st.text_input(
                label=_("Full Name"),
                placeholder=_("Enter your full name"),
                value=st.session_state.farmer_name,
                key="reg_name",
                label_visibility="collapsed"
            )
            
            st.markdown(f"### 📱 {_('Mobile Number')} *")
            mobile = st.text_input(
                label=_("Mobile Number"),
                placeholder=_("10-digit mobile number"),
                value=st.session_state.mobile,
                max_chars=10,
                key="reg_mobile",
                label_visibility="collapsed"
            )
        
        with col2:
            st.markdown(f"### ✉️ {_('Email')}")
            email = st.text_input(
                label=_("Email"),
                placeholder=_("Optional"),
                value=st.session_state.email,
                key="reg_email",
                label_visibility="collapsed"
            )
            
            st.markdown(f"### 🌾 {_('Main Crop')}")
            crops = ["Wheat", "Rice", "Cotton", "Sugarcane", "Mustard", "Potato", "Maize", "Moong"]
            translated_crops = [_(c) for c in crops]
            selected_crop = st.selectbox(
                label=_("Crop"),
                options=translated_crops,
                key="reg_crop",
                label_visibility="collapsed"
            )
            crop = crops[translated_crops.index(selected_crop)]
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Form buttons
        col1, col2, col3 = st.columns([1,2,1])
        with col1:
            if st.form_submit_button(_("← Back"), use_container_width=True):
                st.session_state.page = 1
                st.rerun()
        with col2:
            submitted = st.form_submit_button(_("Proceed to Dashboard →"), use_container_width=True)
    
    # Handle form submission
    if submitted:
        if not name:
            st.error(_("Please enter your name"))
        elif not mobile or len(mobile) != 10:
            st.error(_("Please enter a valid 10-digit mobile number"))
        elif not st.session_state.selected_state:
            st.error(_("Please select a state"))
        elif not st.session_state.selected_district:
            st.error(_("Please select a valid district"))
        else:
            st.session_state.farmer_name = name
            st.session_state.mobile = mobile
            st.session_state.email = email
            st.session_state.state = st.session_state.selected_state
            st.session_state.district = st.session_state.selected_district
            st.session_state.crop = crop
            st.session_state.selected_district = st.session_state.selected_district
            st.session_state.selected_crop = crop
            st.session_state.page = 3
            st.rerun()
# ============================================
# PAGE 3: MAIN DASHBOARD
# ============================================

else:
    # Welcome header
    st.write(f"Debug: Current language = {st.session_state.language}")  # <-- add this
    st.markdown(f"""
    <div class="welcome-header">
        <h1>🌾 {_('KrishiSahay Dashboard')}</h1>
        <p>{_('Welcome')} {st.session_state.farmer_name} | 
        📍 {_(st.session_state.district)}, {_(st.session_state.state)} | 
        🌾 {_(st.session_state.crop)}</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/india--v1.png", width=80)
        st.markdown(f"### 👤 {st.session_state.farmer_name}")
        st.markdown(f"📱 {st.session_state.mobile}")
        if st.session_state.email:
            st.markdown(f"✉️ {st.session_state.email}")
        st.markdown(f"📍 {_(st.session_state.district)}, {_(st.session_state.state)}")
        st.markdown(f"🌾 {_(st.session_state.crop)}")
        
        st.markdown("---")
        
        # Weather update button
        if st.button(_("🌤️ Update Weather"), use_container_width=True):
            with st.spinner(_("Fetching weather...")):
                weather_data = weather_agent.get_weather(st.session_state.selected_district)
                st.session_state.weather_data = weather_data
                if weather_data and not weather_data.get("error", False):
                    alerts = weather_agent.generate_alerts(weather_data, st.session_state.selected_crop)
                else:
                    alerts = []
                st.session_state.current_alerts = alerts
                st.success(_("Weather updated!"))
        
        # Weather display
        if st.session_state.get('weather_data') and not st.session_state.weather_data.get("error", False):
            w = st.session_state.weather_data
            st.markdown(f"""
            <div class="info-card">
                <h4>{_('Weather Information')}</h4>
                <p>🌡️ {_('Temperature')}: {w['current']['temp']}°C</p>
                <p>💧 {_('Humidity')}: {w['current']['humidity']}%</p>
                <p>💨 {_('Wind')}: {w['current']['wind_speed']} m/s</p>
                <p>☁️ {_('Conditions')}: {_(w['current']['description'])}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info(_("Click 'Update Weather' to see data"))
        
        st.markdown("---")
        if st.button(_("Logout"), use_container_width=True):
            # Clear session keys except page and language
            keep_keys = ['page', 'language']
            for key in list(st.session_state.keys()):
                if key not in keep_keys:
                    del st.session_state[key]
            st.rerun()

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"### 💬 {_('Your Question')}")
        
        # Quick questions
        quick_qs = [_("Pests in mustard?"), _("When to sow moong?"), _("PM Kisan scheme?")]
        quick_cols = st.columns(3)
        for i, (col, q) in enumerate(zip(quick_cols, quick_qs)):
            with col:
                if st.button(q, key=f"quick_{i}", use_container_width=True):
                    st.session_state.quick_query = q
        
        # Question input
        question = st.text_area(
            label=_("Your Question"),
            placeholder=_("e.g., How to control pests in mustard?"),
            height=100,
            key="question_input",
            label_visibility="collapsed"
        )
        
        # Ask button
        if st.button(_("Ask KrishiSahay"), type="primary", use_container_width=True):
            if question:
                with st.spinner(_("Processing your question...")):
                    results = rag_engine.search(question, top_k=3)
                    response = llm.generate_with_retrieval(question, results, target_lang=st.session_state.language)
                    st.session_state.last_response = response
                    st.session_state.last_question = question
                    st.session_state.show_answer = True
        
        # Display answer and listen button
                # Display answer and listen button
        if st.session_state.get('show_answer', False):
            st.markdown(f"### 📋 {_('Answer')}")
            answer_text = st.session_state.last_response  # already in target language
            
            st.markdown(f"""
            <div class="answer-box">
                <b>{_('Your Question')}:</b> {st.session_state.last_question}<br><br>
                <b>{_('Answer')}:</b><br>
                {answer_text}
            </div>
            """, unsafe_allow_html=True)
            
            # Listen button
            if st.button(_("🔊 Listen")):
                if st.session_state.last_response:
                    with st.spinner(_("Generating audio...")):
                        from gtts import gTTS
                        import io
                        import base64
                        # Language code mapping for TTS
                        lang_map = {
                            'en': 'en', 'hi': 'hi', 'te': 'te', 'ta': 'ta', 'kn': 'kn',
                            'ml': 'ml', 'bn': 'bn', 'mr': 'mr', 'gu': 'gu',
                            'pa': 'pa', 'or': 'or', 'as': 'as'
                        }
                        tts_lang = lang_map.get(st.session_state.language, 'hi')
                        # Use the already translated answer text
                        tts = gTTS(text=answer_text, lang=tts_lang, slow=False)
                        fp = io.BytesIO()
                        tts.write_to_fp(fp)
                        fp.seek(0)
                        audio_bytes = fp.read()
                        b64 = base64.b64encode(audio_bytes).decode()
                        audio_html = f"""
                        <audio controls autoplay style="width:100%; margin-top:10px;">
                            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                        </audio>
                        """
                        st.markdown(audio_html, unsafe_allow_html=True)
                else:
                    st.warning(_("No answer to play yet."))

    with col2:
        st.markdown(f"### 🚨 {_('Weather Alerts')}")
        alerts = st.session_state.get('current_alerts', [])
        if alerts:
            for alert in alerts:
                st.warning(alert.get('message', ''))
        else:
            st.info(_("No weather alerts"))
        
        st.markdown(f"### 💡 {_('Farming Tips')}")
        tips = [_("Practice crop rotation"), _("Water in morning/evening"),
                _("Test soil regularly"), _("Use high-yield varieties"),
                _("Use organic pesticides")]
        for tip in tips:
            st.markdown(f"- {tip}")
        
        st.markdown("---")
        st.markdown(f"📞 {_('Kisan Call Center: 1800-180-1551')}")