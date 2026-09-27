# PrivacyFirst AI — Render Ready

## Render
Build Command:
pip install -r requirements.txt

Start Command:
gunicorn app:app

Environment variables:
FLASK_SECRET_KEY
GEMINI_API_KEY
GEMINI_MODEL=gemini-3.1-flash-lite

## Local
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
python app.py

Open http://127.0.0.1:5000

## Health
Open /health after deployment.

Never put your real Gemini API key in app.py or GitHub.
The PII masking layer is a starter protection and does not guarantee complete anonymity.
