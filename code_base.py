import streamlit as st
import json
import random
import re
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="RU Mental Health Buddy",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for retro styling (optimized)
@st.cache_data
def load_css():
    return """
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
        max-height: 400px;
        overflow-y: auto;
    }
    
    .user-message {
        background: linear-gradient(135deg, #4ECDC4 0%, #95E1D3 100%);
        color: white;
        padding: 12px 18px;
        border-radius: 20px 20px 5px 20px;
        margin: 10px 0;
        margin-left: 20%;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        word-wrap: break-word;
    }
    
    .bot-message {
        background: linear-gradient(135deg, #FF6B35 0%, #FFA500 100%);
        color: white;
        padding: 12px 18px;
        border-radius: 20px 20px 20px 5px;
        margin: 10px 0;
        margin-right: 20%;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        word-wrap: break-word;
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
        width: 100%;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    }
    </style>
    """

# Enhanced response system with context awareness
@st.cache_data
def load_response_templates():
    return {
        "greetings": {
            "patterns": ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "howdy", "greetings"],
            "responses": [
                "Hello! I'm your mental health buddy here at Redeemers University. How are you feeling today? 😊",
                "Hi there! Welcome to your safe space. I'm here to listen - what's on your mind? 🌟",
                "Hey! Great to see you here. I'm ready to support you through whatever you're experiencing. How can I help? 💙"
            ],
            "follow_ups": ["Tell me more about how you've been feeling lately.", "What brought you here today?", "Is there something specific you'd like to talk about?"]
        },
        "academic_stress": {
            "patterns": ["exam", "test", "study", "grade", "academic", "assignment", "homework", "finals", "midterm", "gpa", "failing", "pressure"],
            "responses": [
                "I totally understand - exam stress can feel overwhelming. Remember, your worth isn't defined by your grades. 📚 Have you tried breaking study sessions into 25-minute chunks with 5-minute breaks?",
                "Academic pressure is so real, especially at RU. You're definitely not alone in feeling this way. 💪 Would you like some study techniques that have helped other students manage their workload?",
                "Feeling stressed about academics is completely normal. Let's work through some healthy coping strategies together. What subject or assignment is causing you the most stress right now?"
            ],
            "follow_ups": ["What's your biggest challenge with studying right now?", "How many hours are you currently studying per day?", "Have you spoken with your professors about extensions or support?"]
        },
        "anxiety": {
            "patterns": ["anxious", "anxiety", "worry", "worried", "nervous", "panic", "overwhelmed", "stressed", "tense", "restless"],
            "responses": [
                "Anxiety can feel really overwhelming, but you're incredibly brave for reaching out. 🌸 Let's try a quick breathing exercise: breathe in for 4 counts, hold for 4, out for 6. Want to try it together?",
                "Many RU students experience anxiety - you're not alone in this. 🤗 I'd love to share some grounding techniques that have helped others. Can you tell me what's triggering your anxiety right now?",
                "Your feelings are completely valid. Anxiety is your mind trying to protect you, even if it doesn't feel helpful. Let's work through this step by step - what's one small thing we can focus on right now?"
            ],
            "follow_ups": ["What physical sensations are you noticing?", "When did you first start feeling this way?", "What usually helps you feel calmer?"]
        },
        "loneliness": {
            "patterns": ["lonely", "alone", "isolated", "friends", "social", "connection", "miss", "homesick", "withdrawn"],
            "responses": [
                "Feeling lonely at university is more common than you might think - you're not alone in feeling alone. 💕 Building connections takes time. Are there any campus activities or clubs that spark your interest?",
                "Loneliness can be really tough, especially when adjusting to university life. 🌱 Have you considered joining study groups, student organizations, or even volunteering? Sometimes helping others helps us connect too.",
                "Your feelings are so valid. Connection is a basic human need. 🤝 Would you like some suggestions for meeting like-minded people on campus? Or would you prefer to talk about what's making you feel most isolated?"
            ],
            "follow_ups": ["What kind of friendships are you looking for?", "Have you tried reaching out to classmates?", "What activities did you enjoy before coming to RU?"]
        },
        "spiritual": {
            "patterns": ["god", "faith", "spiritual", "pray", "prayer", "church", "believe", "doubt", "purpose", "meaning", "soul"],
            "responses": [
                "Spiritual questions and doubts are such a natural part of growth. 🙏 Many RU students navigate similar feelings. It's okay to wrestle with big questions - would you like to share what's been troubling your heart?",
                "At Redeemers University, we understand that spiritual wellness is crucial. 🕊️ It's completely okay to have questions and seek answers. What aspect of your faith or spirituality would you like to explore?",
                "Spiritual struggles can feel really isolating, but they're often part of a deeper journey of growth. ✨ You're in such a supportive environment here. What's been weighing on your spirit lately?"
            ],
            "follow_ups": ["Have you spoken with campus chaplains or spiritual advisors?", "What practices usually bring you peace?", "How has your spiritual journey changed since coming to RU?"]
        },
        "depression": {
            "patterns": ["depressed", "sad", "hopeless", "empty", "worthless", "tired", "exhausted", "numb", "dark", "heavy"],
            "responses": [
                "I hear you, and I want you to know that what you're feeling matters. 💙 Depression can make everything feel heavy and exhausting. You've taken a brave step by reaching out. What's been the hardest part lately?",
                "Thank you for trusting me with these feelings. 🌟 When we're depressed, it can feel like nothing will ever change, but small steps can make a difference. How has your sleep and eating been?",
                "These feelings are real and valid. Depression isn't something you can just 'snap out of,' and seeking support shows incredible strength. 💪 What's one tiny thing that's brought you even a moment of relief recently?"
            ],
            "follow_ups": ["Have you been able to talk to anyone else about this?", "What does a typical day look like for you right now?", "Are you getting professional support?"]
        },
        "crisis": {
            "patterns": ["kill", "suicide", "die", "death", "hurt myself", "end it all", "not worth living", "better off dead", "can't go on"],
            "responses": [
                "I'm really concerned about you, and I want you to know that your life has tremendous value. 🆘 Please reach out to the RU Counseling Center immediately or contact emergency services. You don't have to face this alone.",
                "Your pain is real, but there are people who want to help you through this. 💔 Please connect with professional help right away - the RU Counseling Center, campus security, or call emergency services. Your life matters so much.",
                "I care deeply about your safety and wellbeing. 🚨 Please reach out to someone you trust right now, or contact campus security immediately. These feelings can change with proper support."
            ],
            "follow_ups": ["Can you tell me if you're safe right now?", "Is there a trusted adult you can call?", "Would you like me to help you find immediate professional help?"]
        },
        "general_support": {
            "patterns": ["help", "support", "advice", "guidance", "confused", "lost", "stuck"],
            "responses": [
                "I'm so glad you reached out. 🌟 Remember, seeking help is a sign of incredible strength, not weakness. You've already taken the most important step. What's been on your mind?",
                "You're doing better than you think, even if it doesn't feel that way right now. 💪 Every small step forward counts, including coming here today. What would feel most helpful to talk about?",
                "It's completely okay to not be okay sometimes. 🤗 What matters is that you're here, reaching out and looking for support. I'm here to listen - what's been weighing on you?"
            ],
            "follow_ups": ["What's been your biggest challenge this week?", "How have you been taking care of yourself?", "What kind of support feels most helpful to you?"]
        }
    }

# Intelligent response generation
class SmartResponder:
    def __init__(self):
        self.templates = load_response_templates()
        self.conversation_context = []
        
    def analyze_input(self, user_input):
        user_input = user_input.lower().strip()
        
        # Score each category
        category_scores = {}
        for category, data in self.templates.items():
            score = 0
            for pattern in data["patterns"]:
                if pattern in user_input:
                    # Give higher weight to longer, more specific patterns
                    score += len(pattern) * user_input.count(pattern)
            category_scores[category] = score
        
        # Return the category with the highest score, or general_support if no clear match
        if max(category_scores.values()) > 0:
            return max(category_scores, key=category_scores.get)
        return "general_support"
    
    def generate_response(self, user_input, category=None):
        if not category:
            category = self.analyze_input(user_input)
        
        template_data = self.templates[category]
        
        # Choose response based on conversation history
        if len(self.conversation_context) == 0:
            response = random.choice(template_data["responses"])
        else:
            # Avoid repeating recent responses
            available_responses = [r for r in template_data["responses"] 
                                 if r not in self.conversation_context[-3:]]
            if not available_responses:
                available_responses = template_data["responses"]
            response = random.choice(available_responses)
        
        # Add follow-up question 30% of the time
        if random.random() < 0.3 and "follow_ups" in template_data:
            follow_up = random.choice(template_data["follow_ups"])
            response += f"\n\n{follow_up}"
        
        # Update conversation context
        self.conversation_context.append(response)
        if len(self.conversation_context) > 10:  # Keep only recent context
            self.conversation_context = self.conversation_context[-10:]
        
        return response, category

# Initialize session state with memory optimization
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'responder' not in st.session_state:
    st.session_state.responder = SmartResponder()

# Limit message history to prevent memory overflow
MAX_MESSAGES = 20
if len(st.session_state.messages) > MAX_MESSAGES:
    st.session_state.messages = st.session_state.messages[-MAX_MESSAGES:]

# App header
st.markdown(load_css(), unsafe_allow_html=True)
st.markdown('<p class="title">🌟 RU Mental Health Buddy 🌟</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Your compassionate companion at Redeemers University</p>', unsafe_allow_html=True)

# Sidebar with resources (collapsed by default to save space)
with st.sidebar:
    st.markdown("### 🆘 Emergency Resources")
    st.markdown("""
    **Campus Counseling Center**  
    📞 +234-XXX-XXXX  
    
    **Campus Security**  
    📞 +234-XXX-XXXX  
    
    **National Crisis Hotline**  
    📞 +234-XXX-XXXX  
    
    **Emergency Services**  
    📞 199 (Police) / 911 (Medical)
    """)
    
    if st.button("🔄 Clear Chat History"):
        st.session_state.messages = []
        st.session_state.responder = SmartResponder()
        st.rerun()

# Main chat interface
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display recent chat history (limit to save memory)
recent_messages = st.session_state.messages[-10:] if len(st.session_state.messages) > 10 else st.session_state.messages

for message in recent_messages:
    if message["role"] == "user":
        st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-message">{message["content"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# User input with improved handling
user_input = st.text_input("Share what's on your mind...", 
                          key="user_input", 
                          placeholder="Type your message here...",
                          max_chars=500)  # Limit input size

# Process user input
if user_input and user_input.strip():
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input.strip()})
    
    # Generate intelligent response
    bot_response, category = st.session_state.responder.generate_response(user_input)
    
    # Add bot response
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    
    # Rerun to show new messages
    st.rerun()

# Quick action buttons (optimized)
st.markdown("### Quick Help")
col1, col2, col3, col4 = st.columns(4)

quick_actions = [
    ("😰 Feeling Anxious", "I'm feeling really anxious right now"),
    ("📚 Study Stress", "I'm overwhelmed with my studies and exams"),
    ("😢 Feeling Lonely", "I feel lonely and isolated at university"),
    ("🙏 Spiritual Questions", "I'm having some spiritual doubts and questions")
]

for i, (col, (button_text, message)) in enumerate(zip([col1, col2, col3, col4], quick_actions)):
    with col:
        if st.button(button_text, key=f"quick_{i}"):
            st.session_state.messages.append({"role": "user", "content": message})
            bot_response, category = st.session_state.responder.generate_response(message)
            st.session_state.messages.append({"role": "assistant", "content": bot_response})
            st.rerun()

# Footer
st.markdown("---")
st.markdown("Made with ❤️ for Redeemers University Students | You're never alone in this journey!")

# Memory usage info (for debugging - remove in production)
if st.checkbox("Show Debug Info", value=False):
    st.write(f"Messages in memory: {len(st.session_state.messages)}")
    st.write(f"Conversation context: {len(st.session_state.responder.conversation_context)}")
