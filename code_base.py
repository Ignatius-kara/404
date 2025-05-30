import streamlit as st
import pandas as pd
import numpy as np
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
except ImportError:
    px = None
    go = None
    make_subplots = None
import psutil
import gc
import logging
from datetime import datetime, timedelta
import io
from functools import lru_cache
import hashlib
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None
try:
    from textblob import TextBlob
except ImportError:
    TextBlob = None
try:
    from transformers import pipeline
    import torch
except ImportError:
    pipeline = None
    torch = None
try:
    from langdetect import detect
except ImportError:
    detect = None

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Mental Health Support Chatbot",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
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
    .memory-card { background: linear-gradient(45deg, #43e97b 0%, #38f9d7 100%); }
    .chat-message {
        padding: 1rem;
        border-radius: 4px;
        margin: 0.5rem 0;
        animation: fadeIn 0.5s;
    }
    .user-message {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: #ffffff;
    }
    .bot-message {
        background: #f0f2f6;
        color: #333;
        border-left: 4px solid #667eea;
    }
    .crisis-alert {
        background: linear-gradient(45deg, #ff9a9e 0%, #fecfef 100%);
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
        'crisis_detected': False,
        'cache_hits': 0,
        'memory_optimized': False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Memory and caching
@st.cache_data(ttl=300, max_entries=100)
def get_system_memory_info():
    try:
        memory = psutil.virtual_memory()
        return {
            'total': round(memory.total / (1024**3), 2),
            'available': round(memory.available / (1024**3), 2),
            'used': round(memory.used / (1024**3), 2),
            'percent': memory.percent
        }
    except Exception as e:
        logger.error(f"Memory info error: {e}")
        return {'total': 0, 'available': 0, 'used': 0, 'percent': 0}

@lru_cache(maxsize=128)
def hash_text(text):
    return hashlib.md5(text.encode()).hexdigest()

@st.cache_resource
def load_emotion_classifier():
    if pipeline is None or torch is None:
        logger.warning("Transformers or torch not available; using fallback")
        return None
    logger.info("Loading emotion classifier...")
    try:
        return pipeline("text-classification", model="distilbert-base-uncased-emotion", device_map="auto")
    except Exception as e:
        logger.error(f"Classifier load error: {e}")
        return None

def analyze_emotion(text):
    if not text or len(text.strip()) < 3:
        return 3, 3, False
    try:
        classifier = load_emotion_classifier()
        if classifier:
            result = classifier(text)[0]
            emotion = result['label']
            emotion_map = {
                'sadness': (2, 4), 'anger': (2, 4), 'fear': (2, 4),
                'joy': (4, 2), 'love': (4, 2), 'surprise': (3, 3)
            }
            mood, stress = emotion_map.get(emotion, (3, 3))
        elif TextBlob:
            blob = TextBlob(text.lower())
            polarity = blob.sentiment.polarity
            mood = max(1, min(5, int((polarity + 1) * 2 + 1)))
            stress = 3
            if polarity < -0.3:
                stress = 4
            elif polarity > 0.3:
                stress = 2
        else:
            mood, stress = 3, 3
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
    if px and go and make_subplots:
        fig = make_subplots(rows=2, cols=1, subplot_titles=('Mood Trends', 'Stress Levels'))
        fig.add_trace(go.Scatter(x=mood_data['timestamp'], y=mood_data['mood'], mode='lines+markers', name='Mood', line=dict(color='#667eea')), row=1, col=1)
        fig.add_trace(go.Scatter(x=mood_data['timestamp'], y=mood_data['stress'], mode='lines+markers', name='Stress', line=dict(color='#f093fb')), row=2, col=1)
        crisis_entries = mood_data[mood_data['crisis']]
        for _, entry in crisis_entries.iterrows():
            fig.add_annotation(x=entry['timestamp'], y=entry['mood'], text="⚠️ Crisis", showarrow=True, arrowhead=2, row=1, col=1)
        fig.update_layout(height=500, showlegend=True, title_text="Mood & Stress Analytics", title_x=0.5)
        fig.update_xaxes(title_text="Time")
        fig.update_yaxes(title_text="Mood (1-5)", row=1, col=1)
        fig.update_yaxes(title_text="Stress (1-5)", row=2, col=1)
        return fig
    elif plt:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        ax1.plot(mood_data['timestamp'], mood_data['mood'], 'b-o', label='Mood')
        ax1.set_title('Mood Trends')
        ax1.set_ylabel('Mood (1-5)')
        ax2.plot(mood_data['timestamp'], mood_data['stress'], 'm-o', label='Stress')
        ax2.set_title('Stress Levels')
        ax2.set_ylabel('Stress (1-5)')
        ax2.set_xlabel('Time')
        plt.tight_layout()
        return fig
    else:
        logger.warning("No plotting library available")
        return None

@st.cache_data(ttl=600)
def create_category_chart(mood_data):
    if mood_data.empty:
        return None
    category_counts = mood_data['category'].value_counts()
    if px:
        fig = px.pie(values=category_counts.values, names=category_counts.index, title="Conversation Topics")
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        return fig
    elif plt:
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(category_counts.values, labels=category_counts.index, autopct='%1.1f%%')
        ax.set_title('Conversation Topics')
        return fig
    else:
        logger.warning("No plotting library available")
        return None

def optimize_memory():
    if not st.session_state.get('memory_optimized', False):
        if len(st.session_state.mood_data) > 100:
            st.session_state.mood_data = st.session_state.mood_data.tail(100).reset_index(drop=True)
        if len(st.session_state.messages) > 50:
            st.session_state.messages = st.session_state.messages[-50:]
        gc.collect()
        st.session_state.memory_optimized = True
        logger.info("Memory optimized")

def categorize_conversation(message):
    categories = {
        'anxiety': ['anxious', 'worry', 'nervous', 'panic', 'fear'],
        'depression': ['sad', 'depressed', 'hopeless', 'empty', 'worthless'],
        'stress': ['stress', 'pressure', 'overwhelm', 'burden', 'exhausted'],
        'relationships': ['relationship', 'family', 'friends', 'partner', 'social'],
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
    crisis_keywords = ['suicide', 'kill myself', 'end it all', 'not worth living', 'want to die', 'hurt myself']
    return any(keyword in message.lower() for keyword in crisis_keywords)

def map_document_emotion_to_scores(emotion):
    emotion_map = {'grief': (2, 4), 'shame': (2, 4), 'fear': (2, 4), 'confusion': (3, 3), 'resentment': (2, 4), 'uncertainty': (3, 3)}
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
    sample_document = [
        {"user_message": "I don’t know how to forgive myself", "emotion": "shame", "intent": "self_compassion", "chatbot_response": "It’s okay to feel this way. What makes forgiveness hard?"},
        {"user_message": "Why do I sabotage my closest relationships?", "emotion": "grief", "intent": "relationship_dynamics", "chatbot_response": "That sounds tough. Can we explore a moment when this happened?"},
        {"user_message": "Sometimes I dey wonder if this life get any meaning", "emotion": "uncertainty", "intent": "existential_questions", "chatbot_response": "Na deep question. Wetin dey make you feel so?"}
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
        logger.info("Document data loaded")
    except Exception as e:
        logger.error(f"Document load error: {e}")

@lru_cache(maxsize=512)
def get_dynamic_response(user_input, mood_score, stress_score, category):
    st.session_state.cache_hits += 1
    trends = calculate_trends(st.session_state.mood_data)
    
    crisis_response = """
    🚨 **CRISIS SUPPORT** 🚨🚖
    Please know you're not alone:
    • **Counselling: +2348060623184, +2348139121197**

    • **Redeemers University Security: +2348032116599**
  
    Reach out—you’re valued.
    """
    
    if detect_crisis(user_input):
        return crisis_response
    
    if trends['stress_trend'] == 'worsening' and stress_score >= 4:
        return "You've been really stressed lately. Try this breathing exercise: inhale for 4 counts, hold for 4, exhale for 6. Want to try it again?"
    if trends['mood_trend'] == 'declining' and mood_score <= 2:
        return "Things seem tough. Want to share what's weighing on you?"
    
    if detect and detect_language(user_input) == 'pcm':
        pidgin_responses = {
            'self_forgiveness': "E hard to forgive yourself, I sabi. Wetin dey hold you?",
            'relationships': "Relationship wahala no easy. You don yarn with dem?",
            'existential': "Na deep talk. Wetin dey make you feel life no get meaning?",
            'general': "I dey feel you. Wetin dey what's up?"
        }
        return pidgin_response.get(category, "I dey here for you. Let's talk.")
    
    base_responses = {
        'self_forgiveness': ["Forgiving yourself is tough. What's one thing you’re holding onto?", "You deserve kindness. Can we explore this together?"],
        'identity': ["Feeling like you’re not yourself is hard. What does ‘you’ feel like?", "Let’s explore: what’s one value important to you?"],
        'existential': ["Wondering about life’s meaning is deep. What matters to you now?", "What’s one small thing that feels meaningful today?"]
        
    }
    responses = base_response.get(category, ["Thanks for sharing. Want to tell me more?", "I’m here for you. What’s on your mind?"])
    return responses[0] if mood_score <= 2 or stress_score >= 4 else responses[1]

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

def main():
    initialize_session_state()
    if not st.session_state.mood_data.empty:
        load_document_data()
    
    st.markdown("""
    <div class="main-header" role="banner">
        <h1>💬 Mental Health Support Chatbot</h1>
        <p>Your AI companion for mental wellness</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("📊 Dashboard")
        memory_info = get_system_memory_info()
        st.markdown(f"""
        <div class="memory-card" role="region" aria-label="System memory">
            <h4>💾 Memory</h4>
            <p>Used: {memory_info['used']} GB / {memory_info['total']} GB</p>
            <p>Usage: {memory_info['percent']:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.mood_data.empty:
            avg_mood = st.session_state.mood_data['mood'].mean()
            avg_stress = st.session_state.mood_data['stress'].mean()
            trends = calculate_trends(st.session_state.mood_data)
            mood_emoji = "😊" if avg_mood >= 4 else "😐" if avg_mood >= 3 else "😔"
            stress_emoji = "😌" if avg_stress <= 2 else "😰" if avg_stress >= 4 else "🤔"
            trend_mood = "📈" if trends['mood_trend'] == 'improving' else "📉" if trends['mood_trend'] == 'declining' else "➡️"
            trend_stress = "📉" if trends['stress_trend'] == 'improving' else "📈" if trends['stress_trend'] == 'worsening' else "➡️"
            st.markdown(f"""
            <div class="mood-card" role="region" aria-label="Average mood">
                <h4>{mood_emoji} Mood</h4>
                <h2>{avg_mood:.1f}/5</h2>
                <p>{trend_mood} {trends['mood_trend'].title()}</p>
            </div>
            <div class="stress-card" role="region" aria-label="Average stress">
                <h4>{stress_emoji} Stress</h4>
                <h2>{avg_stress:.1f}/5</h2>
                <p>{trend_stress} {trends['stress_trend'].title()}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.subheader("🎭 Mood Check")
        mood_input = st.selectbox("Feeling?", [1, 2, 3, 4, 5], index=2, format_func=lambda x: f"{x} {'😢' if x<=2 else '😐' if x==3 else '😊'}")
        stress_input = st.selectbox("Stress?", [1, 2, 3, 4, 5], index=2, format_func=lambda x: f"{x} {'😄' if x<=2 else '🫤' if x==3 else '😓'}")
        if st.button("📝 Log Mood"):
            log_mood_data(mood_input, stress_input, 'manual_entry')
            st.success("Mood logged successfully!")
            st.rerun()
        
        st.subheader("📤 Export Data")
        if not st.session_state.mood_data.empty:
            mood_csv, mood_filename = export_data_as_csv(st.session_state.mood_data, "mood")
            st.download_button("📊 Mood Data", mood_csv, mood_filename, "text/csv")
            st.session_state.success("Mood Data ready to download!")
        if st.session_state.messages:
            chat_data = pd.DataFrame([{
                'timestamp': datetime.now() - timedelta(minutes=len(st.session_state.messages)-i),
                'role': msg['role'],
                'content': msg['content']
            } for i, msg in enumerate(st.session_state.messages)])
            chat_csv, chat_filename = export_data_as_csv(chat_data, "chat")
            st.download_button("💬 Chat History", chat_csv, chat_filename, "text/csv")
            st.session_state.success("Chat History ready to download!")
        
        if st.button("🧹 Optimize Memory"):
            optimize_memory()
            st.success("Memory optimized successfully!")
            st.rerun()

    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("💬 Chat")
        for message in st.session_state.messages:
            style = "user-message" if message["role"] == "user" else "bot-message"
            role = "You" if message["role"] == "user" else "AI"
            st.markdown(f"""
            <div class="chat-message {style}" role="alert" aria-label="{role} message">
                <strong>{role}:</strong> {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        
        if st.session_state.crisis_detected:
            st.markdown("""
            <div class="crisis-alert" role="alert">
                <h3>🚨 Emergency Support</h3>
                <p>Please reach out if you're struggling.</p>
            </div>
            """, unsafe_allow_html=True)
        
        user_input = st.chat_input("What's on your mind?")
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
        st.subheader("📈 Analytics")
        if not st.session_state.mood_data.empty:
            mood_chart = create_mood_chart(st.session_state.mood_data)
            if mood_chart:
                if px:
                    st.plotly_chart(mood_chart, use_container_width=True)
                elif plt:
                    st.pyplot(mood_chart)
                else:
                    st.warning("Charting unavailable; install plotly or matplotlib.")
            if len(st.session_state.mood_data) > 1:
                category_chart = create_category_chart(st.session_state.mood_data)
                if category_chart:
                    if px:
                        st.plotly_chart(category_chart, use_container_width=True)
                    elif plt:
                        st.pyplot(category_chart)
            st.subheader("Recent Activity")
            for _, entry in st.session_state.mood_data.tail(5).iterrows():
                mood_emoji = "😊" if entry['mood'] >= 4 else "😐" if entry['mood'] >= 3 else "😔"
                stress_emoji = "😌" if entry['stress'] <= 2 else "😰" if entry['stress'] >= 4 else "🤔"
                crisis_flag = "⚠️" if entry['crisis'] else ""
                st.write(f"{mood_emoji} {stress_emoji} {crisis_flag} {entry['timestamp'].strftime('%H:%M:%S')} - {entry['category']}")
        else:
            st.info("Start chatting to see analytics!")

if __name__ == "__main__":
    main()
