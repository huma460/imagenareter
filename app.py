import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import urllib.parse
import time

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

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: #0d0d0f;
    color: #f0ede8;
}

h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
}

.title-block {
    text-align: center;
    padding: 2.5rem 0 1rem 0;
}

.title-block h1 {
    font-size: 3rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #f0ede8 0%, #c9a96e 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.25rem;
}

.title-block p {
    color: #888;
    font-size: 1rem;
    font-weight: 300;
}

.stTextArea textarea {
    background: #1a1a1e !important;
    border: 1px solid #2a2a30 !important;
    border-radius: 12px !important;
    color: #f0ede8 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    padding: 1rem !important;
    resize: none !important;
    transition: border-color 0.2s;
}

.stTextArea textarea:focus {
    border-color: #c9a96e !important;
    box-shadow: 0 0 0 2px rgba(201,169,110,0.15) !important;
}

.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #c9a96e, #a07840) !important;
    color: #0d0d0f !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.04em !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.75rem 2rem !important;
    cursor: pointer !important;
    transition: opacity 0.2s !important;
}

.stButton > button:hover {
    opacity: 0.85 !important;
}

div[data-testid="stSelectbox"] > div,
div[data-testid="stSelectbox"] label {
    color: #f0ede8 !important;
}

div[data-testid="stSelectbox"] > div > div {
    background: #1a1a1e !important;
    border: 1px solid #2a2a30 !important;
    border-radius: 10px !important;
    color: #f0ede8 !important;
}

.stSlider > div > div {
    background: #c9a96e !important;
}

label, .stSlider label, .stSelectbox label {
    color: #aaa !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}

.image-card {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid #2a2a30;
    margin-top: 1.5rem;
    background: #1a1a1e;
}

.meta-pill {
    display: inline-block;
    background: #1a1a1e;
    border: 1px solid #2a2a30;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.78rem;
    color: #888;
    margin: 4px;
}

.section-divider {
    border: none;
    border-top: 1px solid #1e1e24;
    margin: 1.5rem 0;
}

.history-thumb {
    border-radius: 10px;
    border: 1px solid #2a2a30;
    overflow: hidden;
}

/* Hide Streamlit branding */
#MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="title-block">
    <h1>✦ Imagine</h1>
    <p>Turn words into images — no API key required</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ── Prompt input ──────────────────────────────────────────────────────────────
prompt = st.text_area(
    "PROMPT",
    placeholder="A misty Japanese shrine at dawn, volumetric light, ultra-detailed oil painting...",
    height=110,
)

# ── Style presets ─────────────────────────────────────────────────────────────
STYLES = {
    "None": "",
    "Photorealistic": "photorealistic, DSLR, sharp focus, natural lighting",
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
    aspect = st.selectbox("ASPECT RATIO", ["Square (1:1)", "Portrait (2:3)", "Landscape (3:2)", "Wide (16:9)"])

ASPECT_MAP = {
    "Square (1:1)":    (1024, 1024),
    "Portrait (2:3)":  (768, 1152),
    "Landscape (3:2)": (1152, 768),
    "Wide (16:9)":     (1344, 768),
}
width, height_px = ASPECT_MAP[aspect]

# ── Negative prompt ───────────────────────────────────────────────────────────
with st.expander("⚙️ Advanced options"):
    negative = st.text_input(
        "NEGATIVE PROMPT",
        value="blurry, distorted, low quality, watermark, text, ugly, bad anatomy",
    )
    seed = st.number_input("SEED (0 = random)", min_value=0, max_value=999999, value=0)

st.markdown("<br>", unsafe_allow_html=True)

# ── Generate ──────────────────────────────────────────────────────────────────
generate_btn = st.button("✦ Generate Image")

def build_full_prompt(prompt, style_key):
    base = prompt.strip()
    suffix = STYLES.get(style_key, "")
    return f"{base}, {suffix}" if suffix else base

def fetch_image(full_prompt, neg_prompt, w, h, seed_val):
    """
    Uses Pollinations.ai — free, no API key, supports stable diffusion.
    Falls back to a placeholder on error.
    """
    encoded = urllib.parse.quote(full_prompt)
    neg_encoded = urllib.parse.quote(neg_prompt)
    seed_param = seed_val if seed_val > 0 else int(time.time()) % 999999

    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width={w}&height={h}&seed={seed_param}"
        f"&negative={neg_encoded}&nologo=true&enhance=true"
    )
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return Image.open(BytesIO(response.content)), url

if generate_btn:
    if not prompt.strip():
        st.warning("Please enter a prompt first.")
    else:
        full_prompt = build_full_prompt(prompt, style_choice)

        with st.spinner("Generating your image…"):
            try:
                img, src_url = fetch_image(full_prompt, negative, width, height_px, seed)

                st.markdown("<div class='image-card'>", unsafe_allow_html=True)
                st.image(img, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

                # Meta info
                st.markdown(f"""
                <div style='margin-top:0.75rem; text-align:center;'>
                    <span class='meta-pill'>📐 {width}×{height_px}</span>
                    <span class='meta-pill'>🎨 {style_choice}</span>
                </div>
                """, unsafe_allow_html=True)

                # Download button
                buf = BytesIO()
                img.save(buf, format="PNG")
                st.download_button(
                    "⬇ Download PNG",
                    data=buf.getvalue(),
                    file_name="imagine_output.png",
                    mime="image/png",
                )

                # Save to history
                st.session_state.history.insert(0, {
                    "prompt": prompt,
                    "style": style_choice,
                    "image": img,
                    "size": f"{width}×{height_px}",
                })
                if len(st.session_state.history) > 6:
                    st.session_state.history = st.session_state.history[:6]

            except Exception as e:
                st.error(f"Generation failed: {e}\n\nTry again — free APIs occasionally time out.")

# ── History ───────────────────────────────────────────────────────────────────
if st.session_state.history:
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.markdown("<p style='color:#888; font-size:0.8rem; letter-spacing:0.1em; text-transform:uppercase;'>Recent generations</p>", unsafe_allow_html=True)

    cols = st.columns(min(len(st.session_state.history), 3))
    for i, item in enumerate(st.session_state.history[:3]):
        with cols[i]:
            st.image(item["image"], use_container_width=True)
            st.caption(f"{item['prompt'][:40]}…" if len(item['prompt']) > 40 else item['prompt'])
