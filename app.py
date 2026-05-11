import streamlit as st
from deep_translator import GoogleTranslator

st.set_page_config(page_title="English → اردو Translator", page_icon="🌐")

st.title("🌐 English → اردو Translator")
st.write("100% Free - کوئی API Key نہیں چاہیے")

# Input
text = st.text_area("Enter English text:", height=150, placeholder="Type: I love Pakistan")

# Button
if st.button("Translate to Urdu", type="primary"):
    if text.strip() == "":
        st.warning("پہلے کچھ English لکھو 👆")
    else:
        try:
            with st.spinner("Translate ہو رہا ہے..."):
                # Translate کرو - یہ نیا طریقہ ہے
                translated = GoogleTranslator(source='en', target='ur').translate(text)
            
            st.success("ترجمہ ہو گیا ✅")
            st.text_area("Urdu Translation:", value=translated, height=150)
                
        except Exception as e:
            st.error(f"Error: {e}")
            st.info("Net slow ہے تو دوبارہ Try کرو")

st.markdown("---")
st.caption("Powered by deep-translator - Free Forever")
