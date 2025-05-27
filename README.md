# 404
# RU Mental Health Buddy

## Overview

The **RU Mental Health Buddy** is a web application designed to provide mental health support to students at Redeemers University. It utilizes a chatbot interface to engage users in conversation, offering responses based on their input related to various mental health topics. The application is built using Streamlit, a popular framework for creating web applications in Python.

## Requirements

To run this application, ensure you have the following packages installed:

```plaintext
streamlit>=1.28.0
# Optional: Uncomment if you need additional functionality later
# requests>=2.28.0  # For HTTP requests
# pandas>=1.5.0     # For data processing
```

## Setup Instructions

1. **Install Dependencies**: Use pip to install the required packages.

    ```bash
    pip install -r requirements.txt
    ```
2. **Run the Application**: Start the Streamlit server.

    ```bash
    streamlit run app.py
    ```

## Application Structure

### Page Configuration

The application is configured with a title, icon, layout, and sidebar state.

```python
st.set_page_config(
    page_title="RU Mental Health Buddy",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="collapsed"
)
```

### Custom CSS

The `load_css` function returns a string containing CSS styles for the application, enhancing its visual appeal.

```python
@st.cache_data
def load_css():
    return """
    <style>
    /* CSS styles for the application */
    </style>
    """
```

### Response Templates

The `load_response_templates` function loads predefined response templates for various mental health topics. Each template includes patterns to match user input and corresponding responses.

```python
@st.cache_data
def load_response_templates():
    return {
        "greetings": {
            "patterns": ["hi", "hello", ...],
            "responses": ["Hello! I'm your mental health buddy...", ...],
            "follow_ups": ["Tell me more about how you've been feeling lately...", ...]
        },
        ...
    }
```

### SmartResponder Class

The `SmartResponder` class is responsible for analyzing user input and generating appropriate responses based on the context of the conversation.

#### Methods

* **`__init__`**: Initializes the responder with response templates and conversation context.
* **`analyze_input(user_input)`**: Analyzes the user's input to determine the most relevant category based on predefined patterns.
* **`generate_response(user_input, category=None)`**: Generates a response based on the user's input and the identified category.

### Session State Management

The application uses Streamlit's session state to manage conversation history and the responder instance.

```python
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'responder' not in st.session_state:
    st.session_state.responder = SmartResponder()
```

### User Interface

The main interface includes a chat container for displaying messages, a text input for user input, and quick action buttons for common mental health topics.

```python
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
# Display recent messages
for message in recent_messages:
    ...
st.markdown('</div>', unsafe_allow_html=True)

user_input = st.text_input("Share what's on your mind...", ...)
```

### Quick Action Buttons

Quick action buttons allow users to quickly express their feelings or concerns, which are then processed by the responder.

```python
quick_actions = [
    ("😰 Feeling Anxious", "I'm feeling really anxious right now"),
    ...
]
```

### Footer and Debug Information

The footer provides additional information about the application, and an optional debug section displays memory usage for troubleshooting.

```python
st.markdown("---")
st.markdown("Made with ❤️ for Redeemers University Students | You're never alone in this journey!")

if st.checkbox("Show Debug Info", value=False):
    st.write(f"Messages in memory: {len(st.session_state.messages)}")
    ...
```

## Usage Example

1. Launch the application.
2. Type a message in the input box or click a quick action button.
3. The chatbot will respond based on the input, providing support and follow-up questions as needed.

## Conclusion

The RU Mental Health Buddy is a supportive tool for students, offering a safe space to discuss mental health concerns. The application is designed to be user-friendly and responsive, ensuring that students feel heard and supported.
