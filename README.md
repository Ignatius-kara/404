Mental Health Support Chatbot
A Streamlit-based chatbot for mental health support, featuring mood/stress tracking, analytics, and crisis detection. It integrates conversation logs to address themes like self-forgiveness and relationships, with localization for Nigerian Pidgin.
Features

Chat Interface: Empathetic AI responses based on mood, stress, and conversation category.
Mood/Stress Tracking: Uses Hugging Face’s distilbert-base-uncased-emotion or TextBlob fallback.
Analytics: Plotly charts for mood/stress trends and topic distribution, with crisis annotations.
Crisis Detection: Provides localized support resources (e.g., Nigerian counseling numbers).
Localization: Nigerian Pidgin responses for cultural sensitivity.
Memory Optimization: Caching and data pruning for Streamlit Cloud compatibility.
Data Export: CSV downloads for mood data and chat history.
Accessibility: ARIA labels and high-contrast design.
Document Integration: Loads JSON conversation logs for analytics.

Prerequisites

Python 3.10
Git
Streamlit Community Cloud account
2GB+ RAM for local testing

Installation

Clone the repository:git clone https://github.com/your-repo/mental-health-chatbot.git
cd mental-health-chatbot


Create a virtual environment:python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate


Install dependencies:pip install --upgrade pip
pip install torch==2.4.1+cpu -f https://download.pytorch.org/whl/torch_stable.html
pip install -r requirements.txt



Deployment on Streamlit Cloud

Push the repository to GitHub (public or private with Streamlit access).
Create these files in the repo root:
runtime.txt:python-3.10


packages.txt:libblas-dev
liblapack-dev
g++
python3-distutils
build-essential
python3-dev


setup.sh:pip install --upgrade pip
pip install torch==2.4.1+cpu -f https://download.pytorch.org/whl/torch_stable.html
pip install -r requirements.txt




In Streamlit Cloud:
Create a new app, linking your GitHub repo.
Set the Python version to 3.10 (via runtime.txt).
Deploy and check the "Manage App" terminal for errors.


If errors occur, consult logs and see Troubleshooting.

Usage

Run locally:streamlit run app.py


Access at http://localhost:8501.
Chat, log mood/stress, view analytics, or export data.
To use a custom conversation log, update load_document_data in app.py with your JSON file.

Project Structure

app.py: Main application.
requirements.txt: Dependencies.
runtime.txt: Python version.
packages.txt: System packages.
setup.sh: Setup script.
README.md: Documentation.

Troubleshooting

Error installing requirements:
Check "Manage App" terminal logs.
Ensure torch==2.4.1+cpu is installed via setup.sh.
Verify packages.txt includes necessary system libraries.


ModuleNotFoundError: distutils:
Confirm python3-distutils in packages.txt.


Failed building wheel:
Add build-essential, python3-dev to packages.txt.


Memory issues:
Use CPU-only torch and limit transformers model size.


Post issues on Streamlit forums with logs.

Notes

Crisis Support: Not a substitute for professional care.
LLM: Uses static responses; for advanced AI, integrate xAI’s Grok API (https://x.ai/api).
Document: Update load_document_data for your JSON structure.

License
MIT License.
