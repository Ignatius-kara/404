Mental Health Support Chatbot
A Streamlit-based mental health support chatbot with advanced analytics, designed to engage users in empathetic conversations, track mood and stress, and provide real-time visualizations. The app supports crisis detection, localization for Nigerian Pidgin, and integrates with a conversation log to address themes like self-forgiveness, identity, and relationships.
Features

Chat Interface: Engage in conversations with an AI assistant that responds based on mood, stress, and conversation category.
Mood and Stress Tracking: Log mood/stress via text analysis (Hugging Face emotion classifier) or manual input, stored in a pandas DataFrame.
Analytics Visualizations: Plotly charts for mood/stress trends and conversation topic distribution, with crisis event annotations.
Crisis Detection: Identifies high-risk keywords and provides localized support resources (e.g., Nigerian counseling numbers).
Localization: Supports Nigerian Pidgin responses for culturally sensitive interactions.
Memory Optimization: Caching, garbage collection, and data pruning to manage memory usage.
Data Export: Download mood data and chat history as CSV files.
Accessibility: High-contrast design, ARIA labels, and large fonts for better accessibility.
Document Integration: Loads conversation logs (e.g., JSON) to populate mood data and chat history, aligning with themes like self-forgiveness and boundary-setting.

Prerequisites

Python 3.8+
A system with at least 4GB RAM (for Hugging Face model loading)
Internet connection (for downloading model weights)

Installation

Clone the repository:git clone https://github.com/your-repo/mental-health-chatbot.git
cd mental-health-chatbot


Create a virtual environment:python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install dependencies:pip install -r requirements.txt


(Optional) Replace the sample document data in app.py (load_document_data) with your conversation log JSON file.

Usage

Run the Streamlit app:streamlit run app.py


Open your browser at http://localhost:8501.
Interact via the chat interface, log mood/stress manually, view analytics, or export data.
To load a custom conversation log, update the load_document_data function with your JSON file path and structure.

Project Structure

app.py: Main Streamlit application with chatbot and analytics.
requirements.txt: Python dependencies.
README.md: Project documentation.

Notes

Crisis Support: The app is not a substitute for professional mental health care. Crisis resources are provided for immediate support.
LLM Integration: The current code uses a mock LLM response system. For advanced responses, integrate xAI's Grok API (see https://x.ai/api).
Document Format: The sample document assumes a JSON list of entries with user_message, emotion, intent, and chatbot_response. Adjust mappings in map_document_emotion_to_scores and map_document_intent_to_category for your data.

Contributing
Contributions are welcome! Please open an issue or submit a pull request with improvements or bug fixes.
License
MIT License. See LICENSE for details.
