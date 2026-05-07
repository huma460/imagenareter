# ✦ Imagine — AI Image Generator

A free, no-API-key image generator built with Streamlit and powered by [Pollinations.ai](https://pollinations.ai).

## Features

- 🎨 8 style presets (photorealistic, anime, cinematic, pixel art, etc.)
- 📐 4 aspect ratios
- 🔢 Seed control for reproducibility
- ⚙️ Negative prompt support
- 🕐 Generation history (last 6 images)
- ⬇️ One-click PNG download
- 🆓 Completely free — no API key needed

---

## Deploy to Streamlit Cloud (5 minutes)

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 2. Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **"New app"**
4. Select your repo, branch (`main`), and set main file to `app.py`
5. Click **"Deploy"** — done!

No secrets or environment variables needed.

---

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Project Structure

```
image-generator/
├── app.py                  # Main application
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── config.toml         # Theme & server config
└── README.md
```

---

## How it works

Prompts are sent to **Pollinations.ai**, a free public image generation API backed by Stable Diffusion. No account or API key required. Images are generated on-demand and are not stored.

> **Note:** Free APIs can occasionally be slow or time out. If generation fails, wait a moment and try again.
