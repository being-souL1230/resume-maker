# 🧠 Smart Resume Builder with AI Feedback

A Flask-based web application to build professional resumes from predefined templates. It not only allows users to create, preview, and download resumes — but also evaluates them with a detailed scoring system and provides AI-generated feedback for improvement.

---

## 🚀 Features

- 📝 Multiple resume templates
- ➕ Add custom fields dynamically
- 📊 Resume scoring out of 100 (section-wise breakdown)
- 🤖 AI-based feedback using LLaMA3 (Groq API)
- 📥 Download/Print-ready preview

---

## 📂 Tech Stack

- Python (Flask)
- HTML/CSS (inline styling)
- Groq API (LLaMA3 model for resume feedback)
- Jinja2 templating

---

## ⚙️ Installation Guide

### 1. Clone the Repository
```bash
git clone https://github.com/being-souL1230/resume-maker.git
cd resume-maker
```
### 2. Set up Virtual Environment (optional but recommended)
```bash
python -m venv env
env\Scripts\activate       # On Windows
source env/bin/activate    # On Linux/Mac
```

### 3. Install Dependencies
```bash
pip install flask groq
```

### 4. Add Your Groq API Key

Open app.py and replace this line:
```bash
client = Groq(api_key="YOUR_API_KEY")
```

### 5. Run the App
```bash
python app.py
```
### Note:- Do not forget to delete venv after cloning repository
