import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import psutil
import gc
from datetime import datetime, timedelta
import io
from functools import lru_cache
import hashlib
from textblob import TextBlob
from transformers import pipeline
from langdetect import detect
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Mental Health Support Chatbot",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with accessibility improvements
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        color: #ffffff;
        margin-bottom: 2rem;
    }
    .mood-card, .stress-card, .memory-card {
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        color: #ffffff;
        margin: 0.5rem 0;
        border: 2px solid #ffffff;
    }
    .mood-card { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    .stress-card { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
    .memory-card { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        animation: fadeIn 0.5s;
        border: 1px solid #ccc;
    }
    .user-message {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: #ffffff;
    }
    .bot-message {
        background: #f0f2f6;
        color: #262730;
        border-left: 4px solid #667eea;
    }
    .crisis-alert {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        border: 2px solid #ff6b6b;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
        color: #333;
    }
    @keyframes fadeIn {
        from {opacity: 0; transform: translateY(10px);}
        to {opacity: 1; transform: translateY(0);}
    }
    .metric-container {
        display: flex;
        justify-content: space-around;
        margin: 1rem 0;
    }
    .trend-up { color: #28a745; }
    .trend-down { color: #dc3545; }
    .trend-stable { color: #ffc107; }
    /* Accessibility */
    [role="alert"] { outline: 2px solid #000; }
    button, input, select { font-size: 16px; padding: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    defaults = {
        'messages': [],
        'mood_data': pd.DataFrame(columns=['timestamp', 'mood', 'stress', 'category', 'crisis']),
        'conversation_count': 0,
        'user_name': '',
        'current_mood': 3,
        'crisis_detected': False,
        'last_mood_check': None,
        'cache_hits': 0,
        'memory_optimized': False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Memory management and caching
@st.cache_data(ttl=300, max_entries=100)
def get_system_memory_info():
    memory = psutil.virtual_memory()
    return {
        'total': round(memory.total / (1024**3), 2),
        'available': round(memory.available / (1024**3), 2),
        'used': round(memory.used / (1024**3), 2),
        'percent': memory.percent
    }

@lru_cache(maxsize=128)
def hash_text(text):
    return hashlib.md5(text.encode()).hexdigest()

@st.cache_resource
def load_emotion_classifier():
    logger.info("Loading emotion classifier...")
    return pipeline("text-classification", model="distilbert-base-uncased-emotion")

def analyze_emotion(text):
    if not text or len(text.strip()) < 3:
        return 3, 3, False
    try:
        classifier = load_emotion_classifier()
        result = classifier(text)[0]
        emotion = result['label']
        score = result['score']
        
        # Map emotions to mood/stress
        emotion_map = {
            'sadness': (2, 4), 'anger': (2, 4), 'fear': (2, 4),
            'joy': (4, 2), 'love': (4, 2), 'surprise': (3, 3)
        }
        mood, stress = emotion_map.get(emotion, (3, 3))
        
        # Check for crisis
        crisis = detect_crisis(text)
        if crisis:
            mood, stress = 1, 5
        
        return mood, stress, crisis
    except Exception as e:
        logger.error(f"Emotion analysis error: {e}")
        return 3, 3, False

@st.cache_data(ttl=300)
def calculate_trends(mood_data):
    if len(mood_data) < 2:
        return {"mood_trend": "stable", "stress_trend": "stable", "mood_change": 0, "stress_change": 0}
    recent_data = mood_data.tail(10)
    older_data = mood_data.head(max(1, len(mood_data) - 10))
    recent_mood_avg = recent_data['mood'].mean()
    recent_stress_avg = recent_data['stress'].mean()
    older_mood_avg = older_data['mood'].mean()
    older_stress_avg = older_data['stress'].mean()
    mood_change = recent_mood_avg - older_mood_avg
    stress_change = recent_stress_avg - older_stress_avg
    mood_trend = "improving" if mood_change > 0.2 else "declining" if mood_change < -0.2 else "stable"
    stress_trend = "improving" if stress_change < -0.2 else "worsening" if stress_change > 0.2 else "stable"
    return {
        "mood_trend": mood_trend,
        "stress_trend": stress_trend,
        "mood_change": round(mood_change, 2),
        "stress_change": round(stress_change, 2)
    }

@st.cache_data(ttl=300)
def create_mood_chart(mood_data):
    if mood_data.empty:
        return None
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Mood Trends', 'Stress Levels'),
        vertical_spacing=0.1
    )
    fig.add_trace(
        go.Scatter(
            x=mood_data['timestamp'],
            y=mood_data['mood'],
            mode='lines+markers',
            name='Mood',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8)
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=mood_data['timestamp'],
            y=mood_data['stress'],
            mode='lines+markers',
            name='Stress',
            line=dict(color='#f093fb', width=3),
            marker=dict(size=8)
        ),
        row=2, col=1
    )
    # Add crisis annotations
    crisis_entries = mood_data[mood_data['crisis']]
    for _, entry in crisis_entries.iterrows():
        fig.add_annotation(
            x=entry['timestamp'], y=entry['mood'],
            text="⚠️ Crisis",
            showarrow=True, arrowhead=2,
            ax=20, ay=-30,
            row=1, col=1
        )
    fig.update_layout(
        height=500,
        showlegend=True,
        title_text="Mood & Stress Analytics",
        title_x=0.5
    )
    fig.update_xaxes(title_text="Time")
    fig.update_yaxes(title_text="Mood (1-5)", row=1, col=1)
    fig.update_yaxes(title_text="Stress (1-5)", row=2, col=1)
    return fig

@st.cache_data(ttl=600)
def create_category_chart(mood_data):
    if mood_data.empty:
        return None
    category_counts = mood_data['category'].value_counts()
    fig = px.pie(
        values=category_counts.values,
        names=category_counts.index,
        title="Conversation Topics Distribution",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    return fig

def optimize_memory():
    if not st.session_state.get('memory_optimized', False):
        if len(st.session_state.mood_data) > 100:
            st.session_state.mood_data = st.session_state.mood_data.tail(100).reset_index(drop=True)
        if len(st.session_state.messages) > 50:
            st.session_state.messages = st.session_state.messages[-50:]
        gc.collect()
        memory_info = get_system_memory_info()
        if memory_info['percent'] > 80:
            st.cache_data.clear()
            st.session_state.cache_hits = 0
        st.session_state.memory_optimized = True
        logger.info("Memory optimized")

def categorize_conversation(message):
    categories = {
        'anxiety': ['anxious', 'worry', 'nervous', 'panic', 'fear'],
        'depression': ['sad', 'depressed', 'hopeless', 'empty', 'worthless'],
        'stress': ['stress', 'pressure', 'overwhelm', 'burden', 'exhausted'],
        'relationships': ['relationship', 'family', 'friends', 'partner', 'social'],
        'work': ['work', 'job', 'career', 'boss', 'colleague'],
        'self_forgiveness': ['forgive myself', 'guilt', 'shame', 'regret'],
        'identity': ['myself', 'who am i', 'not myself', 'authenticity'],
        'existential': ['meaning', 'purpose', 'why am i here', 'life'],
        'general': []
    }
    message_lower = message.lower()
    for category, keywords in categories.items():
        if any(keyword in message_lower for keyword in keywords):
            return category
    return 'general'

def detect_crisis(message):
    crisis_keywords = [
        'suicide', 'kill myself', 'end it all', 'not worth living',
        'better off dead', 'want to die', 'end my life', 'hurt myself',
        'self harm', 'cut myself', 'overdose', 'jumping'
    ]
    return any(keyword in message.lower() for keyword in crisis_keywords)

def map_document_emotion_to_scores(emotion):
    emotion_map = {
        'grief': (2, 4), 'shame': (2, 4), 'fear': (2, 4),
        'confusion': (3, 3), 'resentment': (2, 4), 'uncertainty': (3, 3)
    }
    return emotion_map.get(emotion.lower(), (3, 3))

def map_document_intent_to_category(intent):
    intent_map = {
        'self_compassion': 'self_forgiveness',
        'identity_exploration': 'identity',
        'relationship_dynamics': 'relationships',
        'boundaries_setting': 'relationships',
        'existential_questions': 'existential',
        'trauma_processing': 'depression'
    }
    return intent_map.get(intent.lower(), 'general')

def load_document_data():
    # Sample document data (replace with actual file loading)
    sample_document = [
        {"user_message": "I don’t know how to forgive myself", "emotion": "shame", "intent": "self_compassion", "chatbot_response": "It’s okay to feel this way. Can you share what makes forgiveness feel so hard?"},
        {"user_message": "Why do I sabotage my closest relationships?", "emotion": "grief", "intent": "relationship_dynamics", "chatbot_response": "That sounds really tough. Can we explore a moment when this happened?"},
        {"user_message": "Sometimes I dey wonder if this life get any meaning", "emotion": "uncertainty", "intent": "existential_questions", "chatbot_response": "Na deep question. Wetin dey make you feel say life no get meaning now?"}
    ]
    try:
        for entry in sample_document:
            user_message = entry['user_message']
            mood, stress = map_document_emotion_to_scores(entry['emotion'])
            category = map_document_intent_to_category(entry['intent'])
            crisis = detect_crisis(user_message)
            log_mood_data(mood, stress, category, crisis)
            st.session_state.messages.append({"role": "user", "content": user_message})
            st.session_state.messages.append({"role": "assistant", "content": entry['chatbot_response']})
        logger.info("Document data loaded successfully")
    except Exception as e:
        logger.error(f"Error loading document data: {e}")

@lru_cache(maxsize=256)
def get_dynamic_response(message, mood_score, stress_score, category):
    st.session_state.cache_hits += 1
    trends = calculate_trends(st.session_state.mood_data)
    
    # Crisis response
    crisis_response = """🚨 **CRISIS SUPPORT RESOURCES** 🚨

I'm very concerned about what you've shared. Please know that you matter:

**Immediate Help:**
• **Counselling numbers: +2348060623184, +2348139121197**
• **Crisis Text Line: Text HOME to 741741**
• **Redeemers University security Services: call & text Vincent at +2348032116599**

**Online Resources:**
• **SAMHSA: 1-800-662-4357**
• **Crisis Chat: suicidepreventionlifeline.org**

Please reach out for help—you are not alone."""

    if detect_crisis(message):
        return crisis_response
    
    # Personalized recommendations
    if trends['stress_trend'] == 'worsening' and stress_score >= 4:
        return "I notice you've been feeling stressed lately. Would you like to try a guided breathing exercise? Inhale for 4 counts, hold for 4, exhale for 6."
    if trends['mood_trend'] == 'declining' and mood_score <= 2:
        return "It seems things have been tough lately. Would you like to share one thing that’s been weighing on you, or try a small self-care activity?"
    
    # Localization for Nigerian Pidgin
    try:
        lang = detect(message)
        if lang == 'pcm':
            pidgin_responses = {
                'self_forgiveness': "E hard to forgive yourself sometimes, I sabi. Wetin dey make you feel say you no fit let go?",
                'relationships': "Relationship wahala no easy. You don try talk wetin dey your mind with dem?",
                'existential': "Na deep question be dis. Wetin dey make you feel say life no get meaning now?",
                'general': "Na true talk, I dey feel you. Wetin dey worry you? Make we yarn small."
            }
            return pidgin_responses.get(category, "I dey here for you. Wetin dey happen?")
    except:
        pass
    
    # Mock LLM response (replace with actual xAI Grok API call)
    base_responses = {
        'anxiety': [
            "I understand you're feeling anxious. Let's try some grounding: name 5 things you can see right now.",
            "Anxiety can feel heavy. What’s one small thing that helps you feel calmer?",
            "Breathe with me: inhale for 4, hold for 4, exhale for 6. Want to try again?"
        ],
        'depression': [
            "I hear you’re struggling. Your feelings are valid, and it’s okay to take it one step at a time.",
            "Depression can make things feel dark. Have you found anything that brings a bit of light?",
            "You’re not alone in this. Would you like to share more or try a small activity?"
        ],
        'self_forgiveness': [
            "Forgiving yourself is hard but possible. What’s one thing you’re holding onto that feels heavy?",
            "It’s okay to feel guilt, but you deserve compassion too. Can we explore this together?",
            "What would forgiving yourself look like for you? Let’s start small."
        ],
        'identity': [
            "Feeling disconnected from yourself is tough. What does being ‘you’ mean to you?",
            "It’s okay to explore who you are. Is there a moment when you felt truly yourself?",
            "Let’s try this: what’s one value that feels important to you right now?"
        ],
        'existential': [
            "Wondering about life’s meaning is deep. What matters most to you right now?",
            "It’s okay to feel uncertain. Have you found anything that gives you a sense of purpose?",
            "Let’s explore: what’s one small thing that feels meaningful to you today?"
        ]
    }
    
    responses = base_responses.get(category, [
        "Thanks for sharing. I’m here to listen—want to tell me more?",
        "I appreciate you opening up. What’s on your mind right now?",
        "You’ve got a lot going on. What would help you most today?"
    ])
    
    response_idx = 0 if mood_score <= 2 or stress_score >= 4 else 2 if mood_score >= 4 and stress_score <= 2 else 1
    return responses[response_idx]

def log_mood_data(mood, stress, category, crisis=False):
    new_entry = pd.DataFrame({
        'timestamp': [datetime.now()],
        'mood': [mood],
        'stress': [stress],
        'category': [category],
        'crisis': [crisis]
    })
    st.session_state.mood_data = pd.concat([st.session_state.mood_data, new_entry], ignore_index=True)
    if len(st.session_state.mood_data) % 10 == 0:
        optimize_memory()

def export_data_as_csv(data, filename_prefix):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.csv"
    csv_buffer = io.StringIO()
    data.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue(), filename

# Main application
def main():
    initialize_session_state()
    
    # Load document data once
    if not st.session_state.mood_data.empty:
        load_document_data()
    
    # Header
    st.markdown("""
    <div class="main-header" role="banner">
        <h1>🧠 Mental Health Support Chatbot</h1>
        <p>Your AI companion for mental wellness with advanced analytics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Analytics Dashboard")
        
        memory_info = get_system_memory_info()
        st.markdown(f"""
        <div class="memory-card" role="region" aria-label="System memory">
            <h4>💾 System Memory</h4>
            <p>Used: {memory_info['used']} GB / {memory_info['total']} GB</p>
            <p>Usage: {memory_info['percent']:.1f}%</p>
            <p>Cache Hits: {st.session_state.cache_hits}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.mood_data.empty:
            avg_mood = st.session_state.mood_data['mood'].mean()
            avg_stress = st.session_state.mood_data['stress'].mean()
            trends = calculate_trends(st.session_state.mood_data)
            
            mood_emoji = "😊" if avg_mood >= 4 else "😐" if avg_mood >= 3 else "😔"
            stress_emoji = "😌" if avg_stress <= 2 else "😰" if avg_stress >= 4 else "🤔"
            trend_mood_icon = "📈" if trends['mood_trend'] == 'improving' else "📉" if trends['mood_trend'] == 'declining' else "➡️"
            trend_stress_icon = "📉" if trends['stress_trend'] == 'improving' else "📈" if trends['stress_trend'] == 'worsening' else "➡️"
            
            st.markdown(f"""
            <div class="mood-card" role="region" aria-label="Average mood">
                <h4>{mood_emoji} Average Mood</h4>
                <h2>{avg_mood:.1f}/5</h2>
                <p>{trend_mood_icon} {trends['mood_trend'].title()}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="stress-card" role="region" aria-label="Average stress">
                <h4>{stress_emoji} Average Stress</h4>
                <h2>{avg_stress:.1f}/5</h2>
                <p>{trend_stress_icon} {trends['stress_trend'].title()}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.metric("💬 Total Interactions", len(st.session_state.mood_data))
        
        st.subheader("🎭 Quick Mood Check")
        mood_input = st.selectbox("How are you feeling?", [1, 2, 3, 4, 5], index=2,
                                 format_func=lambda x: f"{x} - {'😢' if x<=2 else '😐' if x==3 else '😊' if x<=4 else '😄'}",
                                 key="mood_select")
        stress_input = st.selectbox("Stress level?", [1, 2, 3, 4, 5], index=2,
                                   format_func=lambda x: f"{x} - {'😌' if x<=2 else '🤔' if x==3 else '😰' if x<=4 else '🤯'}",
                                   key="stress_select")
        
        if st.button("📝 Log Mood"):
            log_mood_data(mood_input, stress_input, 'manual_entry')
            st.success("Mood logged successfully!")
            st.rerun()
        
        st.subheader("📤 Export Data")
        if not st.session_state.mood_data.empty:
            mood_csv, mood_filename = export_data_as_csv(st.session_state.mood_data, "mood_data")
            st.download_button(
                label="📊 Download Mood Data",
                data=mood_csv,
                file_name=mood_filename,
                mime="text/csv",
                key="download_mood"
            )
        
        if st.session_state.messages:
            chat_df = pd.DataFrame([
                {
                    'timestamp': datetime.now() - timedelta(minutes=len(st.session_state.messages)-i),
                    'role': msg['role'],
                    'content': msg['content']
                }
                for i, msg in enumerate(st.session_state.messages)
            ])
            chat_csv, chat_filename = export_data_as_csv(chat_df, "chat_history")
            st.download_button(
                label="💬 Download Chat History",
                data=chat_csv,
                file_name=chat_filename,
                mime="text/csv",
                key="download_chat"
            )
        
        if st.button("🧹 Optimize Memory"):
            optimize_memory()
            st.success("Memory optimized!")
            st.rerun()
        
        if st.button("🗑️ Clear Cache"):
            st.cache_data.clear()
            st.session_state.cache_hits = 0
            st.success("Cache cleared!")
            st.rerun()
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 Chat Interface")
        
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                role = "User" if message["role"] == "user" else "AI Assistant"
                style = "user-message" if message["role"] == "user" else "bot-message"
                st.markdown(f"""
                <div class="chat-message {style}" role="alert" aria-label="{role} message">
                    <strong>{role}:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
        
        if st.session_state.crisis_detected:
            st.markdown("""
            <div class="crisis-alert" role="alert" aria-label="Crisis support">
                <h3>🚨 Crisis Support Resources Available</h3>
                <p>If you're having thoughts of self-harm, please reach out for immediate help.</p>
            </div>
            """, unsafe_allow_html=True)
        
        user_input = st.chat_input("Share what's on your mind...")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            mood_score, stress_score, crisis = analyze_emotion(user_input)
            category = categorize_conversation(user_input)
            if crisis:
                st.session_state.crisis_detected = True
            log_mood_data(mood_score, stress_score, category, crisis)
            ai_response = get_dynamic_response(user_input, mood_score, stress_score, category)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            st.session_state.conversation_count += 1
            st.rerun()
    
    with col2:
        st.subheader("📈 Analytics Visualizations")
        
        if not st.session_state.mood_data.empty:
            mood_chart = create_mood_chart(st.session_state.mood_data)
            if mood_chart:
                st.plotly_chart(mood_chart, use_container_width=True)
            
            if len(st.session_state.mood_data) > 1:
                category_chart = create_category_chart(st.session_state.mood_data)
                if category_chart:
                    st.plotly_chart(category_chart, use_container_width=True)
            
            st.subheader("📋 Recent Mood Entries")
            recent_entries = st.session_state.mood_data.tail(5)
            for _, entry in recent_entries.iterrows():
                mood_emoji = "😊" if entry['mood'] >= 4 else "😐" if entry['mood'] >= 3 else "😔"
                stress_emoji = "😌" if entry['stress'] <= 2 else "😰" if entry['stress'] >= 4 else "🤔"
                crisis_flag = "⚠️" if entry['crisis'] else ""
                st.write(f"{mood_emoji} {stress_emoji} {crisis_flag} {entry['timestamp'].strftime('%H:%M')} - {entry['category']}")
        
        else:
            st.info("Start chatting to see analytics and mood tracking data!")
    
    # Footer
    st.markdown("""
    ---
    <div style="text-align: center; color: #666; padding: 1rem;" role="contentinfo">
        <p>🧠 Mental Health Support Chatbot with Advanced Analytics</p>
        <p>Remember: This AI assistant is not a replacement for professional mental health care.</p>
        <p>💾 Memory optimized • 📊 Real-time analytics • 🗂️ Data export capabilities</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
