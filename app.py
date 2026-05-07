
from flask import Flask, request, jsonify
from groq import Groq
import os

app = Flask(__name__)

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Supported languages
LANGUAGES = {
    "Afrikaans": "af", "Albanian": "sq", "Amharic": "am", "Arabic": "ar",
    "Armenian": "hy", "Azerbaijani": "az", "Bengali": "bn", "Bosnian": "bs",
    "Bulgarian": "bg", "Catalan": "ca", "Chinese (Simplified)": "zh-CN",
    "Chinese (Traditional)": "zh-TW", "Croatian": "hr", "Czech": "cs",
    "Danish": "da", "Dutch": "nl", "English": "en", "Estonian": "et",
    "Finnish": "fi", "French": "fr", "Galician": "gl", "Georgian": "ka",
    "German": "de", "Greek": "el", "Gujarati": "gu", "Haitian Creole": "ht",
    "Hebrew": "he", "Hindi": "hi", "Hungarian": "hu", "Icelandic": "is",
    "Indonesian": "id", "Irish": "ga", "Italian": "it", "Japanese": "ja",
    "Kannada": "kn", "Kazakh": "kk", "Korean": "ko", "Latvian": "lv",
    "Lithuanian": "lt", "Macedonian": "mk", "Malay": "ms", "Malayalam": "ml",
    "Maltese": "mt", "Marathi": "mr", "Mongolian": "mn", "Nepali": "ne",
    "Norwegian": "no", "Persian": "fa", "Polish": "pl", "Portuguese": "pt",
    "Punjabi": "pa", "Romanian": "ro", "Russian": "ru", "Serbian": "sr",
    "Sinhala": "si", "Slovak": "sk", "Slovenian": "sl", "Somali": "so",
    "Spanish": "es", "Swahili": "sw", "Swedish": "sv", "Tagalog": "tl",
    "Tamil": "ta", "Telugu": "te", "Thai": "th", "Turkish": "tr",
    "Ukrainian": "uk", "Urdu": "ur", "Uzbek": "uz", "Vietnamese": "vi",
    "Welsh": "cy", "Yoruba": "yo", "Zulu": "zu"
}


def get_language_name(code):
    """Get language name from code."""
    return next((name for name, c in LANGUAGES.items() if c == code), code)


@app.route("/translate", methods=["POST"])
def translate():
    """
    Translate text using Groq LLM.

    JSON body:
        text   (str): Text to translate.
        source (str): Source language code or 'auto' for auto-detect.
        target (str): Target language code (e.g., 'ur', 'fr').

    Returns:
        JSON with translated text and metadata.
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON body provided."}), 400

    text = data.get("text", "").strip()
    source = data.get("source", "auto")
    target = data.get("target", "en")

    if not text:
        return jsonify({"error": "No text provided."}), 400

    # Build source language instruction
    if source == "auto":
        source_instruction = "Detect the source language automatically."
    else:
        source_name = get_language_name(source)
        source_instruction = f"The source language is {source_name}."

    target_name = get_language_name(target)

    prompt = f"""You are a professional translator.
{source_instruction}
Translate the following text into {target_name}.

Rules:
- Return ONLY the translated text, nothing else.
- Do not add any explanation, notes, or extra text.
- Preserve the original formatting, tone, and style.
- If the text is already in {target_name}, return it as-is.

Text to translate:
{text}"""

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert multilingual translator. Always respond with only the translated text — no preamble, no explanation."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=2048
        )

        translated_text = response.choices[0].message.content.strip()

        return jsonify({
            "status": "success",
            "original": text,
            "translated": translated_text,
            "source_language": source,
            "target_language": target,
            "target_language_name": target_name,
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/detect", methods=["POST"])
def detect_language():
    """
    Detect the language of the given text using Groq.

    JSON body:
        text (str): Text to detect.

    Returns:
        JSON with detected language name and code.
    """
    data = request.get_json()
    text = data.get("text", "").strip() if data else ""

    if not text:
        return jsonify({"error": "No text provided."}), 400

    prompt = f"""Detect the language of the following text.
Respond with ONLY a JSON object in this exact format:
{{"language_name": "English", "language_code": "en"}}

Do not include any other text or explanation.

Text: {text}"""

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=60
        )

        import json
        result = json.loads(response.choices[0].message.content.strip())

        return jsonify({
            "status": "success",
            "detected_language_name": result.get("language_name", "Unknown"),
            "detected_language_code": result.get("language_code", "??")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/languages", methods=["GET"])
def get_languages():
    """Return all supported languages."""
    langs = [{"name": name, "code": code} for name, code in sorted(LANGUAGES.items())]
    return jsonify({"status": "success", "languages": langs, "count": len(langs)})


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "app": "Lingua Translator API (Groq)",
        "endpoints": {
            "POST /translate": "Translate text",
            "POST /detect": "Detect language",
            "GET  /languages": "List supported languages"
        }
    })


if __name__ == "__main__":
    if not os.environ.get("GROQ_API_KEY"):
        print("⚠️  WARNING: GROQ_API_KEY environment variable not set!")
        print("   Set it with: export GROQ_API_KEY=your_key_here")
    else:
        print("✅ Groq API key loaded.")

    print("\n🌐 Lingua Translator API (Groq) running at http://127.0.0.1:5000")
    print("📌 Endpoints:")
    print("   POST /translate   — Translate text")
    print("   POST /detect      — Detect language")
    print("   GET  /languages   — List supported languages\n")

    app.run(debug=True, host="0.0.0.0", port=5000)
