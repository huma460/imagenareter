
import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import base64

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Image Generator",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.stApp { background: #0d0d0f; color: #f0ede8; }

h1, h2, h3 { font-family: 'Syne', sans-serif !important; }

.title-block { text-align: center; padding: 2.5rem 0 1rem 0; }

.title-block h1 {
    font-size: 3rem; font-weight: 800; letter-spacing: -0.03em;
    background: linear-gradient(135deg, #f0ede8 0%, #c9a96e 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0.25rem;
}

.title-block p { color: #888; font-size: 1rem; font-weight: 300; }

.stTextArea textarea {
    background: #1a1a1e !important; border: 1px solid #2a2a30 !important;
    border-radius: 12px !important; color: #f0ede8 !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 1rem !important;
    padding: 1rem !important; resize: none !important;
}

.stTextArea textarea:focus {
    border-color: #c9a96e !important;
    box-shadow: 0 0 0 2px rgba(201,169,110,0.15) !important;
}

.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #c9a96e, #a07840) !important;
    color: #0d0d0f !important; font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important; font-size: 1rem !important;
    letter-spacing: 0.04em !important; border: none !important;
    border-radius: 10px !important; padding: 0.75rem 2rem !important;
    transition: opacity 0.2s !important;
}

.stButton > button:hover { opacity: 0.85 !important; }

div[data-testid="stSelectbox"] > div > div {
    background: #1a1a1e !important; border: 1px solid #2a2a30 !important;
    border-radius: 10px !important; color: #f0ede8 !important;
}

label, .stSlider label, .stSelectbox label {
    color: #aaa !important; font-size: 0.85rem !important;
    letter-spacing: 0.06em !important; text-transform: uppercase !important;
}

.image-card {
    border-radius: 16px; overflow: hidden; border: 1px solid #2a2a30;
    margin-top: 1.5rem; background: #1a1a1e;
}

.meta-pill {
    display: inline-block; background: #1a1a1e; border: 1px solid #2a2a30;
    border-radius: 20px; padding: 4px 14px; font-size: 0.78rem;
    color: #888; margin: 4px;
}

.section-divider { border: none; border-top: 1px solid #1e1e24; margin: 1.5rem 0; }

#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="title-block">
    <h1>✦ Imagine</h1>
    <p>Powered by xAI Grok · Enter your API key to begin</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ── API Key input ─────────────────────────────────────────────────────────────
# On Streamlit Cloud: add XAI_API_KEY in App Settings → Secrets
# Locally: create .streamlit/secrets.toml with XAI_API_KEY = "xai-..."
api_key = ""
try:
    api_key = st.secrets["XAI_API_KEY"]
except Exception:
    pass

if not api_key:
    api_key = st.text_input(
        "XAI API KEY",
        type="password",
        placeholder="xai-xxxxxxxxxxxxxxxxxxxxxxxx",
        help="Get your free key at console.x.ai — only stored for this session",
    )

if not api_key:
    st.info("👆 Enter your xAI API key above. Get one free at [console.x.ai](https://console.x.ai)")
    st.stop()

# ── Prompt input ──────────────────────────────────────────────────────────────
prompt = st.text_area(
    "PROMPT",
    placeholder="A misty Japanese shrine at dawn, volumetric light, ultra-detailed oil painting...",
    height=110,
)

# ── Style presets ─────────────────────────────────────────────────────────────
STYLES = {
    "None": "",
    "Photorealistic": "photorealistic, DSLR, sharp focus, natural lighting, 8K",
    "Oil Painting": "oil painting, textured canvas, expressive brushwork, fine art",
    "Anime": "anime style, vibrant colors, cel shading, Studio Ghibli",
    "Cinematic": "cinematic, anamorphic lens, film grain, dramatic lighting, movie still",
    "Watercolor": "watercolor painting, soft edges, flowing colors, artistic",
    "Pixel Art": "pixel art, 16-bit, retro game style, crisp pixels",
    "Neon Noir": "neon noir, cyberpunk, rain-slicked streets, glowing signs, dark atmosphere",
}

col1, col2 = st.columns(2)
with col1:
    style_choice = st.selectbox("STYLE PRESET", list(STYLES.keys()))
with col2:
    n_images = st.selectbox("NUMBER OF IMAGES", [1, 2, 3, 4], index=0)

# ── Advanced options ──────────────────────────────────────────────────────────
with st.expander("⚙️ Advanced options"):
    model_choice = st.selectbox(
        "MODEL",
        ["grok-2-image", "grok-2-image-1212"],
        help="grok-2-image is the latest stable model",
    )
    response_format = st.selectbox(
        "RESPONSE FORMAT",
        ["url", "b64_json"],
        help="url = image hosted on xAI servers | b64_json = raw image data"
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Generate ──────────────────────────────────────────────────────────────────
generate_btn = st.button("✦ Generate Image")

def build_full_prompt(prompt, style_key):
    base = prompt.strip()
    suffix = STYLES.get(style_key, "")
    return f"{base}, {suffix}" if suffix else base

def generate_image(api_key, full_prompt, model, n, fmt):
    """Call xAI Grok image generation API."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "prompt": full_prompt,
        "n": n,
        "response_format": fmt,
    }
    response = requests.post(
        "https://api.x.ai/v1/images/generations",
        headers=headers,
        json=payload,
        timeout=90,
    )
    if response.status_code == 401:
        raise ValueError("Invalid API key. Double-check at console.x.ai")
    elif response.status_code == 429:
        raise ValueError("Rate limit hit. Wait a moment and try again.")
    elif response.status_code != 200:
        raise ValueError(f"API error {response.status_code}: {response.text}")
    return response.json()

def load_image(item, fmt):
    """Convert API result to PIL Image."""
    if fmt == "url":
        r = requests.get(item["url"], timeout=30)
        r.raise_for_status()
        return Image.open(BytesIO(r.content))
    else:
        return Image.open(BytesIO(base64.b64decode(item["b64_json"])))

if generate_btn:
    if not prompt.strip():
        st.warning("Please enter a prompt first.")
    else:
        full_prompt = build_full_prompt(prompt, style_choice)
        with st.spinner(f"Generating {n_images} image(s) with Grok…"):
            try:
                result = generate_image(api_key, full_prompt, model_choice, n_images, response_format)
                items = result.get("data", [])

                if not items:
                    st.error("No images returned. Try a different prompt.")
                else:
                    if len(items) == 1:
                        img = load_image(items[0], response_format)
                        st.markdown("<div class='image-card'>", unsafe_allow_html=True)
                        st.image(img, use_container_width=True)
                        st.markdown("</div>", unsafe_allow_html=True)

                        st.markdown(f"""
                        <div style='margin-top:0.75rem; text-align:center;'>
                            <span class='meta-pill'>🤖 {model_choice}</span>
                            <span class='meta-pill'>🎨 {style_choice}</span>
                        </div>
                        """, unsafe_allow_html=True)

                        buf = BytesIO()
                        img.save(buf, format="PNG")
                        st.download_button("⬇ Download PNG", data=buf.getvalue(),
                                           file_name="grok_image.png", mime="image/png")
                        st.session_state.history.insert(0, {"prompt": prompt, "style": style_choice, "image": img})

                    else:
                        cols = st.columns(min(len(items), 2))
                        for i, item in enumerate(items):
                            img = load_image(item, response_format)
                            with cols[i % 2]:
                                st.image(img, use_container_width=True)
                                buf = BytesIO()
                                img.save(buf, format="PNG")
                                st.download_button(
                                    f"⬇ Image {i+1}", data=buf.getvalue(),
                                    file_name=f"grok_image_{i+1}.png",
                                    mime="image/png", key=f"dl_{i}",
                                )
                            st.session_state.history.insert(0, {"prompt": prompt, "style": style_choice, "image": img})

                    if len(st.session_state.history) > 6:
                        st.session_state.history = st.session_state.history[:6]

            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Something went wrong: {e}")

# ── History ───────────────────────────────────────────────────────────────────
if st.session_state.history:
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.markdown("<p style='color:#888; font-size:0.8rem; letter-spacing:0.1em; text-transform:uppercase;'>Recent generations</p>", unsafe_allow_html=True)
    cols = st.columns(min(len(st.session_state.history), 3))
    for i, item in enumerate(st.session_state.history[:3]):
        with cols[i]:
            st.image(item["image"], use_container_width=True)
            st.caption(f"{item['prompt'][:40]}…" if len(item['prompt']) > 40 else item['prompt'])
