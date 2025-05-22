import streamlit as st
import json
import random
import re

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
    
    .warning-box {
        background: #FFE5B4;
        border-left: 5px solid #FF6B35;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# Mental health response database - Embedded directly in code
RESPONSES = {
    "greetings": [
        "Hello! I'm your mental health buddy here at Redeemers University. How are you feeling today? 😊",
        "Hi there! Welcome to your safe space. What's on your mind today?",
        "Hey! I'm here to listen and support you. How can I help you today? 🌟"
    ],
    "academic_stress": [
        "I understand exam stress can be overwhelming. Remember, your worth isn't defined by your grades. Have you tried breaking your study sessions into smaller, manageable chunks? 📚",
        "Academic pressure is real, especially at RU. Many students feel this way. Would you like some study techniques that have helped other students?",
        "Feeling stressed about academics is completely normal. Let's talk about some healthy coping strategies you could try. 💪"
    ],
    "anxiety": [
        "Anxiety can feel overwhelming, but you're not alone in this. Have you tried any breathing exercises or mindfulness techniques? 🧘‍♀️",
        "Many RU students experience anxiety. It's brave of you to reach out. Would you like me to share some grounding techniques?",
        "Feeling anxious is your mind's way of trying to protect you. Let's work through this together step by step. ❤️"
    ],
    "loneliness": [
        "Feeling lonely at university is more common than you think. You're not alone in feeling this way. Are there any campus activities that interest you? 🤝",
        "Loneliness can be really tough, especially when adjusting to university life. Have you considered joining any student clubs or organizations?",
        "Your feelings are valid. Building connections takes time. Would you like suggestions for meeting like-minded people on campus? 🌈"
    ],
    "spiritual": [
        "Spiritual questions and doubts are a natural part of growth. Many RU students navigate similar feelings. Would you like to talk about what's troubling you? 🙏",
        "At Redeemers University, we understand the importance of spiritual wellness. It's okay to have questions and seek answers.",
        "Spiritual struggles can feel isolating, but they're often part of a deeper journey. You're in a supportive environment here. ✨"
    ],
    "support": [
        "Remember, seeking help is a sign of strength, not weakness. You've taken a brave first step. 💙",
        "You're doing better than you think. Every small step forward counts. Keep going! 🌟",
        "It's okay to not be okay sometimes. What matters is that you're reaching out. I'm here for you. 🤗"
    ],
    "crisis": [
        "🚨 I'm very concerned about you. Please reach out to the RU Counseling Center immediately at [+234-XXX-XXXX] or contact emergency services at 199 if you're in immediate danger.",
        "Your life has value and meaning. Please connect with professional help right away. The RU Counseling Center is available, or call emergency services at 199.",
        "I care about your safety. Please reach out to someone you trust or contact campus security immediately at [+234-XXX-XXXX]."
    ],
    "time_management": [
        "Time management is one of the biggest challenges in university! You're not alone in struggling with this. Have you tried using a planner or digital calendar? 📅",
        "Balancing everything can feel impossible sometimes. Would you like some practical time management strategies that other RU students have found helpful?",
        "Feeling overwhelmed by your schedule is totally normal. Let's break down some ways to make it more manageable. ⏰"
    ],
    "financial_stress": [
        "Financial concerns can add so much pressure to university life. Have you looked into the financial aid options available at RU? 💰",
        "Money stress is real and affects many students. Would you like information about scholarships, work-study programs, or budgeting resources?",
        "Financial worries can be overwhelming. Remember that RU has resources to help students in financial need. Let's explore your options. 📊"
    ]
}

# Improved keyword matching with scoring
def get_response_category(user_input):
    user_input = user_input.lower()
    
    # Crisis keywords - highest priority
    crisis_keywords = ['kill', 'suicide', 'die', 'death', 'hurt myself', 'end it all', 'can\'t go on', 'want to die']
    if any(keyword in user_input for keyword in crisis_keywords):
        return 'crisis'
    
    # Greeting keywords
    greeting_keywords = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
    if any(keyword in user_input for keyword in greeting_keywords):
        return 'greetings'
    
    # Academic stress keywords
    academic_keywords = ['exam', 'test', 'study', 'grade', 'academic', 'assignment', 'homework', 'coursework', 'fail', 'failing']
    if any(keyword in user_input for keyword in academic_keywords):
        return 'academic_stress'
    
    # Anxiety keywords
    anxiety_keywords = ['anxious', 'anxiety', 'worry', 'worried', 'nervous', 'panic', 'stress', 'overwhelmed']
    if any(keyword in user_input for keyword in anxiety_keywords):
        return 'anxiety'
    
    # Loneliness keywords
    loneliness_keywords = ['lonely', 'alone', 'isolated', 'friends', 'social', 'miss', 'homesick']
    if any(keyword in user_input for keyword in loneliness_keywords):
        return 'loneliness'
    
    # Spiritual keywords
    spiritual_keywords = ['god', 'faith', 'spiritual', 'pray', 'church', 'believe', 'doubt', 'religion']
    if any(keyword in user_input for keyword in spiritual_keywords):
        return 'spiritual'
    
    # Time management keywords
    time_keywords = ['time', 'schedule', 'busy', 'manage', 'organize', 'procrastinate']
    if any(keyword in user_input for keyword in time_keywords):
        return 'time_management'
    
    # Financial keywords
    financial_keywords = ['money', 'financial', 'fees', 'cost', 'expensive', 'afford', 'broke']
    if any(keyword in user_input for keyword in financial_keywords):
        return 'financial_stress'
    
    # Default to support
    return 'support'

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
    # Add welcome message
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "Hello! I'm your mental health buddy here at Redeemers University. I'm here to listen, support, and help you navigate any challenges you're facing. How are you feeling today? 😊"
    })

# App header
load_css()
st.markdown('<p class="title">🌟 RU Mental Health Buddy 🌟</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Your friendly companion at Redeemers University</p>', unsafe_allow_html=True)

# Sidebar with resources
with st.sidebar:
    st.markdown("### 🆘 Emergency Resources")
    st.markdown("""
    **RU Counseling Center**  
    📞 +234-XXX-XXXX  
    ⏰ Mon-Fri, 8AM-5PM
    
    **Campus Security**  
    📞 +234-XXX-XXXX  
    ⏰ 24/7 Emergency Line
    
    **National Crisis Hotline**  
    📞 +234-XXX-XXXX  
    ⏰ 24/7 Support
    
    **Emergency Services**  
    📞 199 (Police) / 911 (Medical)
    """)
    
    st.markdown("### 📚 Helpful Resources")
    st.markdown("""
    - [RU Student Support Services](#)
    - [Study Tips & Techniques](#)
    - [Spiritual Life Office](#)
    - [Health & Wellness Center](#)
    - [Financial Aid Office](#)
    """)
    
    st.markdown("### ℹ️ Important Note")
    st.markdown("""
    <div class="warning-box">
    <strong>⚠️ Disclaimer:</strong><br>
    This chatbot provides peer support and information. 
    It is NOT a replacement for professional mental health services.
    If you're experiencing a crisis, please contact emergency services immediately.
    </div>
    """, unsafe_allow_html=True)

# Main chat interface
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display chat history
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-message">{message["content"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# User input
user_input = st.text_input("Share what's on your mind...", key="user_input", placeholder="Type your message here... 💭")

# Process user input
if user_input and user_input.strip():
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Get response category and generate bot response
    category = get_response_category(user_input)
    bot_response = random.choice(RESPONSES[category])
    
    # Add contextual follow-up for certain categories
    if category == 'crisis':
        bot_response += "\n\n🔗 **Immediate Resources:**\n- RU Counseling: +234-XXX-XXXX\n- Emergency: 199\n- Campus Security: +234-XXX-XXXX"
    elif category == 'academic_stress':
        bot_response += "\n\n💡 **Quick Tip:** Try the Pomodoro Technique - 25 min study, 5 min break!"
    elif category == 'anxiety':
        bot_response += "\n\n🧘‍♀️ **Try this:** Take 5 deep breaths - in for 4, hold for 4, out for 6."
    
    # Add bot response to history
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    
    # Rerun to show new messages
    st.rerun()

# Quick action buttons
st.markdown("### Quick Help Topics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("😰 Feeling Anxious"):
        st.session_state.messages.append({"role": "user", "content": "I'm feeling anxious"})
        category = get_response_category("I'm feeling anxious")
        bot_response = random.choice(RESPONSES[category]) + "\n\n🧘‍♀️ **Try this:** Take 5 deep breaths - in for 4, hold for 4, out for 6."
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        st.rerun()

with col2:
    if st.button("📚 Study Stress"):
        st.session_state.messages.append({"role": "user", "content": "I'm stressed about studying"})
        category = get_response_category("I'm stressed about studying")
        bot_response = random.choice(RESPONSES[category]) + "\n\n💡 **Quick Tip:** Try the Pomodoro Technique - 25 min study, 5 min break!"
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        st.rerun()

with col3:
    if st.button("😢 Feeling Lonely"):
        st.session_state.messages.append({"role": "user", "content": "I feel lonely"})
        category = get_response_category("I feel lonely")
        bot_response = random.choice(RESPONSES[category])
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        st.rerun()

with col4:
    if st.button("🙏 Spiritual Questions"):
        st.session_state.messages.append({"role": "user", "content": "I have spiritual questions"})
        category = get_response_category("I have spiritual questions")
        bot_response = random.choice(RESPONSES[category])
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        st.rerun()

# Additional quick buttons
col5, col6, col7, col8 = st.columns(4)

with col5:
    if st.button("⏰ Time Management"):
        st.session_state.messages.append({"role": "user", "content": "I struggle with time management"})
        category = get_response_category("I struggle with time management")
        bot_response = random.choice(RESPONSES[category])
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        st.rerun()

with col6:
    if st.button("💰 Financial Stress"):
        st.session_state.messages.append({"role": "user", "content": "I'm worried about money"})
        category = get_response_category("I'm worried about money")
        bot_response = random.choice(RESPONSES[category])
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        st.rerun()

with col7:
    if st.button("🔄 Start Over"):
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "Hello! I'm your mental health buddy here at Redeemers University. I'm here to listen, support, and help you navigate any challenges you're facing. How are you feeling today? 😊"
        })
        st.rerun()

with col8:
    if st.button("📞 Get Help Now"):
        st.session_state.messages.append({"role": "user", "content": "I need help right now"})
        bot_response = "🆘 **I'm here for you.** If this is an emergency, please contact:\n\n📞 **RU Counseling Center:** +234-XXX-XXXX\n📞 **Campus Security:** +234-XXX-XXXX\n📞 **Emergency Services:** 199\n\nYou're not alone in this. Professional help is available. ❤️"
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        st.rerun()

# Footer with additional info
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
<p><strong>Made with ❤️ for Redeemers University Students</strong></p>
<p>Remember: You're not alone in this journey! 🌟</p>
<p><em>This bot is available 24/7, but for emergencies, always contact professional services.</em></p>
</div>
""", unsafe_allow_html=True)

# Analytics (optional - for your tracking)
if 'conversation_count' not in st.session_state:
    st.session_state.conversation_count = 0

if len(st.session_state.messages) > 2:  # More than just welcome message
    st.session_state.conversation_count += 1
