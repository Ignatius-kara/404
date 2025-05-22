import streamlit as st
import json
import random
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Page configuration
st.set_page_config(
    page_title="RU Mental Health Buddy",
    page_icon="🌟",
    layout="wide"
)

# Custom CSS for retro styling
def load_css():
    st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #FFF8E7 0%, #F5F5DC 100%);
    }
    
    .stApp > header {
        background-color: transparent;
    }
    
    .chat-container {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 3px solid #FF6B35;
    }
    
    .user-message {
        background: linear-gradient(135deg, #4ECDC4 0%, #95E1D3 100%);
        color: white;
        padding: 12px 18px;
        border-radius: 20px 20px 5px 20px;
        margin: 10px 0;
        margin-left: 20%;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .bot-message {
        background: linear-gradient(135deg, #FF6B35 0%, #FFA500 100%);
        color: white;
        padding: 12px 18px;
        border-radius: 20px 20px 20px 5px;
        margin: 10px 0;
        margin-right: 20%;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .title {
        font-family: 'Comic Sans MS', cursive;
        color: #2C3E50;
        text-align: center;
        font-size: 3em;
        margin-bottom: 20px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .subtitle {
        font-family: 'Arial', sans-serif;
        color: #FF6B35;
        text-align: center;
        font-size: 1.2em;
        margin-bottom: 30px;
    }
    
    div.stButton > button {
        background: linear-gradient(135deg, #FF6B35 0%, #FFA500 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 24px;
        font-weight: bold;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# Mental health response database
@st.cache_data
def load_responses():
    return {
        "greetings": [
            "Hello! I'm your mental health buddy here at Redeemers University. How are you feeling today?",
            "Hi there! Welcome to your safe space. What's on your mind?",
            "Hey! I'm here to listen and support you. How can I help you today?"
        ],
        "academic_stress": [
            "I understand exam stress can be overwhelming. Remember, your worth isn't defined by your grades. Have you tried breaking your study sessions into smaller, manageable chunks?",
            "Academic pressure is real, especially at RU. Many students feel this way. Would you like some study techniques that have helped other students?",
            "Feeling stressed about academics is completely normal. Let's talk about some healthy coping strategies you could try."
        ],
        "anxiety": [
            "Anxiety can feel overwhelming, but you're not alone in this. Have you tried any breathing exercises or mindfulness techniques?",
            "Many RU students experience anxiety. It's brave of you to reach out. Would you like me to share some grounding techniques?",
            "Feeling anxious is your mind's way of trying to protect you. Let's work through this together step by step."
        ],
        "loneliness": [
            "Feeling lonely at university is more common than you think. You're not alone in feeling this way. Are there any campus activities that interest you?",
            "Loneliness can be really tough, especially when adjusting to university life. Have you considered joining any student clubs or organizations?",
            "Your feelings are valid. Building connections takes time. Would you like suggestions for meeting like-minded people on campus?"
        ],
        "spiritual": [
            "Spiritual questions and doubts are a natural part of growth. Many RU students navigate similar feelings. Would you like to talk about what's troubling you?",
            "At Redeemers University, we understand the importance of spiritual wellness. It's okay to have questions and seek answers.",
            "Spiritual struggles can feel isolating, but they're often part of a deeper journey. You're in a supportive environment here."
        ],
        "support": [
            "Remember, seeking help is a sign of strength, not weakness. You've taken a brave first step.",
            "You're doing better than you think. Every small step forward counts.",
            "It's okay to not be okay sometimes. What matters is that you're reaching out."
        ],
        "crisis": [
            "I'm concerned about you. Please reach out to the RU Counseling Center immediately at [campus number] or contact emergency services if you're in immediate danger.",
            "Your life has value and meaning. Please connect with professional help right away. The RU Counseling Center is available, or call the Nigeria Suicide Prevention Hotline.",
            "I care about your safety. Please reach out to someone you trust or contact campus security immediately."
        ]
    }

# Simple keyword matching for responses
def get_response_category(user_input):
    user_input = user_input.lower()
    
    if any(word in user_input for word in ['hi', 'hello', 'hey', 'good morning', 'good afternoon']):
        return 'greetings'
    elif any(word in user_input for word in ['exam', 'test', 'study', 'grade', 'academic', 'assignment', 'homework']):
        return 'academic_stress'
    elif any(word in user_input for word in ['anxious', 'anxiety', 'worry', 'worried', 'nervous', 'panic']):
        return 'anxiety'
    elif any(word in user_input for word in ['lonely', 'alone', 'isolated', 'friends', 'social']):
        return 'loneliness'
    elif any(word in user_input for word in ['god', 'faith', 'spiritual', 'pray', 'church', 'believe']):
        return 'spiritual'
    elif any(word in user_input for word in ['kill', 'suicide', 'die', 'death', 'hurt myself', 'end it all']):
        return 'crisis'
    else:
        return 'support'

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'responses' not in st.session_state:
    st.session_state.responses = load_responses()

# App header
load_css()
st.markdown('<p class="title">🌟 RU Mental Health Buddy 🌟</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Your friendly companion at Redeemers University</p>', unsafe_allow_html=True)

# Sidebar with resources
with st.sidebar:
    st.markdown("### 🆘 Emergency Resources")
    st.markdown("""
    **Campus Counseling Center**  
    📞 [Insert RU number]  
    
    **Campus Security**  
    📞 [Insert security number]  
    
    **National Crisis Hotline**  
    📞 +234-XXX-XXXX  
    
    **Emergency Services**  
    📞 199 (Police) / 911 (Medical)
    """)
    
    st.markdown("### 📚 Helpful Resources")
    st.markdown("""
    - [RU Student Support Services](link)
    - [Study Tips & Techniques](link)
    - [Spiritual Life Office](link)
    - [Health & Wellness Center](link)
    """)
    
    st.markdown("### ℹ️ Important Note")
    st.markdown("""
    This chatbot provides peer support and information. 
    It is not a replacement for professional mental health services.
    If you're experiencing a crisis, please contact emergency services immediately.
    """)

# Main chat interface
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display chat history
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-message">{message["content"]}</div>', unsafe_allow_html=True)

# User input
user_input = st.text_input("Share what's on your mind...", key="user_input", placeholder="Type your message here...")

# Process user input
if user_input:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Get response category and generate bot response
    category = get_response_category(user_input)
    bot_response = random.choice(st.session_state.responses[category])
    
    # Add bot response to history
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    
    # Clear input and rerun to show new messages
    st.experimental_rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Quick action buttons
st.markdown("### Quick Help")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("😰 Feeling Anxious"):
        st.session_state.messages.append({"role": "user", "content": "I'm feeling anxious"})
        category = get_response_category("I'm feeling anxious")
        bot_response = random.choice(st.session_state.responses[category])
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        st.experimental_rerun()

with col2:
    if st.button("📚 Study Stress"):
        st.session_state.messages.append({"role": "user", "content": "I'm stressed about exams"})
        category = get_response_category("I'm stressed about exams")
        bot_response = random.choice(st.session_state.responses[category])
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        st.experimental_rerun()

with col3:
    if st.button("😢 Feeling Lonely"):
        st.session_state.messages.append({"role": "user", "content": "I feel lonely"})
        category = get_response_category("I feel lonely")
        bot_response = random.choice(st.session_state.responses[category])
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        st.experimental_rerun()

with col4:
    if st.button("🙏 Spiritual Questions"):
        st.session_state.messages.append({"role": "user", "content": "I have spiritual questions"})
        category = get_response_category("I have spiritual questions")
        bot_response = random.choice(st.session_state.responses[category])
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        st.experimental_rerun()

# Clear conversation button
if st.button("🔄 Start New Conversation"):
    st.session_state.messages = []
    st.experimental_rerun()

# Footer
st.markdown("---")
st.markdown("Made with ❤️ for Redeemers University Students | Remember: You're not alone in this journey!")
