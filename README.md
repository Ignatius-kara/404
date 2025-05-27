Mental Health Support Chatbot
A Streamlit-based chatbot for mental health support, featuring mood/stress tracking, analytics, crisis detection, and Nigerian Pidgin localization. It integrates conversation logs to address themes like self-forgiveness and relationships.
Features

Chat Interface: AI responses based on mood, stress, and conversation category.
Mood/Stress Tracking: Uses Hugging Face’s distilbert-base-uncased-emotion or TextBlob fallback.
Analytics: Plotly charts for mood/stress trends and topic distribution, with crisis annotations.
Crisis Detection: Localized support resources (e.g., Nigerian counseling numbers).
Localization: Nigerian Pidgin responses.
Memory Optimization: Caching and data pruning for Streamlit Cloud.
Data Export: CSV downloads for mood data and chat history.
Accessibility: ARIA labels and high-contrast design.
Document Integration: Loads JSON conversation logs.

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
bash setup.sh



Deployment on Streamlit Cloud

Push the repository to GitHub (public or private with Streamlit access).
Ensure these files are in the repo root:
app.py: Main application.
requirements.txt: Python dependencies (excludes torch).
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
Deploy and monitor the "Manage App" terminal.


If errors occur, see Troubleshooting.

Usage

Run locally:streamlit run app.py


Access at http://localhost:8501.
Chat, log mood/stress, view analytics, or export data.
Update load_document_data in app.py for custom JSON logs.

Project Structure

app.py: Main application.
requirements.txt: Dependencies (excludes torch).
runtime.txt: Python version.
packages.txt: System packages.
setup.sh: Installs torch and dependencies.
README.md: Documentation.

Troubleshooting

No version of torch==2.4.1+cpu:
Ensure setup.sh includes -f https://download.pytorch.org/whl/torch_stable.html.
Verify torch installation in logs.


ModuleNotFoundError: distutils:
Confirm python3-distutils in packages.txt.


Failed building wheel:
Include build-essential, python3-dev in packages.txt.


Memory issues:
Use CPU-only torch and lightweight transformers model.


Check "Manage App" logs and post on Streamlit forums.

Notes

Crisis Support: Not a substitute for professional care.
LLM: Uses static responses; integrate xAI’s Grok API for advanced AI (https://x.ai/api).
Document: Update load_document_data for your JSON structure.

License
MIT License.
