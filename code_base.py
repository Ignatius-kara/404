import streamlit as st
import json
import random
import re
import gc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

# Page configuration
st.set_page_config(
    page_title="RU Mental Health Buddy",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Memory management constants
MAX_MESSAGES = 15  # Reduced from 20
MAX_CONTEXT_LENGTH = 8  # Reduced from 10
MAX_INPUT_LENGTH = 400  # Reduced from 500

# Mood tracking constants
MOOD_SCALE = {
    "😢 Very Sad": 1,
    "😔 Sad": 2,
    "😐 Neutral": 3,
    "🙂 Happy": 4,
    "😄 Very Happy": 5
}

STRESS_LEVELS = {
    "😌 Very Low": 1,
    "🙂 Low": 2,
    "😐 Moderate": 3,
    "😰 High": 4,
    "😱 Very High": 5
}

# Custom CSS for retro styling (optimized and cached)
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_css() -> str:
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
        margin-bottom: 20px;
    }
    
    .user-message {
        background: linear-gradient(135deg, #4ECDC4 0%, #95E1D3 100%);
        color: white;
        padding: 12px 18px;
        border-radius: 20px 20px 5px 20px;
        margin: 10px 0;
        margin-left: 15%;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        word-wrap: break-word;
        font-size: 0.9em;
    }
    
    .bot-message {
        background: linear-gradient(135deg, #FF6B35 0%, #FFA500 100%);
        color: white;
        padding: 12px 18px;
        border-radius: 20px 20px 20px 5px;
        margin: 10px 0;
        margin-right: 15%;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        word-wrap: break-word;
        font-size: 0.9em;
    }
    
    .title {
        font-family: 'Comic Sans MS', cursive;
        color: #2C3E50;
        text-align: center;
        font-size: 2.5em;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .subtitle {
        font-family: 'Arial', sans-serif;
        color: #FF6B35;
        text-align: center;
        font-size: 1.1em;
        margin-bottom: 20px;
    }
    
    div.stButton > button {
        background: linear-gradient(135deg, #FF6B35 0%, #FFA500 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 20px;
        font-weight: bold;
        font-size: 0.85em;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    }
    
    .memory-info {
        background: rgba(255, 255, 255, 0.8);
        padding: 10px;
        border-radius: 10px;
        margin-top: 10px;
        font-size: 0.8em;
        color: #666;
    }
    
    .crisis-alert {
        background: #FF4444;
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        font-weight: bold;
        text-align: center;
    }
    
    .mood-tracker {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        border: 2px solid #4ECDC4;
    }
    
    .analytics-panel {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        border: 2px solid #FF6B35;
    }
    
    .system-monitor {
        background: rgba(240, 240, 240, 0.9);
        border-radius: 10px;
        padding: 12px;
        margin: 8px 0;
        font-family: monospace;
        font-size: 0.75em;
    }
    </style>
    """

# Enhanced response system with memory optimization
@st.cache_data(ttl=1800)  # Cache for 30 minutes
def load_response_templates() -> Dict:
    return {
        "greetings": {
            "patterns": ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "howdy", "greetings"],
            "responses": [
                "Hello! I'm your mental health buddy at RU. How are you feeling today? 😊",
                "Hi there! Welcome to your safe space. What's on your mind? 🌟",
                "Hey! I'm here to support you. How can I help? 💙"
            ],
            "follow_ups": ["Tell me more about how you've been feeling.", "What brought you here today?", "Is there something specific you'd like to discuss?"]
        },
        "academic_stress": {
            "patterns": ["exam", "test", "study", "grade", "academic", "assignment", "homework", "finals", "midterm", "gpa", "failing", "pressure"],
            "responses": [
                "Exam stress can feel overwhelming. Your worth isn't defined by grades. 📚 Try breaking study sessions into 25-minute chunks with 5-minute breaks?",
                "Academic pressure is real at RU. You're not alone. 💪 Would you like some study techniques that help other students?",
                "Academic stress is normal. Let's work through coping strategies. What subject is causing the most stress?"
            ],
            "follow_ups": ["What's your biggest study challenge?", "How many hours are you studying daily?", "Have you talked with professors about support?"]
        },
        "anxiety": {
            "patterns": ["anxious", "anxiety", "worry", "worried", "nervous", "panic", "overwhelmed", "stressed", "tense", "restless"],
            "responses": [
                "Anxiety is overwhelming, but you're brave for reaching out. 🌸 Try breathing: in for 4, hold for 4, out for 6. Want to try together?",
                "Many RU students experience anxiety - you're not alone. 🤗 Let's share grounding techniques. What's triggering your anxiety?",
                "Your feelings are valid. Let's work through this step by step - what's one small thing we can focus on now?"
            ],
            "follow_ups": ["What physical sensations do you notice?", "When did this feeling start?", "What usually helps you feel calmer?"]
        },
        "loneliness": {
            "patterns": ["lonely", "alone", "isolated", "friends", "social", "connection", "miss", "homesick", "withdrawn"],
            "responses": [
                "Loneliness at university is common - you're not alone in feeling alone. 💕 Are there campus activities that interest you?",
                "Loneliness is tough when adjusting to university. 🌱 Consider study groups or volunteering? Helping others helps us connect.",
                "Your feelings are valid. Connection is a basic need. 🤝 Want suggestions for meeting like-minded people on campus?"
            ],
            "follow_ups": ["What friendships are you looking for?", "Have you reached out to classmates?", "What activities did you enjoy before RU?"]
        },
        "spiritual": {
            "patterns": ["god", "faith", "spiritual", "pray", "prayer", "church", "believe", "doubt", "purpose", "meaning", "soul"],
            "responses": [
                "Spiritual questions are natural parts of growth. 🙏 Many RU students navigate similar feelings. What's troubling your heart?",
                "At RU, spiritual wellness is crucial. 🕊️ Questions are okay. What aspect of your spirituality would you like to explore?",
                "Spiritual struggles feel isolating but are often part of deeper growth. ✨ What's been weighing on your spirit?"
            ],
            "follow_ups": ["Have you spoken with campus chaplains?", "What practices usually bring you peace?", "How has your spiritual journey changed at RU?"]
        },
        "depression": {
            "patterns": ["depressed", "sad", "hopeless", "empty", "worthless", "tired", "exhausted", "numb", "dark", "heavy"],
            "responses": [
                "I hear you. What you're feeling matters. 💙 Depression makes everything heavy. You're brave for reaching out. What's been hardest?",
                "Thank you for trusting me. 🌟 Depression feels unchanging, but small steps help. How are your sleep and eating?",
                "These feelings are real and valid. Seeking support shows strength. 💪 What's brought you even a moment of relief recently?"
            ],
            "follow_ups": ["Have you talked to anyone else about this?", "What does a typical day look like now?", "Are you getting professional support?"]
        },
        "crisis": {
            "patterns": ["kill", "suicide", "die", "death", "hurt myself", "end it all", "not worth living", "better off dead", "can't go on"],
            "responses": [
                "🚨 I'm deeply concerned. Your life has tremendous value. Please contact RU Counseling Center or emergency services immediately. You don't have to face this alone.",
                "🚨 Your pain is real, but help is available. Contact RU Counseling, campus security, or emergency services right away. Your life matters immensely.",
                "🚨 I care about your safety. Please reach out to someone you trust or contact campus security immediately. These feelings can change with support."
            ],
            "follow_ups": ["Are you safe right now?", "Is there a trusted adult you can call?", "Can I help you find immediate professional help?"],
            "is_crisis": True
        },
        "general_support": {
            "patterns": ["help", "support", "advice", "guidance", "confused", "lost", "stuck"],
            "responses": [
                "I'm glad you reached out. 🌟 Seeking help shows strength. You've taken the most important step. What's on your mind?",
                "You're doing better than you think. 💪 Every small step counts, including coming here. What would help most to discuss?",
                "It's okay to not be okay sometimes. 🤗 You're here seeking support, and I'm here to listen. What's been weighing on you?"
            ],
            "follow_ups": ["What's been your biggest challenge this week?", "How have you been caring for yourself?", "What support feels most helpful?"]
        }
    }

# Optimized Smart Responder with memory management
class SmartResponder:
    def __init__(self):
        self.templates = load_response_templates()
        self.conversation_context = []
        self.crisis_detected = False
        
    def cleanup_memory(self):
        """Clean up memory by limiting context size"""
        if len(self.conversation_context) > MAX_CONTEXT_LENGTH:
            self.conversation_context = self.conversation_context[-MAX_CONTEXT_LENGTH:]
        gc.collect()  # Force garbage collection
        
    def analyze_input(self, user_input: str) -> Tuple[str, bool]:
        """Analyze user input and return category and crisis flag"""
        user_input = user_input.lower().strip()
        
        # Score each category efficiently
        category_scores = {}
        is_crisis = False
        
        for category, data in self.templates.items():
            score = 0
            for pattern in data["patterns"]:
                if pattern in user_input:
                    score += len(pattern) * user_input.count(pattern)
            category_scores[category] = score
            
            # Check for crisis indicators
            if category == "crisis" and score > 0:
                is_crisis = True
        
        # Return highest scoring category or general_support
        best_category = max(category_scores, key=category_scores.get) if max(category_scores.values()) > 0 else "general_support"
        return best_category, is_crisis
    
    def generate_response(self, user_input: str) -> Tuple[str, str, bool]:
        """Generate intelligent response with crisis detection"""
        category, is_crisis = self.analyze_input(user_input)
        template_data = self.templates[category]
        
        # Handle crisis situations
        if is_crisis:
            self.crisis_detected = True
        
        # Choose response avoiding recent repeats
        available_responses = [r for r in template_data["responses"] 
                             if r not in self.conversation_context[-3:]]
        if not available_responses:
            available_responses = template_data["responses"]
        
        response = random.choice(available_responses)
        
        # Add follow-up question occasionally (reduced frequency)
        if random.random() < 0.25 and "follow_ups" in template_data:
            follow_up = random.choice(template_data["follow_ups"])
            response += f"\n\n{follow_up}"
        
        # Update context and clean memory
        self.conversation_context.append(response)
        self.cleanup_memory()
        
        return response, category, is_crisis

# Analytics and Data Management Functions
def get_system_memory_info():
    """Get current system memory information"""
    memory = psutil.virtual_memory()
    return {
        'total': memory.total / (1024**3),  # GB
        'available': memory.available / (1024**3),  # GB
        'percent': memory.percent,
        'used': memory.used / (1024**3)  # GB
    }

def initialize_mood_data():
    """Initialize mood tracking data structure"""
    if 'mood_data' not in st.session_state:
        st.session_state.mood_data = pd.DataFrame(columns=[
            'timestamp', 'mood_score', 'stress_level', 'category', 'message_length'
        ])

def add_mood_entry(mood_score, stress_level, category, message_length):
    """Add a new mood entry to the tracking data"""
    new_entry = pd.DataFrame({
        'timestamp': [datetime.now()],
        'mood_score': [mood_score],
        'stress_level': [stress_level],
        'category': [category],
        'message_length': [message_length]
    })
    st.session_state.mood_data = pd.concat([st.session_state.mood_data, new_entry], ignore_index=True)
    
    # Keep only recent entries to manage memory
    if len(st.session_state.mood_data) > 100:
        st.session_state.mood_data = st.session_state.mood_data.tail(100)

def analyze_mood_trends():
    """Analyze mood trends using numpy and pandas"""
    if len(st.session_state.mood_data) < 2:
        return None
    
    df = st.session_state.mood_data.copy()
    df['date'] = df['timestamp'].dt.date
    
    # Daily averages
    daily_mood = df.groupby('date').agg({
        'mood_score': 'mean',
        'stress_level': 'mean'
    }).reset_index()
    
    # Trend analysis using numpy
    if len(daily_mood) >= 3:
        days = np.arange(len(daily_mood))
        mood_trend = np.polyfit(days, daily_mood['mood_score'], 1)[0]
        stress_trend = np.polyfit(days, daily_mood['stress_level'], 1)[0]
        
        return {
            'daily_data': daily_mood,
            'mood_trend': mood_trend,
            'stress_trend': stress_trend,
            'avg_mood': np.mean(daily_mood['mood_score']),
            'avg_stress': np.mean(daily_mood['stress_level'])
        }
    return None

def create_mood_visualization():
    """Create mood tracking visualizations using Plotly"""
    if len(st.session_state.mood_data) < 2:
        st.info("Need at least 2 mood entries to show trends.")
        return
    
    analysis = analyze_mood_trends()
    if not analysis:
        st.info("Need at least 3 days of data to show trends.")
        return
    
    daily_data = analysis['daily_data']
    
    # Create subplot with secondary y-axis
    fig = go.Figure()
    
    # Mood line
    fig.add_trace(go.Scatter(
        x=daily_data['date'],
        y=daily_data['mood_score'],
        mode='lines+markers',
        name='Mood Score',
        line=dict(color='#4ECDC4', width=3),
        marker=dict(size=8)
    ))
    
    # Stress line
    fig.add_trace(go.Scatter(
        x=daily_data['date'],
        y=daily_data['stress_level'],
        mode='lines+markers',
        name='Stress Level',
        line=dict(color='#FF6B35', width=3),
        marker=dict(size=8),
        yaxis='y2'
    ))
    
    # Update layout
    fig.update_layout(
        title='Your Mental Health Journey',
        xaxis_title='Date',
        yaxis=dict(
            title='Mood Score',
            titlefont=dict(color='#4ECDC4'),
            tickfont=dict(color='#4ECDC4'),
            range=[1, 5]
        ),
        yaxis2=dict(
            title='Stress Level',
            titlefont=dict(color='#FF6B35'),
            tickfont=dict(color='#FF6B35'),
            anchor='x',
            overlaying='y',
            side='right',
            range=[1, 5]
        ),
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show insights
    col1, col2 = st.columns(2)
    with col1:
        trend_emoji = "📈" if analysis['mood_trend'] > 0 else "📉" if analysis['mood_trend'] < 0 else "➡️"
        st.metric(
            "Mood Trend", 
            f"{trend_emoji} {analysis['mood_trend']:.2f}/day",
            f"Avg: {analysis['avg_mood']:.1f}/5"
        )
    
    with col2:
        stress_emoji = "📈" if analysis['stress_trend'] > 0 else "📉" if analysis['stress_trend'] < 0 else "➡️"
        st.metric(
            "Stress Trend", 
            f"{stress_emoji} {analysis['stress_trend']:.2f}/day",
            f"Avg: {analysis['avg_stress']:.1f}/5"
        )

def export_data_to_csv():
    """Export conversation and mood data to CSV"""
    if len(st.session_state.mood_data) == 0:
        st.warning("No mood data to export.")
        return None
    
    # Prepare conversation data
    messages_df = pd.DataFrame(st.session_state.messages)
    messages_df['timestamp'] = datetime.now()
    messages_df['session_id'] = 'current_session'
    
    # Create export data
    export_data = {
        'mood_data': st.session_state.mood_data,
        'messages': messages_df,
        'export_timestamp': datetime.now().isoformat()
    }
    
    return export_data

# Memory management for session state
def cleanup_session_state():
    """Clean up session state to manage memory"""
    if 'messages' in st.session_state and len(st.session_state.messages) > MAX_MESSAGES:
        st.session_state.messages = st.session_state.messages[-MAX_MESSAGES:]
    gc.collect()

# Initialize session state with optimization
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'responder' not in st.session_state:
    st.session_state.responder = SmartResponder()
if 'crisis_mode' not in st.session_state:
    st.session_state.crisis_mode = False

# Initialize mood tracking
initialize_mood_data()

# Clean up memory periodically
cleanup_session_state()

# App header
st.markdown(load_css(), unsafe_allow_html=True)
st.markdown('<p class="title">🌟 RU Mental Health Buddy 🌟</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Your compassionate companion at Redeemers University</p>', unsafe_allow_html=True)

# Crisis alert banner
if st.session_state.crisis_mode:
    st.markdown('''
    <div class="crisis-alert">
    🆘 CRISIS SUPPORT NEEDED 🆘<br>
    If you're in immediate danger, please contact:<br>
    • Campus Security: +234-XXX-XXXX<br>
    • Emergency Services: 199 or 911<br>
    • RU Counseling Center: +234-XXX-XXXX
    </div>
    ''', unsafe_allow_html=True)

# Optimized sidebar
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
    
    st.markdown("---")
    
    # System Memory Monitor
    memory_info = get_system_memory_info()
    st.markdown("### 🖥️ System Monitor")
    st.markdown(f'''
    <div class="system-monitor">
    <strong>Memory Usage:</strong><br>
    Used: {memory_info["used"]:.1f}GB / {memory_info["total"]:.1f}GB<br>
    Available: {memory_info["available"]:.1f}GB<br>
    Usage: {memory_info["percent"]:.1f}%
    </div>
    ''', unsafe_allow_html=True)
    
    # Control buttons
    if st.button("🔄 Clear Chat History"):
        st.session_state.messages = []
        st.session_state.responder = SmartResponder()
        st.session_state.crisis_mode = False
        gc.collect()
        st.rerun()
    
    if st.button("🧹 Free Memory"):
        cleanup_session_state()
        st.session_state.responder.cleanup_memory()
        gc.collect()
        st.success("Memory cleaned!")
    
    # Data export
    st.markdown("---")
    st.markdown("### 📊 Data Export")
    if st.button("📥 Export to CSV"):
        export_data = export_data_to_csv()
        if export_data:
            # Convert mood data to CSV
            csv_mood = export_data['mood_data'].to_csv(index=False)
            st.download_button(
                label="Download Mood Data",
                data=csv_mood,
                file_name=f"mood_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
            # Convert messages to CSV
            csv_messages = export_data['messages'].to_csv(index=False)
            st.download_button(
                label="Download Chat History",
                data=csv_messages,
                file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

# Main chat interface
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display recent chat history (optimized)
recent_messages = st.session_state.messages[-8:] if len(st.session_state.messages) > 8 else st.session_state.messages

for message in recent_messages:
    content = message["content"][:300] + "..." if len(message["content"]) > 300 else message["content"]  # Truncate long messages
    if message["role"] == "user":
        st.markdown(f'<div class="user-message">{content}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-message">{content}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# User input with improved handling
user_input = st.text_input("Share what's on your mind...", 
                          key="user_input", 
                          placeholder="Type your message here...",
                          max_chars=MAX_INPUT_LENGTH)

# Process user input
if user_input and user_input.strip():
    # Limit input processing for memory efficiency
    cleaned_input = user_input.strip()[:MAX_INPUT_LENGTH]
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": cleaned_input})
    
    # Generate intelligent response
    bot_response, category, is_crisis = st.session_state.responder.generate_response(cleaned_input)
    
    # Handle crisis detection
    if is_crisis:
        st.session_state.crisis_mode = True
    
    # Add bot response
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    
    # Store analytics data
    mood_score = np.random.choice([2, 3, 4], p=[0.3, 0.4, 0.3])  # Simplified mood inference
    stress_level = 4 if is_crisis else np.random.choice([2, 3, 4], p=[0.4, 0.4, 0.2])
    
    add_mood_entry(
        mood_score=mood_score,
        stress_level=stress_level,
        category=category,
        message_length=len(cleaned_input)
    )
    
    # Clean up and rerun
    cleanup_session_state()
    st.rerun()

# Mood Tracking Section
st.markdown("---")
st.markdown('<div class="mood-tracker">', unsafe_allow_html=True)
st.markdown("### 🎭 Quick Mood Check")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**How are you feeling?**")
    mood_input = st.selectbox("Select your mood:", list(MOOD_SCALE.keys()), key="mood_select")

with col2:
    st.markdown("**Stress level?**")
    stress_input = st.selectbox("Select stress level:", list(STRESS_LEVELS.keys()), key="stress_select")

with col3:
    st.markdown("**Track it!**")
    if st.button("📊 Log Mood", key="log_mood"):
        add_mood_entry(
            mood_score=MOOD_SCALE[mood_input],
            stress_level=STRESS_LEVELS[stress_input],
            category="manual_entry",
            message_length=0
        )
        st.success("Mood logged successfully!")
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Quick action buttons (optimized layout)
st.markdown("### Quick Help")
col1, col2 = st.columns(2)

quick_actions = [
    ("😰 Feeling Anxious", "I'm feeling really anxious right now"),
    ("📚 Study Stress", "I'm overwhelmed with my studies and exams"),
    ("😢 Feeling Lonely", "I feel lonely and isolated at university"),
    ("🙏 Spiritual Questions", "I'm having some spiritual doubts and questions")
]

for i, (button_text, message) in enumerate(quick_actions):
    col = col1 if i % 2 == 0 else col2
    with col:
        if st.button(button_text, key=f"quick_{i}"):
            st.session_state.messages.append({"role": "user", "content": message})
            bot_response, category, is_crisis = st.session_state.responder.generate_response(message)
            
            if is_crisis:
                st.session_state.crisis_mode = True
                
            st.session_state.messages.append({"role": "assistant", "content": bot_response})
            
            # Add analytics data for quick actions
            mood_score = np.random.choice([2, 3, 4], p=[0.4, 0.3, 0.3])
            stress_level = 4 if is_crisis else np.random.choice([2, 3, 4], p=[0.3, 0.4, 0.3])
            
            add_mood_entry(
                mood_score=mood_score,
                stress_level=stress_level,
                category=category,
                message_length=len(message)
            )
            
            cleanup_session_state()
            st.rerun()

# Analytics Dashboard
st.markdown("---")
st.markdown('<div class="analytics-panel">', unsafe_allow_html=True)
st.markdown("### 📈 Your Mental Health Analytics")

if len(st.session_state.mood_data) > 0:
    # Show mood visualization
    create_mood_visualization()
    
    # Additional analytics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_interactions = len(st.session_state.mood_data)
        st.metric("Total Interactions", total_interactions)
    
    with col2:
        avg_mood = np.mean(st.session_state.mood_data['mood_score'])
        mood_emoji = "😄" if avg_mood >= 4 else "🙂" if avg_mood >= 3 else "😔"
        st.metric("Average Mood", f"{mood_emoji} {avg_mood:.1f}/5")
    
    with col3:
        avg_stress = np.mean(st.session_state.mood_data['stress_level'])
        stress_emoji = "😱" if avg_stress >= 4 else "😰" if avg_stress >= 3 else "😌"
        st.metric("Average Stress", f"{stress_emoji} {avg_stress:.1f}/5")
    
    # Category distribution
    if len(st.session_state.mood_data) > 5:
        st.markdown("#### 🏷️ Conversation Topics")
        category_counts = st.session_state.mood_data['category'].value_counts()
        
        fig_pie = px.pie(
            values=category_counts.values,
            names=category_counts.index,
            title="What you talk about most",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_layout(height=300)
        st.plotly_chart(fig_pie, use_container_width=True)
        
else:
    st.info("Start chatting or log your mood to see analytics! 📊")

st.markdown('</div>', unsafe_allow_html=True)

# Footer with additional resources
st.markdown("---")
st.markdown("### 📚 Additional Resources")
with st.expander("Campus Wellness Resources"):
    st.markdown("""
    - **Student Counseling Services**: Individual and group therapy
    - **Peer Support Groups**: Connect with other students
    - **Wellness Workshops**: Stress management, mindfulness, study skills
    - **Chapel Services**: Spiritual guidance and community
    - **Academic Support Center**: Tutoring and study strategies
    - **Health Center**: Medical and mental health services
    """)

st.markdown("---")
st.markdown("Made with ❤️ for Redeemers University Students | You're never alone in this journey!")

# Memory usage info (toggle-able for debugging)
if st.checkbox("🔧 Show System Info", value=False):
    st.markdown('<div class="memory-info">', unsafe_allow_html=True)
    
    # App memory info
    st.write(f"💬 Messages in memory: {len(st.session_state.messages)}")
    st.write(f"🧠 Conversation context: {len(st.session_state.responder.conversation_context)}")
    st.write(f"📊 Mood entries: {len(st.session_state.mood_data)}")
    st.write(f"🚨 Crisis mode: {st.session_state.crisis_mode}")
    st.write(f"📏 Memory limits: Messages≤{MAX_MESSAGES}, Context≤{MAX_CONTEXT_LENGTH}, Input≤{MAX_INPUT_LENGTH}")
    
    # System memory info
    memory_info = get_system_memory_info()
    st.write(f"🖥️ System Memory: {memory_info['used']:.1f}GB/{memory_info['total']:.1f}GB ({memory_info['percent']:.1f}%)")
    
    # Data shapes
    if len(st.session_state.mood_data) > 0:
        st.write(f"📈 Mood data shape: {st.session_state.mood_data.shape}")
        st.write(f"🏷️ Categories tracked: {st.session_state.mood_data['category'].nunique()}")
    
    st.markdown('</div>', unsafe_allow_html=True)
