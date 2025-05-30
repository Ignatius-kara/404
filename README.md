Mental Health Support Chatbot
A Streamlit-based chatbot for mental health support, featuring mood/stress tracking, analytics, crisis detection, and Nigerian Pidgin localization. Integrates conversation logs for themes like self-forgiveness and relationships.
Features

Chat Interface: AI responses based on mood, stress, and conversation category.
Mood/Stress Tracking: Uses Hugging Face’s distilbert-base-uncased-emotion or TextBlob fallback.
Analytics: Plotly charts for mood/stress trends and topic distribution (if Plotly is installed).
Crisis Detection: Localized support resources (e.g., Nigerian counseling numbers).
Localization: Nigerian Pidgin responses.
Memory Optimization: Caching and data pruning.
Data Export: CSV downloads for mood data and chat history.
Accessibility: ARIA labels and high-contrast design.
Document Integration: Loads JSON conversation logs.

Prerequisites

Python 3.10
Git
Streamlit Community Cloud account
2GB+ RAM for local testing

Installation

Clone the repository:git clone https://github.com/your-repo/404.git
cd 404


Create a virtual environment:python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate


Install dependencies:pip install --upgrade pip
bash setup.sh



Deployment on Streamlit Cloud

Push the repository to GitHub (public or private with Streamlit access).
Ensure these files are in the repo root:
code_base.py: Main application.
requirements.txt: Python dependencies (excludes torch).
runtime.txt:python-3.10


packages.txt:libblas-dev
liblapack-dev
g++
python3-distutils
build-essential
python3-dev


setup.sh:#!/bin/bash
pip install --upgrade pip
pip install torch==2.4.1+cpu -f https://download.pytorch.org/whl/torch_stable.html || echo "Torch install failed"
pip install -r requirements.txt || echo "Requirements install failed"




In Streamlit Cloud:
Link the GitHub repo (branch: main).
Set the main module to code_base.py.
Deploy and check "Manage App" logs.


If errors occur, see Troubleshooting.

Usage

Run locally:streamlit run code_base.py


Access at http://localhost:8501.
Chat, log mood/stress, view analytics (if Plotly is installed), or export data.
Update load_document_data in code_base.py for custom JSON logs.

Project Structure

code_base.py: Main application.
requirements.txt: Dependencies (excludes torch).
runtime.txt: Python version.
packages.txt: System libraries.
setup.sh: Installs torch and dependencies.
README.md: Documentation.

Troubleshooting

ModuleNotFoundError: plotly.express:
Check "Manage App" logs for uv errors.
Ensure runtime.txt specifies python-3.10.
Run pip install plotly==5.24.1 locally to verify compatibility.


Python version mismatch:
Confirm runtime.txt is in the repo root with python-3.10.


Torch installation failure:
Verify setup.sh logs (echo statements) in the terminal.
Test locally: pip install torch==2.4.1+cpu -f https://download.pytorch.org/whl/torch_stable.html.


uv pip install issues:
Clear Streamlit Cloud cache via "Manage App" > "Advanced Settings".
Post logs to Streamlit forums.



Notes

Crisis Support: Not a substitute for professional care.
LLM: Uses static responses; integrate xAI’s Grok API for advanced AI (https://x.ai/api).
Document: Update load_document_data for your JSON structure.
Plotly: If charts fail, ensure Python 3.10 and retry deployment.

License
MIT License.
