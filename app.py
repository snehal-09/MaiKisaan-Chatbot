import os
import re
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from google import genai

# Load environment
load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
app = Flask(__name__)

# ---------------- LANGUAGE DETECTION ----------------
def detect_language_strict(text: str) -> str:
    # Devanagari detection
    if re.search(r'[\u0900-\u097F]', text):
        # Could be Marathi or Hindi, decide by keywords
        if any(word in text for word in ["शेत", "पीक", "कापूस", "शेती"]):
            return "mr"
        return "hi"

    text = text.lower()

    marathi_words = [
        "kapas", "kapus", "pane", "pivli", "zad", "zhad",
        "sheti", "shet", "kide", "rog", "pani", "urea"
    ]

    hindi_words = [
        "gulab", "phool", "ful", "paani", "nahi", "nhi",
        "kyu", "ka", "ki", "ke", "raha", "rahe", "fasal"
    ]

    if any(w in text for w in marathi_words):
        return "mr"
    if any(w in text for w in hindi_words):
        return "hi"

    return "en"

# ---------------- PROMPT BUILDER ----------------
def build_prompt(lang: str, question: str) -> str:
    if lang == "mr":
        return (
            "तू MaiKisaan सहाय्यक आहेस.\n"
            "नियम:\n"
            "1) उत्तर फक्त मराठी देवनागरी लिपीत द्यायचे.\n"
            "2) इंग्रजी शब्द, रोमन अक्षरे, बुलेट किंवा चिन्हे वापरायची नाहीत.\n"
            "3) उत्तर सोपे, स्पष्ट आणि शेतकऱ्यांसाठी उपयुक्त असावे.\n\n"
            f"प्रश्न: {question}\n"
            "उत्तर:"
        )

    if lang == "hi":
        return (
            "आप MaiKisaan सहायक हैं।\n"
            "नियम:\n"
            "1) उत्तर केवल हिंदी देवनागरी लिपि में दें।\n"
            "2) अंग्रेज़ी या रोमन हिंदी शब्दों का प्रयोग न करें।\n"
            "3) उत्तर सरल और किसानों के लिए उपयोगी हो।\n\n"
            f"प्रश्न: {question}\n"
            "उत्तर:"
        )

    return (
        "You are MaiKisaan Assistant.\n"
        "Reply in simple English without markdown.\n\n"
        f"Question: {question}\n"
        "Answer:"
    )

# ---------------- CLEAN RESPONSE ----------------
def clean_text(text: str) -> str:
    for s in ["###", "##", "#", "**", "*", "---", "__"]:
        text = text.replace(s, "")
    return text.strip()

# ---------------- FORCE TRANSLATION (FAILSAFE) ----------------
def force_language(reply: str, lang: str) -> str:
    if lang == "en":
        return reply

    # If Devanagari exists, assume OK
    if re.search(r'[\u0900-\u097F]', reply):
        return reply

    # Otherwise translate using Gemini
    if lang == "mr":
        prompt = f"खालील मजकूर शुद्ध मराठी देवनागरीत भाषांतर करा:\n{reply}"
    else:
        prompt = f"निम्नलिखित पाठ को शुद्ध हिंदी देवनागरी में अनुवाद करें:\n{reply}"

    response = client.models.generate_content(
        model="models/gemini-flash-latest",
        contents=prompt
    )

    return response.text.strip()

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template("index.html")

from google.genai.errors import ClientError

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_msg = data.get("message", "")
    lang = data.get("language", "en")

    try:
        prompt = build_prompt(lang, user_msg)

        response = client.models.generate_content(
            model="models/gemini-flash-latest",
            contents=prompt
        )

        reply = clean_text(response.text)

    except ClientError as e:
        # Handle quota / rate limit error
        if "RESOURCE_EXHAUSTED" in str(e):
            if lang == "mr":
                reply = (
                    "सध्या सर्व्हरवर जास्त विनंत्या आल्या आहेत.\n"
                    "कृपया १ मिनिट थांबा आणि पुन्हा प्रयत्न करा 🙏"
                )
            elif lang == "hi":
                reply = (
                    "अभी सर्वर पर बहुत अधिक अनुरोध हैं।\n"
                    "कृपया 1 मिनट बाद फिर प्रयास करें 🙏"
                )
            else:
                reply = (
                    "Too many requests right now.\n"
                    "Please wait 1 minute and try again 🙏"
                )
        else:
            reply = "Server error. Please try again later."

    except Exception:
        reply = "Something went wrong. Please try again."

    return jsonify({"reply": reply})

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)


