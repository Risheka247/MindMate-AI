from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import random
import re

app = Flask(__name__)
CORS(app)

# Crisis keyword set (simple detector). Keep this conservative and expand as needed.
CRISIS_KEYWORDS = [
    r"\bkill myself\b", r"\bsuicide\b", r"\bwant to die\b", r"\bend my life\b",
    r"\bi will die\b", r"\bcut myself\b", r"\bself[- ]harm\b", r"\bworthless\b\s*and\b\s*die"
]

HOTLINES = {
    "India": "1800 599 0019",
    "USA": "988",
    "UK": "0800 689 5652",
    "International": "If you are outside these countries, contact local emergency services or search 'suicide hotline' in your country."
}

# Some therapist-style canned responses and techniques
OPENING = [
    "I hear you. Thank you for sharing that with me — you're not alone in this.",
    "I'm really glad you reached out. Tell me what's been happening recently.",
    "It takes courage to share that. I'm here to listen—what's on your mind right now?"
]

GROUNDING = [
    "Let's try a quick grounding exercise: name 5 things you can see, 4 things you can touch, 3 things you can hear, 2 things you can smell, and 1 thing you can taste. Tell me when you're ready.",
    "Try this 5-4-3-2-1 grounding: look for 5 things you see, 4 you can touch, 3 you hear, 2 you smell, and 1 you can taste. Want me to guide you step-by-step?"
]

BREATHING = [
    "Try a simple breathing technique: breathe in for 4 seconds, hold for 4, breathe out for 6 — repeat 4 times. Want me to guide you through one round now?",
    "Let's do a 1-minute breathing pause: inhale 4, hold 4, exhale 6. Focus on the breath and your chest rising and falling."
]

CBT_REFRAME = [
    "Sometimes our thoughts get harsh and automatic. Can we try to spot one unhelpful thought together and test how true it is?",
    "A helpful step is to write the thought down and ask: 'What's the evidence for this thought?' and 'Is there another way to view it?'"
]

BEHAVIORAL = [
    "Small actions can change how you feel. Is there one small thing you could try today — maybe a short walk, a glass of water, or calling a friend?",
    "Would you be open to setting a tiny goal for today, something achievable in 10–20 minutes?"
]

REASSURE = [
    "You're doing the best you can in a hard moment. It's okay to ask for help.",
    "Feelings can feel overwhelming, but they can change. You're taking a step by talking about it."
]

def detect_crisis(text: str) -> bool:
    if not text:
        return False
    t = text.lower()
    for patt in CRISIS_KEYWORDS:
        if re.search(patt, t):
            return True
    return False

def generate_reply(user_msg: str) -> dict:
    """Return dict {reply: str, crisis: bool}"""
    # Basic crisis detection
    if detect_crisis(user_msg):
        crisis_text = (
            "I'm really sorry — it sounds like you're in serious distress. "
            "If you are in immediate danger, please call your local emergency number right now.\n\n"
            "Here are some crisis resources:\n"
        )
        for k, v in HOTLINES.items():
            crisis_text += f"- {k}: {v}\n"
        crisis_text += "\nIf you want, I can guide you through a 1-minute grounding or breathing exercise now. Would you like that?"
        return {"reply": crisis_text, "crisis": True}

    # Normalize
    msg = user_msg.lower().strip()

    # Short heuristics & keywords
    if any(word in msg for word in ["hi", "hello", "hey", "hii"]):
        return {"reply": random.choice(OPENING), "crisis": False}

    if any(word in msg for word in ["sad", "depressed", "down", "unhappy", "hopeless"]):
        reply = (
            "I'm sorry you're feeling sad or low. That feeling is valid. "
            + random.choice(REASSURE) + " "
            + random.choice(GROUNDING)
        )
        return {"reply": reply, "crisis": False}

    if any(word in msg for word in ["anxious", "anxiety", "panic", "scared", "nervous"]):
        reply = (
            random.choice(REASSURE) + " " +
            random.choice(BREATHING) + "\n\nWould you like another short grounding or to talk about what triggered this?"
        )
        return {"reply": reply, "crisis": False}

    if any(word in msg for word in ["lonely", "alone", "isolated"]):
        reply = (
            "Feeling lonely can be heavy. " +
            random.choice(REASSURE) + " " +
            random.choice(BEHAVIORAL)
        )
        return {"reply": reply, "crisis": False}

    if any(word in msg for word in ["sleep", "insomnia", "tired", "exhausted"]):
        reply = (
            "Sleep and rest matter a lot. Try a short wind-down: reduce screens, dim lights, and try gentle breathing. "
            "Would you like some sleep-focused tips or a short relaxation exercise?"
        )
        return {"reply": reply, "crisis": False}

    if any(word in msg for word in ["thanks", "thank", "bye", "goodbye"]):
        return {"reply": "You’re welcome. Take care of yourself — I'm here whenever you need to talk.", "crisis": False}

    # If user asks for help / wants coping strategies
    if any(phrase in msg for phrase in ["help", "cope", "coping", "advice", "tips"]):
        reply = (
            "Here are some coping ideas:\n"
            "1. Breathing pauses: inhale 4 — hold 4 — exhale 6 (repeat 3–5x).\n"
            "2. Grounding (5-4-3-2-1) to bring focus to the present.\n"
            "3. Small action: a 10-minute walk, water, or texting a friend.\n"
            "4. Write one thought and challenge it (CBT).\n\nWhich of these would you like to try now?"
        )
        return {"reply": reply, "crisis": False}

    # Default — reflective prompt + invite
    reflective = (
        "Thank you for telling me. Can you say more about what you were feeling in that moment? "
        "If you're unsure, try describing the last hour and any thoughts that stood out."
    )
    return {"reply": reflective, "crisis": False}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    user_message = data.get("message", "")
    if not isinstance(user_message, str):
        user_message = str(user_message)

    result = generate_reply(user_message)
    # For safety, do not store or log sensitive user text. (If logging, make sure to anonymize.)
    return jsonify(result)

if __name__ == "__main__":
    # Dev server — for production, use proper WSGI host or Replit
    app.run(host="0.0.0.0", port=3000)