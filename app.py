import os
import re
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-secret-key")

PII_PATTERNS = [
    (r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', '[EMAIL]'),
    (r'\b(?:\+91[-\s]?)?[6-9]\d{9}\b', '[PHONE]'),
    (r'\b\d{12}\b', '[ID_NUMBER]'),
    (r'\b(?:\d[ -]*?){13,19}\b', '[CARD_NUMBER]'),
]

def mask_pii(text):
    for pattern, replacement in PII_PATTERNS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def demo_response(message):
    return (
        "🔐 PrivacyFirst AI is running in DEMO mode.\n\n"
        "Your message passed through the privacy layer.\n\n"
        f"Processed message:\n{message}\n\n"
        "Add GEMINI_API_KEY in Render Environment Variables "
        "to enable real AI responses."
    )

def ai_response(message):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return demo_response(message)

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        model = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

        prompt = f"""
You are PrivacyFirst AI, a privacy-focused conversational assistant.
Do not ask for unnecessary personal information.
Never request passwords, API keys, banking details, or OTPs.
Treat [EMAIL], [PHONE], [ID_NUMBER], and [CARD_NUMBER] as masked data.
Answer clearly and naturally.
Do not claim the system is completely private or anonymous.

User message:
{message}
"""
        response = client.models.generate_content(
            model=model,
            contents=prompt
        )
        return response.text if response and response.text else "I couldn't generate a response."

    except Exception as error:
        print("Gemini error:", error)
        return "⚠️ The AI service could not be reached. Please check your Gemini API configuration."

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(silent=True) or {}
        original = str(data.get("message", "")).strip()

        if not original:
            return jsonify({"error": "Message cannot be empty."}), 400

        masked = mask_pii(original)
        answer = ai_response(masked)

        return jsonify({
            "answer": answer,
            "privacy": {
                "pii_masking_applied": masked != original,
                "processed_message": masked
            }
        })
    except Exception as error:
        print("Chat error:", error)
        return jsonify({"error": "An unexpected server error occurred."}), 500

@app.route("/api/clear", methods=["POST"])
def clear_chat():
    session.clear()
    return jsonify({"ok": True})

@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "PrivacyFirst AI"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
