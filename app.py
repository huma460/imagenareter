
from flask import Flask, request, jsonify, render_template_string
from deep_translator import GoogleTranslator
from langdetect import detect

app = Flask(__name__)

# Supported languages (name -> code)
LANGUAGES = {
    "Afrikaans": "af", "Albanian": "sq", "Amharic": "am", "Arabic": "ar",
    "Armenian": "hy", "Azerbaijani": "az", "Basque": "eu", "Belarusian": "be",
    "Bengali": "bn", "Bosnian": "bs", "Bulgarian": "bg", "Catalan": "ca",
    "Cebuano": "ceb", "Chinese (Simplified)": "zh-CN", "Chinese (Traditional)": "zh-TW",
    "Corsican": "co", "Croatian": "hr", "Czech": "cs", "Danish": "da",
    "Dutch": "nl", "English": "en", "Esperanto": "eo", "Estonian": "et",
    "Finnish": "fi", "French": "fr", "Frisian": "fy", "Galician": "gl",
    "Georgian": "ka", "German": "de", "Greek": "el", "Gujarati": "gu",
    "Haitian Creole": "ht", "Hausa": "ha", "Hawaiian": "haw", "Hebrew": "iw",
    "Hindi": "hi", "Hmong": "hmn", "Hungarian": "hu", "Icelandic": "is",
    "Igbo": "ig", "Indonesian": "id", "Irish": "ga", "Italian": "it",
    "Japanese": "ja", "Javanese": "jw", "Kannada": "kn", "Kazakh": "kk",
    "Khmer": "km", "Korean": "ko", "Kurdish": "ku", "Kyrgyz": "ky",
    "Lao": "lo", "Latin": "la", "Latvian": "lv", "Lithuanian": "lt",
    "Luxembourgish": "lb", "Macedonian": "mk", "Malagasy": "mg", "Malay": "ms",
    "Malayalam": "ml", "Maltese": "mt", "Maori": "mi", "Marathi": "mr",
    "Mongolian": "mn", "Myanmar (Burmese)": "my", "Nepali": "ne", "Norwegian": "no",
    "Nyanja (Chichewa)": "ny", "Pashto": "ps", "Persian": "fa", "Polish": "pl",
    "Portuguese": "pt", "Punjabi": "pa", "Romanian": "ro", "Russian": "ru",
    "Samoan": "sm", "Scots Gaelic": "gd", "Serbian": "sr", "Sesotho": "st",
    "Shona": "sn", "Sindhi": "sd", "Sinhala": "si", "Slovak": "sk",
    "Slovenian": "sl", "Somali": "so", "Spanish": "es", "Sundanese": "su",
    "Swahili": "sw", "Swedish": "sv", "Tagalog (Filipino)": "tl", "Tajik": "tg",
    "Tamil": "ta", "Telugu": "te", "Thai": "th", "Turkish": "tr",
    "Ukrainian": "uk", "Urdu": "ur", "Uzbek": "uz", "Vietnamese": "vi",
    "Welsh": "cy", "Xhosa": "xh", "Yiddish": "yi", "Yoruba": "yo", "Zulu": "zu"
}


@app.route("/")
def index():
    """Serve the main translator page."""
    return render_template_string(open("index.html").read() if __import__("os").path.exists("index.html") else "<h1>Translator API Running</h1><p>Use /translate endpoint.</p>")


@app.route("/translate", methods=["POST"])
def translate():
    """
    Translate text from source language to target language.

    JSON body:
        text (str): Text to translate.
        source (str): Source language code (e.g., 'en'). Use 'auto' for auto-detection.
        target (str): Target language code (e.g., 'fr').

    Returns:
        JSON with translated text, detected language (if auto), and status.
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON body provided."}), 400

    text = data.get("text", "").strip()
    source = data.get("source", "auto")
    target = data.get("target", "en")

    if not text:
        return jsonify({"error": "No text provided."}), 400

    if target not in LANGUAGES.values():
        return jsonify({"error": f"Unsupported target language: '{target}'."}), 400

    # Auto-detect source language if requested
    detected_lang = None
    if source == "auto":
        try:
            detected_lang = detect(text)
            source = detected_lang
        except Exception:
            source = "auto"

    try:
        translated = GoogleTranslator(source=source, target=target).translate(text)
        return jsonify({
            "status": "success",
            "original": text,
            "translated": translated,
            "source_language": detected_lang or source,
            "target_language": target
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/detect", methods=["POST"])
def detect_language():
    """
    Detect the language of the given text.

    JSON body:
        text (str): Text to detect.

    Returns:
        JSON with detected language code and status.
    """
    data = request.get_json()
    text = data.get("text", "").strip() if data else ""

    if not text:
        return jsonify({"error": "No text provided."}), 400

    try:
        lang_code = detect(text)
        lang_name = next((k for k, v in LANGUAGES.items() if v == lang_code), lang_code)
        return jsonify({
            "status": "success",
            "detected_language_code": lang_code,
            "detected_language_name": lang_name
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/languages", methods=["GET"])
def get_languages():
    """Return all supported languages as a list of {name, code} objects."""
    langs = [{"name": name, "code": code} for name, code in sorted(LANGUAGES.items())]
    return jsonify({"status": "success", "languages": langs, "count": len(langs)})


if __name__ == "__main__":
    print("🌐 Lingua Translator API running at http://127.0.0.1:5000")
    print("📌 Endpoints:")
    print("   POST /translate   — Translate text")
    print("   POST /detect      — Detect language")
    print("   GET  /languages   — List supported languages")
    app.run(debug=True, host="0.0.0.0", port=5000)
