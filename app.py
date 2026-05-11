import streamlit as st
from googletrans import Translator

st.set_page_config(page_title="English → اردو Translator", page_icon="🌐")

st.title("🌐 English → اردو Translator")
st.write("Free Google Translate - کوئی API Key نہیں چاہیے")

# Translator object بناؤ
translator = Translator()

# User سے input لو
text = st.text_area("Enter English text:", height=150, placeholder="Type something like: How are you?")

# Button
if st.button("Translate to Urdu", type="primary"):
    if text.strip() == "":
        st.warning("پہلے کچھ English لکھو 👆")
    else:
        try:
            with st.spinner("Translate ہو رہا ہے..."):
                # Translate کرو
                result = translator.translate(text, dest='ur')
            
            st.success("ترجمہ ہو گیا ✅")
            st.text_area("Urdu Translation:", value=result.text, height=150)
            
            # Pronunciation بھی دکھا دو
            if result.pronunciation:
                st.caption(f"**Pronunciation:** {result.pronunciation}")
                
        except Exception as e:
            st.error(f"Error آ گیا: {e}")
            st.info("Net slow ہے تو 1 منٹ بعد Try کرو")

st.markdown("---")
st.caption("Made with ❤️ using Google Translate Free")
