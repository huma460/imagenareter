import streamlit as st
from openai import OpenAI

# API Key
client = OpenAI(
    api_key=st.secrets["GROK_API_KEY"],
    base_url="https://api.x.ai/v1"
)

st.title("🌐 English → اردو Translator")

text = st.text_area("Enter English text:")

if st.button("Translate to Urdu"):

    response = client.chat.completions.create(
        model="grok-beta",
        messages=[
            {
                "role": "user",
                "content": f"Translate this into Urdu: {text}"
            }
        ]
    )

    translation = response.choices[0].message.content

    st.success(translation)
