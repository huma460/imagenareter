import streamlit as st
from xai_sdk import Client

st.set_page_config(
    page_title="English to Urdu Translator",
    page_icon="🌐",
    layout="centered"
)

st.markdown("""
<style>
    .stTextArea textarea {
        font-size: 16px;
    }
    .stButton button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 8px;
        width: 100%;
    }
    .result-box {
        background-color: #1a1a2e;
        border: 1px solid #4a4a8a;
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
        font-size: 18px;
        color: #e0e0ff;
        line-height: 2;
        direction: rtl;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

st.title("🌐 English → اردو Translator")
st.markdown("<p style='text-align:center; color:#888;'>Powered by Grok AI</p>", unsafe_allow_html=True)

english_text = st.text_area(
    "Enter English text:",
    placeholder="Type or paste your English text here...",
    height=150
)

if st.button("Translate to Urdu 🔄"):
    if english_text.strip() == "":
        st.warning("Please enter some text first!")
    else:
        with st.spinner("Translating..."):
            try:
                client = Client(api_key=st.secrets["GROK_API_KEY"])

                response = client.chat.completions.create(
                    model="grok-3",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a translator. Translate English to Urdu. Return ONLY the Urdu translation, nothing else."
                        },
                        {
                            "role": "user",
                            "content": english_text
                        }
                    ]
                )

                urdu_translation = response.choices[0].message.content

                st.markdown("### Urdu Translation:")
                st.markdown(f'<div class="result-box">{urdu_translation}</div>', unsafe_allow_html=True)
                st.text_area("Copy translation:", value=urdu_translation, height=100)

            except Exception as e:
                st.error(f"Error: {str(e)}")

st.markdown("---")
st.markdown("<p style='text-align:center; color:#555; font-size:12px;'>Made with ❤️ using Grok AI</p>", unsafe_allow_html=True)
