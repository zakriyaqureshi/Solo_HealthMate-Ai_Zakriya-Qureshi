
import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI

# Load API key from .env
load_dotenv()

# Create Flask application
app = Flask(__name__)

# Connect to OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# AI chatbot endpoint
@app.route("/api/chat", methods=["POST"])
def chat():

    # Get question and language from frontend
    data = request.get_json(silent=True) or {}

    question = data.get("question", "").strip()
    language = data.get("language", "English")

    # Check empty question
    if not question:
        return jsonify({"error": "Please enter a question."}), 400

    # Check API key
    if not os.getenv("OPENROUTER_API_KEY"):
        return jsonify({"error": "API key is missing."}), 500

    try:
        response = client.chat.completions.create(
            model="openrouter/free",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are HealthMate AI, a healthcare information "
                        "assistant. Explain general health information in "
                        "simple language. Reply in the requested language: "
                        + language +
                        ". Do not diagnose diseases, prescribe medicines, "
                        "or recommend medication dosages. Encourage users "
                        "to consult qualified healthcare professionals. "
                        "For possible emergencies, advise immediate "
                        "emergency medical assistance."
                    )
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
        )

        answer = response.choices[0].message.content

        return jsonify({"answer": answer})

    except Exception:
        app.logger.exception("OpenRouter API request failed")
        return jsonify({
            "error": "Sorry, the AI service is temporarily unavailable. Please try again."
        }), 502


# Medical Text Simplifier
@app.route("/api/simplify", methods=["POST"])
def simplify():

    data = request.get_json(silent=True) or {}

    medical_text = data.get("text", "").strip()
    language = data.get("language", "English")

    if not medical_text:
        return jsonify({"error": "Please enter medical text."}), 400

    if not os.getenv("OPENROUTER_API_KEY"):
        return jsonify({"error": "API key is missing."}), 500

    try:
        response = client.chat.completions.create(
            model="openrouter/free",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are HealthMate AI. Explain the provided "
                        "medical text in simple, easy-to-understand language. "
                        "Reply in " + language + ". Do not diagnose, "
                        "prescribe medicines, or recommend dosages. "
                        "Do not change the meaning of the original text. "
                        "Encourage users to consult a healthcare professional."
                    )
                },
                {
                    "role": "user",
                    "content": medical_text
                }
            ]
        )

        answer = response.choices[0].message.content

        return jsonify({"answer": answer})

    except Exception:
        app.logger.exception("Medical text simplification failed")
        return jsonify({
            "error": "The AI service is temporarily unavailable."
        }), 502

# Run application

# Preventive Health Tips API
@app.route("/api/tips", methods=["POST"])
def health_tips():

    data = request.get_json(silent=True) or {}
    language = data.get("language", "English")

    if not os.getenv("OPENROUTER_API_KEY"):
        return jsonify({"error": "API key is missing."}), 500

    try:
        response = client.chat.completions.create(
            model="openrouter/free",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are HealthMate AI. Generate 5 simple, "
                        "general preventive health and wellness tips. "
                        "Reply in " + language + ". "
                        "Use clear numbered points. Focus on safe everyday "
                        "habits such as hydration, sleep, physical activity "
                        "and hygiene. Avoid diagnosis, medication advice, "
                        "or unsupported medical claims. Mention that tips "
                        "do not replace professional medical advice."
                    )
                },
                {
                    "role": "user",
                    "content": "Give me five useful preventive health tips."
                }
            ]
        )

        answer = response.choices[0].message.content
        return jsonify({"answer": answer})

    except Exception:
        app.logger.exception("Health tips request failed")
        return jsonify({
            "error": "The AI service is temporarily unavailable."
        }), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
