"""
YouTube AI Agent — Professional Streamlit Dashboard
Full UI with all pages working end-to-end.
"""

from pathlib import Path
from collections import Counter
from datetime import datetime, timedelta
import json
import sys
import time

import re
import urllib.parse
import urllib.request
import altair as alt
import pandas as pd
import streamlit as st

# =========================
# PATHS
# =========================

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

OUTPUT_DIR = ROOT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
USED_FILE     = OUTPUT_DIR / "used_topics.json"
SETTINGS_FILE = OUTPUT_DIR / "settings.json"
SCRIPT_FILE   = OUTPUT_DIR / "script.json"
MANUAL_SCRIPT_FILE = OUTPUT_DIR / "manual_script.txt"
YOUTUBE_META_FILE  = OUTPUT_DIR / "youtube_meta.json"
AUDIO_FILE    = ROOT_DIR / "data" / "audio" / "generated_voice.mp3"
THUMB_FILE    = OUTPUT_DIR / "thumbnail.jpg"

# =========================
# CONSTANTS
# =========================

LANG_MAP = {
    "Azərbaycan dili": "Azerbaijani",
    "English": "English",
    "Türkçe": "Turkish",
    "Русский": "Russian",
    "Deutsch": "German",
}

MUSIC_OPTIONS   = ["Cinematic", "Documentary", "Technology", "Emotional", "Suspense", "Inspirational", "No Music"]
EFFECT_OPTIONS  = ["Whoosh", "Impact", "Hit", "Door", "Rain", "Fire", "Electricity", "Wind", "Footsteps", "Notification"]
DURATION_OPTIONS = ["0.5 saniyə", "1 saniyə", "2 saniyə", "3 saniyə", "5 saniyə"]
VISUAL_SOURCES  = ["Stock Footage (Pixabay)", "AI Image Generator", "AI Video Generator"]
VISUAL_STYLES   = ["Cinematic", "Realistic", "Documentary", "3D", "Anime", "Minimal"]
EDITING_OPTIONS = ["Automatic Editing", "Manual Editing", "Cinematic Editing", "Shorts Editing", "Documentary Editing"]
PRIVACY_OPTIONS = ["private", "unlisted", "public"]

PAGES = [
    "🏠 Dashboard",
    "📁 Layihələr",
    "📝 Senaryo",
    "🎙️ Ses",
    "🎵 Musiqi",
    "🔊 Ses Efektləri",
    "🎥 Görseller",
    "✂️ Düzenleme",
    "🖼️ Küçük Çizim",
    "📤 YouTube",
]

PAGE_LABELS = {
    "🏠 Dashboard":       "🏠  Əsas Səhifə",
    "📁 Layihələr":       "📁  Layihələr",
    "📝 Senaryo":         "🎬  Video Yarat",
    "🎙️ Ses":            "🎧  Səs & Dublaj",
    "🔊 Ses Efektləri":   "✨  Effektlər",
    "🎵 Musiqi":          "🎵  Musiqi",
    "🎥 Görseller":       "🎞️  Görseller",
    "✂️ Düzenleme":       "✂️  Düzənləmə",
    "🖼️ Küçük Çizim":    "🖼️  Küçük Çizim",
    "📤 YouTube":         "📤  YouTube",
}

PAGE_DESCRIPTIONS = {
    "🏠 Dashboard":       "Statistika və ümumi baxış",
    "📁 Layihələr":       "Videolar və mövzular",
    "📝 Senaryo":         "AI ilə ssenari yarat",
    "🎙️ Ses":            "Səs & Dublaj yaradın",
    "🔊 Ses Efektləri":   "Vizual effektlər",
    "🎵 Musiqi":          "Fon musiqisi",
    "🎥 Görseller":       "Kliplər & şəkillər",
    "✂️ Düzenleme":       "Montaj seçimləri",
    "🖼️ Küçük Çizim":    "Thumbnail yarat",
    "📤 YouTube":         "Yükləmə ayarları",
}

VOICE_OPTIONS = {
    "🇦🇿 Babək (AZ)":        "az-AZ-BabekNeural",
    "🇦🇿 Banu (AZ)":         "az-AZ-BanuNeural",
    "🇹🇷 Ahmet (TR)":        "tr-TR-AhmetNeural",
    "🇹🇷 Emel (TR)":         "tr-TR-EmelNeural",
    "🇺🇸 Guy (EN)":          "en-US-GuyNeural",
    "🇺🇸 Jenny (EN)":        "en-US-JennyNeural",
    "🇺🇸 Christopher (EN)":  "en-US-ChristopherNeural",
    "🇷🇺 Dmitry (RU)":       "ru-RU-DmitryNeural",
    "🇩🇪 Conrad (DE)":       "de-DE-ConradNeural",
}

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="YouTube AI Agent",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# CUSTOM CSS & SPLASH PRELOADER
# =========================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    /* Dərin Tünd Yaşıl (Deep Forest Green & Cyber Emerald) */
    --bg-base:      #050c08;
    --bg-surface:   #09150e;
    --bg-surface-2: #0e2016;
    --bg-card:      rgba(10, 24, 16, 0.82);
    --border:       rgba(34, 197, 94, 0.12);
    --border-hover: rgba(34, 197, 94, 0.4);
    
    /* Primary Accent: Forest Emerald */
    --accent:       #15803d;
    --accent-light: #22c55e;
    --accent-glow:  rgba(34, 197, 94, 0.28);
    --teal-dark:    #0f766e;
    --mint:         #4ade80;
    
    --text-primary:   #f0fdf4;
    --text-secondary: #86efac;
    --text-muted:     #4b7256;
    
    --radius-lg: 16px;
    --radius-md: 12px;
    --radius-sm: 8px;
}

/* ── PRELOADER / SPLASH SCREEN ── */
#app-splash-preloader {
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    background: radial-gradient(circle at center, #0b1e13 0%, #030704 80%);
    z-index: 9999999;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    pointer-events: none;
    animation: splashFadeOut 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards 1.7s;
}

@keyframes splashFadeOut {
    0% { opacity: 1; visibility: visible; }
    99% { opacity: 0; visibility: visible; }
    100% { opacity: 0; visibility: hidden; display: none; }
}

.splash-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
    animation: splashScaleIn 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes splashScaleIn {
    0% { opacity: 0; transform: scale(0.88); }
    100% { opacity: 1; transform: scale(1); }
}

.splash-logo {
    width: 72px; height: 72px;
    background: linear-gradient(135deg, #15803d, #22c55e);
    border-radius: 20px;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 0 45px rgba(34, 197, 94, 0.5), inset 0 0 15px rgba(255, 255, 255, 0.2);
    animation: pulseLogo 1.6s ease-in-out infinite alternate;
}

@keyframes pulseLogo {
    0% { transform: scale(1); box-shadow: 0 0 30px rgba(34, 197, 94, 0.4); }
    100% { transform: scale(1.06); box-shadow: 0 0 55px rgba(34, 197, 94, 0.7); }
}

.splash-title {
    font-size: 26px;
    font-weight: 800;
    color: #f0fdf4;
    letter-spacing: -0.02em;
    font-family: 'Plus Jakarta Sans', sans-serif;
}
.splash-title span {
    background: linear-gradient(90deg, #4ade80, #10b981);
    -webkit-background-clip: text;
    color: transparent;
}

.splash-bar-track {
    width: 220px;
    height: 4px;
    background: rgba(34, 197, 94, 0.15);
    border-radius: 999px;
    overflow: hidden;
    margin-top: 4px;
    position: relative;
}

.splash-bar-fill {
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg, #15803d, #4ade80);
    border-radius: 999px;
    box-shadow: 0 0 12px #22c55e;
    animation: splashFill 1.5s cubic-bezier(0.65, 0, 0.35, 1) forwards;
}

@keyframes splashFill {
    0% { width: 0%; }
    40% { width: 55%; }
    80% { width: 88%; }
    100% { width: 100%; }
}

.splash-subtitle {
    font-size: 13px;
    color: #86efac;
    opacity: 0.8;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    font-weight: 500;
}

/* ── Smooth Fade & Slide In Animations ── */
@keyframes fadeInUp {
    0% { opacity: 0; transform: translateY(14px); }
    100% { opacity: 1; transform: translateY(0); }
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    letter-spacing: -0.01em;
}

.stApp {
    background: var(--bg-base);
    background-image:
        radial-gradient(ellipse 70% 45% at 50% -10%, rgba(21, 128, 61, 0.22) 0%, transparent 70%),
        radial-gradient(ellipse 55% 35% at 90% 90%, rgba(15, 118, 110, 0.14) 0%, transparent 65%);
    animation: fadeInUp 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

.block-container {
    padding: 1.5rem 2.2rem 3rem 2.2rem !important;
    max-width: 1380px !important;
    animation: fadeInUp 0.55s cubic-bezier(0.16, 1, 0.3, 1);
}

/* ── HEADINGS ── */
h1 { color: var(--text-primary) !important; font-weight: 800 !important; font-size: 2rem !important; margin-bottom: 4px !important; letter-spacing: -0.03em !important; }
h2 { color: var(--text-primary) !important; font-weight: 700 !important; letter-spacing: -0.02em !important; }
h3 { color: var(--text-primary) !important; font-weight: 600 !important; }
p  { color: #9cdab1 !important; line-height: 1.6 !important; }

/* ── MODERN GLASS CARDS ── */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--bg-card) !important;
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4) !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: var(--border-hover) !important;
    box-shadow: 0 14px 40px rgba(34, 197, 94, 0.12) !important;
    transform: translateY(-1px);
}

/* ── HIGH PERFORMANCE BUTTONS ── */
div.stButton > button {
    background: linear-gradient(135deg, #166534 0%, #15803d 50%, #22c55e 100%) !important;
    color: #ffffff !important;
    border: 1px solid rgba(74, 222, 128, 0.25) !important;
    border-radius: var(--radius-md) !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    letter-spacing: 0.01em !important;
    padding: 0.6rem 1.4rem !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    box-shadow: 0 4px 18px rgba(22, 101, 52, 0.4) !important;
}
div.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 26px rgba(34, 197, 94, 0.45) !important;
    filter: brightness(1.12) !important;
}
div.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── REFINED CLEAN INPUTS ── */
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
div[data-baseweb="textarea"] > div {
    background: rgba(9, 21, 14, 0.9) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
    transition: all 0.2s ease !important;
}
div[data-baseweb="input"] > div:focus-within,
div[data-baseweb="select"] > div:focus-within,
div[data-baseweb="textarea"] > div:focus-within {
    border-color: var(--accent-light) !important;
    box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.2) !important;
}
input, textarea, select { color: var(--text-primary) !important; font-size: 14px !important; }

/* ── LABELS ── */
label[data-testid="stWidgetLabel"] p,
div[data-testid="stSelectbox"] label p,
div[data-testid="stSlider"] label p,
div[data-testid="stTextInput"] label p,
div[data-testid="stTextArea"] label p {
    color: #86efac !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}

/* ── PILL RADIO BUTTONS ── */
[data-testid="stMain"] div[role="radiogroup"] > label > div:first-child { display: none !important; }
[data-testid="stMain"] div[role="radiogroup"] > label {
    padding: 8px 20px;
    border-radius: 999px;
    margin-right: 8px;
    margin-bottom: 6px;
    background: rgba(9, 21, 14, 0.7);
    border: 1px solid var(--border);
    color: #86efac;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
[data-testid="stMain"] div[role="radiogroup"] > label:hover {
    border-color: rgba(34, 197, 94, 0.5);
    color: var(--text-primary);
    transform: translateY(-1px);
}
[data-testid="stMain"] div[role="radiogroup"] > label:has(input:checked) {
    background: linear-gradient(135deg, #15803d, #22c55e);
    color: #ffffff;
    border-color: transparent;
    box-shadow: 0 4px 16px rgba(34, 197, 94, 0.35);
}

/* ── RANGE SLIDER ── */
div[data-testid="stSlider"] > div > div > div {
    background: linear-gradient(90deg, #15803d, #4ade80) !important;
}
div[data-testid="stSlider"] [data-testid="stThumbValue"] {
    color: var(--text-primary) !important;
}

/* ── CHECKBOX ── */
input[type="checkbox"] { accent-color: var(--accent-light) !important; }

/* ── SELECT DROPDOWN POPOVER ── */
div[data-baseweb="popover"] { background: var(--bg-surface-2) !important; border: 1px solid var(--border) !important; border-radius: var(--radius-md) !important; }
li[role="option"] { color: #86efac !important; background: var(--bg-surface-2) !important; font-size: 13px !important; }
li[role="option"]:hover { background: rgba(34, 197, 94, 0.15) !important; color: #ffffff !important; }

/* ── CLEAN STATUS ALERTS ── */
div[data-testid="stInfo"] { background: rgba(15, 118, 110, 0.12) !important; border: 1px solid rgba(20, 184, 166, 0.3) !important; border-radius: var(--radius-md) !important; }
div[data-testid="stSuccess"] { background: rgba(22, 101, 52, 0.18) !important; border: 1px solid rgba(34, 197, 94, 0.35) !important; border-radius: var(--radius-md) !important; }
div[data-testid="stWarning"] { background: rgba(180, 83, 9, 0.14) !important; border: 1px solid rgba(245, 158, 11, 0.35) !important; border-radius: var(--radius-md) !important; }
div[data-testid="stError"] { background: rgba(153, 27, 27, 0.15) !important; border: 1px solid rgba(239, 68, 68, 0.35) !important; border-radius: var(--radius-md) !important; }

/* ── TAB BAR ── */
div[data-baseweb="tab-list"] {
    gap: 8px !important;
    border-bottom: 1px solid var(--border) !important;
}
div[data-baseweb="tab"] {
    padding: 8px 16px !important;
    border-radius: var(--radius-sm) !important;
    color: #86efac !important;
    font-weight: 500 !important;
}
div[data-baseweb="tab"][aria-selected="true"] {
    color: var(--mint) !important;
    border-bottom: 2px solid var(--accent-light) !important;
}

/* ─────────────── SIDEBAR STYLING ─────────────── */
section[data-testid="stSidebar"] {
    background: #040906 !important;
    border-right: 1px solid var(--border) !important;
    padding: 0 !important;
}

section[data-testid="stSidebar"] div.stButton > button {
    width: 100% !important;
    justify-content: flex-start !important;
    text-align: left !important;
    border-radius: var(--radius-md) !important;
    border: none !important;
    background: transparent !important;
    color: #86efac !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    padding: 10px 14px !important;
    box-shadow: none !important;
    transform: none !important;
    transition: all 0.18s ease !important;
    margin-bottom: 3px !important;
}
section[data-testid="stSidebar"] div.stButton > button:hover {
    background: rgba(255, 255, 255, 0.04) !important;
    color: var(--text-primary) !important;
    transform: translateX(3px) !important;
}
section[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, rgba(21, 128, 61, 0.25), rgba(34, 197, 94, 0.1)) !important;
    color: var(--mint) !important;
    border-left: 3px solid var(--accent-light) !important;
    padding-left: 12px !important;
    font-weight: 600 !important;
    box-shadow: none !important;
}

/* ─────────────── CUSTOM COMPONENTS ─────────────── */
.sidebar-logo {
    display: flex; align-items: center; gap: 12px;
    padding: 22px 18px 12px 18px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 14px;
}
.sidebar-logo-icon {
    width: 32px; height: 23px; background: #ff0033;
    border-radius: 6px; display: flex; align-items: center; justify-content: center;
    box-shadow: 0 4px 12px rgba(255, 0, 51, 0.3);
}
.sidebar-logo-icon::after {
    content: ""; border-left: 9px solid #fff;
    border-top: 5.5px solid transparent; border-bottom: 5.5px solid transparent; margin-left: 2px;
}
.sidebar-logo-text { font-size: 15px; font-weight: 700; color: var(--text-primary); }
.sidebar-logo-text span { background: linear-gradient(90deg, #4ade80, #15803d); -webkit-background-clip: text; color: transparent; }
.sidebar-footer { padding: 16px; margin-top: auto; border-top: 1px solid var(--border); }
.sidebar-footer p { font-size: 12px; color: var(--text-muted); line-height: 1.6; margin: 0; }

.page-header { margin-bottom: 24px; animation: fadeInUp 0.4s ease; }
.page-header h1 { margin: 0 0 4px 0 !important; }
.page-header p { margin: 0; font-size: 14px; color: #86efac; }

.hero-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(21, 128, 61, 0.18); border: 1px solid rgba(34, 197, 94, 0.35);
    border-radius: 999px; padding: 5px 14px; font-size: 12px; color: var(--mint);
    font-weight: 600; letter-spacing: 0.02em; margin-bottom: 16px;
}
.hero-title { font-size: 2.8rem !important; font-weight: 800 !important; line-height: 1.15 !important; color: var(--text-primary) !important; letter-spacing: -0.03em !important; }
.hero-title span { background: linear-gradient(90deg, #4ade80, #22c55e); -webkit-background-clip: text; color: transparent; }
.hero-sub { color: #86efac !important; font-size: 15px !important; line-height: 1.7 !important; margin: 0 !important; }

/* ── STAT CARDS ── */
.stat-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg); padding: 18px 20px;
    transition: all 0.25s ease;
}
.stat-card:hover {
    border-color: rgba(34, 197, 94, 0.45);
    box-shadow: 0 8px 24px rgba(34, 197, 94, 0.1);
    transform: translateY(-2px);
}
.stat-icon { font-size: 22px; margin-bottom: 8px; }
.stat-num { font-size: 28px; font-weight: 800; color: var(--text-primary); margin: 0; letter-spacing: -0.02em; }
.stat-lbl { font-size: 12px; color: var(--text-muted); margin: 3px 0 0 0; font-weight: 500; }
.stat-delta { font-size: 11px; color: var(--mint); margin-top: 4px; font-weight: 500; }

/* ── SERVICE TILES ── */
.svc-icon { width: 42px; height: 42px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 20px; margin-bottom: 12px; }
.svc-title { font-size: 15px; font-weight: 600; color: var(--text-primary); margin: 0 0 6px 0; }
.svc-text { font-size: 13px; color: #86efac; opacity: 0.9; line-height: 1.5; margin: 0; }

.proj-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 11px 0; border-bottom: 1px solid var(--border);
}
.proj-row:last-child { border-bottom: none; }
.proj-title { font-size: 13px; font-weight: 500; color: var(--text-primary); margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 210px; }
.proj-meta  { font-size: 11px; color: var(--text-muted); margin: 2px 0 0 0; }
.badge-done { background: rgba(34, 197, 94, 0.16); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.35); border-radius: 999px; padding: 3px 10px; font-size: 11px; font-weight: 600; white-space: nowrap; }
.badge-wait { background: rgba(245, 158, 11, 0.16); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 999px; padding: 3px 10px; font-size: 11px; font-weight: 600; white-space: nowrap; }

.section-title { font-size: 15px; font-weight: 700; color: var(--text-primary); margin: 0; display: flex; align-items: center; gap: 8px; letter-spacing: -0.01em; }

.topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 0 20px 0; border-bottom: 1px solid var(--border); margin-bottom: 24px;
}
.topbar-logo { display: flex; align-items: center; gap: 10px; }
.topbar-logo-icon { width: 36px; height: 25px; background: #ff0033; border-radius: 7px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 14px rgba(255, 0, 51, 0.3); }
.topbar-logo-icon::after { content: ""; border-left: 10px solid #fff; border-top: 6px solid transparent; border-bottom: 6px solid transparent; margin-left: 3px; }
.topbar-title { font-size: 20px; font-weight: 700; color: var(--text-primary); }
.topbar-title span { background: linear-gradient(90deg, #10b981, #06b6d4); -webkit-background-clip: text; color: transparent; }
.topbar-status { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--text-muted); }
.status-dot { width: 7px; height: 7px; border-radius: 50%; background: #10b981; box-shadow: 0 0 8px rgba(16, 185, 129, 0.8); }

.step-badge { display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; border-radius: 50%; background: linear-gradient(135deg, #10b981, #06b6d4); color: #fff; font-size: 13px; font-weight: 700; flex-shrink: 0; }

.yt-upload-card { background: linear-gradient(145deg, rgba(255, 0, 51, 0.08), rgba(255, 0, 51, 0.02)); border: 1px solid rgba(255, 0, 51, 0.2); border-radius: var(--radius-lg); padding: 20px; }
.yt-logo { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
.yt-icon { width: 40px; height: 28px; background: #ff0033; border-radius: 8px; display: flex; align-items: center; justify-content: center; }
.yt-icon::after { content: ""; border-left: 11px solid #fff; border-top: 7px solid transparent; border-bottom: 7px solid transparent; margin-left: 3px; }
.yt-brand { font-size: 18px; font-weight: 700; color: var(--text-primary); }

.empty-state { text-align: center; padding: 40px 20px; color: var(--text-muted); }
.empty-state .icon { font-size: 42px; margin-bottom: 10px; }
.empty-state .label { font-size: 14px; line-height: 1.6; color: var(--text-secondary); }
</style>
""", unsafe_allow_html=True)

# =========================
# HELPERS
# =========================

def load_json(path, default):
    try:
        if path.exists():
            with open(path, encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default


def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"❌ Fayl yazılarkən xəta: {e}")
        return False


def save_setting(section, values):
    settings = load_json(SETTINGS_FILE, {})
    settings[section] = values
    save_json(SETTINGS_FILE, settings)


def get_setting(section, key, default):
    return load_json(SETTINGS_FILE, {}).get(section, {}).get(key, default)


def pick_index(options, saved):
    return options.index(saved) if saved in options else 0


def all_videos():
    return sorted(OUTPUT_DIR.glob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)


def latest_video():
    videos = all_videos()
    return videos[0] if videos else None


def last_title():
    result = st.session_state.get("last_result")
    if result:
        return result.get("title", "")
    return load_json(YOUTUBE_META_FILE, {}).get("title", "")


def go_to(page_name):
    st.session_state["page"] = page_name


def daily_series(days=30):
    today = datetime.now().date()
    keys = [today - timedelta(days=i) for i in range(days - 1, -1, -1)]
    counts = Counter(datetime.fromtimestamp(v.stat().st_mtime).date() for v in all_videos())
    labels = [k.strftime("%d.%m") for k in keys]
    values = [counts.get(k, 0) for k in keys]
    return labels, values


def area_chart(labels, values, height=180):
    df = pd.DataFrame({"label": labels, "value": values})
    axis_style = dict(
        labelColor="#6b7597",
        labelFontSize=10,
        tickColor="transparent",
        domain=False,
        gridColor="#1a2340",
    )
    base = alt.Chart(df).encode(
        x=alt.X("label:N", sort=labels, title=None,
                axis=alt.Axis(**axis_style, labelAngle=0, labelOverlap="parity")),
        y=alt.Y("value:Q", title=None,
                axis=alt.Axis(**axis_style, format="d", tickMinStep=1)),
        tooltip=[
            alt.Tooltip("label:N", title="Tarix"),
            alt.Tooltip("value:Q", title="Video sayı"),
        ],
    )
    area = base.mark_area(
        interpolate="monotone",
        color=alt.Gradient(
            gradient="linear",
            stops=[
                alt.GradientStop(color="#15803d", offset=0),
                alt.GradientStop(color="#4ade80", offset=1),
            ],
            x1=1, x2=1, y1=1, y2=0,
        ),
        opacity=0.4,
        line={"color": "#22c55e", "strokeWidth": 2.5},
    )
    return (
        area.properties(height=height)
        .configure_view(strokeWidth=0)
        .configure(background="transparent")
    )


def recent_projects(limit=5):
    topics = load_json(USED_FILE, [])
    videos = all_videos()
    rows = []
    for i, topic in enumerate(reversed(topics)):
        if len(rows) >= limit:
            break
        done = i < len(videos)
        when = ""
        if done:
            delta = datetime.now() - datetime.fromtimestamp(videos[i].stat().st_mtime)
            hours = int(delta.total_seconds() // 3600)
            when = f"{hours} saat əvvəl" if hours < 24 else f"{hours // 24} gün əvvəl"
        rows.append((topic, done, when))
    return rows


def format_size(path):
    sz = path.stat().st_size
    if sz < 1024:
        return f"{sz} B"
    elif sz < 1024 * 1024:
        return f"{sz/1024:.1f} KB"
    else:
        return f"{sz/(1024*1024):.1f} MB"


def try_import(module_name):
    """Try to import a module; return it or None."""
    import importlib
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None


def extract_youtube_video_id(url: str):
    """Extract 11-char YouTube video ID from various URL patterns."""
    if not url:
        return None
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/|shorts\/|youtu\.be\/)([0-9A-Za-z_-]{11})',
    ]
    for p in patterns:
        m = re.search(p, url.strip())
        if m:
            return m.group(1)
    return None


def get_youtube_video_info(url: str):
    """Fetch video title and author using YouTube oEmbed endpoint (no API key required)."""
    vid = extract_youtube_video_id(url)
    if not vid:
        return None
    try:
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid}&format=json"
        req = urllib.request.Request(
            oembed_url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            data["video_id"] = vid
            data["thumbnail_url"] = f"https://img.youtube.com/vi/{vid}/hqdefault.jpg"
            data["canonical_url"] = f"https://www.youtube.com/watch?v={vid}"
            return data
    except Exception:
        return {
            "video_id": vid,
            "title": f"YouTube Video ({vid})",
            "author_name": "YouTube",
            "thumbnail_url": f"https://img.youtube.com/vi/{vid}/hqdefault.jpg",
            "canonical_url": f"https://www.youtube.com/watch?v={vid}",
        }

# =========================
# SESSION STATE DEFAULTS
# =========================

st.session_state.setdefault("page", PAGES[0])
st.session_state.setdefault("last_result", None)
st.session_state.setdefault("script_data", None)
st.session_state.setdefault("selected_effects", [])
st.session_state.setdefault("selected_music", get_setting("music", "style", MUSIC_OPTIONS[0]))
st.session_state.setdefault("splash_shown", False)

# =========================
# SPLASH SCREEN PRELOADER
# =========================

if not st.session_state["splash_shown"]:
    st.session_state["splash_shown"] = True
    st.markdown("""
    <div id="app-splash-preloader">
        <div class="splash-content">
            <div class="splash-logo">
                <svg viewBox="0 0 40 40" width="38" height="38">
                    <rect x="5" y="10" width="30" height="20" rx="6" fill="#f0fdf4"/>
                    <path d="M17 15 L17 25 L25 20 Z" fill="#15803d"/>
                </svg>
            </div>
            <div class="splash-title">YouTube <span>AI Agent</span></div>
            <div class="splash-subtitle">Süni İntellekt Sistemi Yüklənir...</div>
            <div class="splash-bar-track">
                <div class="splash-bar-fill"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# =========================
# SIDEBAR
# =========================

with st.sidebar:
    # Logo
    st.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-logo-icon"></div>
        <div class="sidebar-logo-text">YouTube <span>AI Agent</span></div>
    </div>
    """, unsafe_allow_html=True)

    # Nav sections
    for name in PAGES:
        is_active = st.session_state["page"] == name
        st.button(
            PAGE_LABELS[name],
            key=f"nav_{name}",
            on_click=go_to,
            args=(name,),
            type="primary" if is_active else "secondary",
            use_container_width=True,
        )

    # Footer
    st.markdown("""
    <div class="sidebar-footer">
        <p>⚡ Süni intellektlə daha yaxşı videolar yaradın.<br><br>
        <span style="color:#4b5563;font-size:11px">v2.0 · YouTube AI Agent</span></p>
    </div>
    """, unsafe_allow_html=True)

page = st.session_state["page"]

# ══════════════════════════════════════════════
#  🏠  DASHBOARD
# ══════════════════════════════════════════════

if page == "🏠 Dashboard":

    # Top bar
    st.markdown("""
    <div class="topbar">
        <div class="topbar-logo">
            <div class="topbar-logo-icon"></div>
            <div class="topbar-title">YouTube <span>AI Agent</span></div>
        </div>
        <div class="topbar-status">
            <div class="status-dot"></div>
            Sistem aktiv
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Hero
    hero_l, hero_r = st.columns([5, 4], gap="large")
    with hero_l:
        st.markdown("""
        <div class="hero-badge">✦ AI-powered video yaradıcısı</div>
        <h1 class="hero-title">YouTube üçün<br><span>Peşəkar Videolar</span></h1>
        <p class="hero-sub">İdeyadan bitmiş videoya qədər — senaryo, səs, görüntü<br>
        və yükləmə — hamısı bir platformada.</p>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        btn_cols = st.columns([2, 1])
        with btn_cols[0]:
            st.button("✦ Yeni Layihə Başlat →", key="new_proj_hero",
                      on_click=go_to, args=("📝 Senaryo",), use_container_width=True)
        with btn_cols[1]:
            st.button("📁 Layihələr", key="go_projects_hero",
                      on_click=go_to, args=("📁 Layihələr",), use_container_width=True)

    with hero_r:
        st.markdown("""
        <div style="display:flex;justify-content:center;padding:10px 0">
        <svg viewBox="0 0 300 230" width="100%" style="max-width:340px;opacity:0.95">
          <defs>
            <radialGradient id="rg1" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stop-color="#10b981" stop-opacity="0.35"/>
              <stop offset="100%" stop-color="#10b981" stop-opacity="0"/>
            </radialGradient>
            <linearGradient id="lg1" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#10b981"/>
              <stop offset="100%" stop-color="#06b6d4"/>
            </linearGradient>
          </defs>
          <ellipse cx="150" cy="115" rx="130" ry="85" fill="url(#rg1)"/>
          <ellipse cx="150" cy="115" rx="125" ry="80" fill="none" stroke="#10b981" stroke-opacity=".25" stroke-width="1.5"/>
          <rect x="82" y="58" width="136" height="90" rx="20" fill="#ff0033"/>
          <rect x="82" y="58" width="136" height="90" rx="20" fill="rgba(0,0,0,0.12)"/>
          <path d="M132 83 L132 123 L168 103 Z" fill="#fff"/>
          <rect x="16" y="38" width="50" height="50" rx="14" fill="#0d1424" stroke="#10b981" stroke-width="1.5"/>
          <text x="41" y="70" font-size="22" text-anchor="middle" fill="#34d399">🎙</text>
          <rect x="236" y="140" width="50" height="50" rx="14" fill="#0d1424" stroke="#06b6d4" stroke-width="1.5"/>
          <text x="261" y="172" font-size="22" text-anchor="middle" fill="#06b6d4">🎵</text>
          <rect x="236" y="28" width="44" height="44" rx="12" fill="#0d1424" stroke="#10b981" stroke-width="1.5"/>
          <text x="258" y="56" font-size="18" text-anchor="middle" fill="#10b981">✨</text>
          <rect x="16" y="148" width="44" height="44" rx="12" fill="#0d1424" stroke="#06b6d4" stroke-width="1.5"/>
          <text x="38" y="176" font-size="18" text-anchor="middle" fill="#06b6d4">🎞</text>
          <line x1="66" y1="63" x2="82" y2="80" stroke="#10b981" stroke-opacity=".4" stroke-width="1.2"/>
          <line x1="236" y1="103" x2="218" y2="103" stroke="#06b6d4" stroke-opacity=".4" stroke-width="1.2"/>
          <line x1="236" y1="50" x2="218" y2="72" stroke="#10b981" stroke-opacity=".4" stroke-width="1.2"/>
          <line x1="60" y1="170" x2="82" y2="148" stroke="#06b6d4" stroke-opacity=".4" stroke-width="1.2"/>
        </svg>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick stats
    used_topics = load_json(USED_FILE, [])
    videos = all_videos()
    labels, values = daily_series(30)
    week_count = sum(values[-7:])

    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    stat_data = [
        ("🎬", str(len(videos)),    "Ümumi Videolar",   f"+{week_count} bu həftə"),
        ("📝", str(len(used_topics)), "Mövzular",        "Unikal mövzular"),
        ("🔊", "Var" if AUDIO_FILE.exists() else "Yox", "Səs Faylı", "generated_voice.mp3"),
        ("📅", str(week_count),     "Bu Həftə",        "Son 7 günün videaları"),
    ]
    for col, (icon, num, label, sub) in zip([stat_col1, stat_col2, stat_col3, stat_col4], stat_data):
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-icon">{icon}</div>
                <div class="stat-num">{num}</div>
                <div class="stat-lbl">{label}</div>
                <div class="stat-delta">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Services
    st.markdown('<div class="section-title" style="margin-bottom:16px">⚡ Xidmətlər</div>', unsafe_allow_html=True)
    services = [
        ("🎬", "Video Yarat",    "Mövzunu yaz, AI ssenari versin, görüntülər tapılsın.",    "📝 Senaryo",       "#10b981"),
        ("🎧", "Səs & Dublaj",  "Təbii neural səslərlə peşəkar dublaj yaradın.",              "🎙️ Ses",          "#06b6d4"),
        ("✨", "Effektlər",     "Vizual & səs effektləri ilə videonuzu canlandırın.",         "🔊 Ses Efektləri", "#3b82f6"),
        ("📈", "YouTube SEO",   "Başlıq, açıqlama, teq ilə videonu öndə göstərin.",          "📤 YouTube",       "#10b981"),
    ]
    svc_cols = st.columns(4, gap="small")
    for col, (icon, title, text, target, color) in zip(svc_cols, services):
        with col:
            with st.container(border=True):
                st.markdown(
                    f'<div class="svc-icon" style="background:{color}22;border:1px solid {color}44">'
                    f'<span style="font-size:20px">{icon}</span></div>'
                    f'<div class="svc-title">{title}</div>'
                    f'<div class="svc-text">{text}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
                st.button("Aç →", key=f"svc_{target}",
                          on_click=go_to, args=(target,), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Chart + Recent projects
    chart_col, recent_col = st.columns([3, 2], gap="large")

    with chart_col:
        with st.container(border=True):
            st.markdown("""
            <div class="section-header">
                <span class="section-title">📊 Video Statistikası <span style="font-size:12px;color:#6b7597;font-weight:500">(son 30 gün)</span></span>
            </div>
            """, unsafe_allow_html=True)
            if sum(values) == 0:
                st.markdown("""
                <div class="empty-state">
                    <div class="icon">📊</div>
                    <div class="label">Hələ video yoxdur.<br>Video yaradıldıqdan sonra qrafik burada görünəcək.</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.altair_chart(area_chart(labels, values, 180), use_container_width=True)

    with recent_col:
        with st.container(border=True):
            st.markdown('<div class="section-header">', unsafe_allow_html=True)
            hdr_l, hdr_r = st.columns([3, 2])
            with hdr_l:
                st.markdown('<span class="section-title">🕒 Son Layihələr</span>', unsafe_allow_html=True)
            with hdr_r:
                st.button("Hamısı →", key="see_all_dash",
                          on_click=go_to, args=("📁 Layihələr",), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            rows = recent_projects(5)
            if not rows:
                st.markdown("""
                <div class="empty-state">
                    <div class="icon">🗂️</div>
                    <div class="label">Hələ layihə yoxdur.</div>
                </div>""", unsafe_allow_html=True)
            for topic, done, when in rows:
                badge = f'<span class="badge-done">✓ Hazır</span>' if done else f'<span class="badge-wait">⏳ Hazırlanır</span>'
                st.markdown(f"""
                <div class="proj-row">
                    <div>
                        <div class="proj-title">{topic}</div>
                        <div class="proj-meta">{when}</div>
                    </div>
                    {badge}
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick video creator
    with st.container(border=True):
        st.markdown('<div class="section-title" style="margin-bottom:16px">🚀 Sürətli Video Yarat</div>', unsafe_allow_html=True)

        qc1, qc2, qc3 = st.columns([3, 2, 1])
        with qc1:
            q_topic = st.text_input("Video mövzusu",
                placeholder="Məsələn: Süni intellekt gələcəkdə işləri necə dəyişəcək?",
                key="dash_topic")
            q_niche = st.text_input("Niş (ixtiyari)",
                placeholder="Məsələn: Texnologiya, Tarix, Maliyyə",
                key="dash_niche")
        with qc2:
            q_lang = st.selectbox("Dil", list(LANG_MAP.keys()), key="dash_lang")
            q_fmt  = st.radio("Format", ["Shorts (9:16)", "Uzun (16:9)"],
                              key="dash_fmt", horizontal=True)
        with qc3:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            make_btn = st.button("🚀 Yarat", key="dash_make", use_container_width=True)

        if make_btn:
            if not q_topic.strip() and not q_niche.strip():
                st.warning("Mövzu və ya niş daxil edin.")
            else:
                agent = try_import("agent")
                if agent is None:
                    st.error("❌ `agent.py` tapılmadı. Zəhmət olmasa layihəyə əlavə edin.")
                else:
                    try:
                        with st.spinner("Video hazırlanır… bir neçə dəqiqə çəkə bilər."):
                            result = agent.make_one(
                                niche=q_niche.strip() or q_topic.strip(),
                                topic=q_topic.strip() or None,
                                language=LANG_MAP[q_lang],
                                fmt="shorts" if q_fmt.startswith("Shorts") else "long",
                            )
                        st.session_state["last_result"] = result
                        topics = load_json(USED_FILE, [])
                        if q_topic.strip() and q_topic.strip() not in topics:
                            topics.append(q_topic.strip())
                            save_json(USED_FILE, topics)
                        st.success("✅ Video hazırdır!")
                    except Exception as e:
                        st.error(f"❌ Xəta: {e}")

        result = st.session_state.get("last_result")
        if result:
            st.markdown("---")
            r1, r2 = st.columns([3, 2])
            with r1:
                st.markdown(f"**Mövzu:** {result.get('topic', '')}")
                st.markdown(f"**Başlıq:** {result.get('title', '')}")
            with r2:
                video_path = Path(result.get("video", ""))
                if video_path.exists():
                    with open(video_path, "rb") as vf:
                        st.download_button("⬇️ Videonu yüklə", vf,
                                           file_name=video_path.name,
                                           mime="video/mp4",
                                           use_container_width=True,
                                           key="dl_last_video")
            video_path = Path(result.get("video", ""))
            if video_path.exists():
                st.video(str(video_path))


# ══════════════════════════════════════════════
#  📁  LAYİHƏLƏR
# ══════════════════════════════════════════════

elif page == "📁 Layihələr":

    st.markdown("""
    <div class="page-header">
        <h1>📁 Layihələr</h1>
        <p>Yaradılmış videolar, mövzular və keçmiş layihələr.</p>
    </div>
    """, unsafe_allow_html=True)

    videos  = all_videos()
    topics  = load_json(USED_FILE, [])

    tab_vid, tab_top = st.tabs(["🎥 Videolar", "🧠 Mövzular"])

    with tab_vid:
        if not videos:
            st.markdown("""
            <div class="empty-state">
                <div class="icon">🎬</div>
                <div class="label">Hələ video yoxdur.<br>Dashboard-dan video yaradın.</div>
            </div>""", unsafe_allow_html=True)
            st.button("→ Video Yarat", on_click=go_to, args=("📝 Senaryo",), key="go_script_empty")
        else:
            st.markdown(f"**{len(videos)} video tapıldı**")
            st.markdown("")
            for v in videos[:50]:
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([4, 2, 2, 1])
                    when     = datetime.fromtimestamp(v.stat().st_mtime).strftime("%d.%m.%Y %H:%M")
                    size_str = format_size(v)
                    c1.markdown(f"**{v.name}**")
                    c2.markdown(f"<span style='color:#7b87aa'>{when}</span>", unsafe_allow_html=True)
                    c3.markdown(f"<span style='color:#7b87aa'>{size_str}</span>", unsafe_allow_html=True)
                    with open(v, "rb") as vf:
                        c4.download_button("⬇️", vf, file_name=v.name,
                                           mime="video/mp4", key=f"dl_{v.name}")
                    with st.expander("▶ Önizlə"):
                        st.video(str(v))

    with tab_top:
        if not topics:
            st.info("Hələ mövzu yoxdur.")
        else:
            rows = []
            for i, t in enumerate(reversed(topics)):
                rows.append({
                    "№": i + 1,
                    "Mövzu": t,
                    "Status": "✅ Tamamlandı" if i < len(videos) else "⏳ Hazırlanır",
                })
            st.dataframe(
                pd.DataFrame(rows),
                hide_index=True,
                use_container_width=True,
                column_config={
                    "№":     st.column_config.NumberColumn(width="small"),
                    "Mövzu": st.column_config.TextColumn(width="large"),
                    "Status": st.column_config.TextColumn(width="medium"),
                },
            )

            # clear button
            st.markdown("")
            if st.button("🗑️ Bütün mövzuları sil", key="clear_topics"):
                save_json(USED_FILE, [])
                st.success("Mövzular silindi.")
                st.rerun()


# ══════════════════════════════════════════════
#  📝  SENARYO
# ══════════════════════════════════════════════

elif page == "📝 Senaryo":

    st.markdown("""
    <div class="page-header">
        <h1>📝 Senaryo Studio</h1>
        <p>Ssenarinizi AI ilə yaradın və ya özünüz yazın.</p>
    </div>
    """, unsafe_allow_html=True)

    mode = st.radio("Üsul seç", ["🤖 AI ilə yarat", "🔗 YouTube Linkdən yarat", "✍️ Manual yaz"], horizontal=True, key="script_mode")

    st.markdown("")

    if mode == "🤖 AI ilə yarat":

        with st.container(border=True):
            st.markdown('<div class="section-title" style="margin-bottom:16px">⚙️ Parametrlər</div>', unsafe_allow_html=True)
            p1, p2 = st.columns(2)
            with p1:
                script_topic = st.text_input("🎯 Video mövzusu",
                    placeholder="Məsələn: Kvant kompüterləri necə işləyir?",
                    key="sc_topic")
                script_niche = st.text_input("🏷️ Niş",
                    placeholder="Məsələn: Texnologiya",
                    key="sc_niche")
            with p2:
                script_lang  = st.selectbox("🌐 Dil", list(LANG_MAP.keys()), key="sc_lang")
                script_fmt   = st.radio("📐 Format", ["Shorts (60 san)", "Uzun (5-10 dəq)"],
                                        horizontal=True, key="sc_fmt")

            gen_btn = st.button("✨ AI Senaryo Yarat", use_container_width=True, key="gen_script_btn")

        if gen_btn:
            if not script_topic.strip():
                st.warning("Mövzu daxil edin.")
            else:
                mod = try_import("write_bridge")
                if mod is None:
                    st.error("❌ `write_bridge.py` tapılmadı. Zəhmət olmasa layihəyə əlavə edin.")
                else:
                    try:
                        with st.spinner("AI ssenari yazır…"):
                            data = mod.generate_script(
                                script_topic.strip(),
                                script_niche.strip() or script_topic.strip(),
                                LANG_MAP[script_lang],
                            )
                        st.session_state["script_data"] = data
                        save_json(SCRIPT_FILE, data)
                        # save to used topics
                        topics = load_json(USED_FILE, [])
                        if script_topic.strip() not in topics:
                            topics.append(script_topic.strip())
                            save_json(USED_FILE, topics)
                        st.success("✅ Ssenari hazırdır!")
                    except Exception as e:
                        st.error(f"❌ Xəta: {e}")

        data = st.session_state.get("script_data") or load_json(SCRIPT_FILE, None)
        if data:
            st.markdown("---")
            st.markdown(f"### 🎬 {data.get('title', 'Başlıqsız')}")

            hook = data.get("hook", "")
            if hook:
                st.markdown(f"> 💡 **Hook:** {hook}")

            edited_scenes = []
            scenes = data.get("scenes", [])
            for i, scene in enumerate(scenes, start=1):
                with st.container(border=True):
                    sc1, sc2 = st.columns([1, 4])
                    with sc1:
                        st.markdown(f"""
                        <div style="display:flex;flex-direction:column;align-items:center;gap:6px;padding-top:4px">
                            <div class="step-badge">{i}</div>
                            <div style="font-size:11px;color:#7b87aa;text-align:center">{scene.get('visual','')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with sc2:
                        new_text = st.text_area(
                            f"Səhnə {i} — narrasyon",
                            value=scene.get("narration", ""),
                            key=f"scene_{i}",
                            height=90,
                        )
                        edited_scenes.append({**scene, "narration": new_text})

            if st.button("💾 Ssenaridəki dəyişiklikləri yadda saxla",
                         use_container_width=True, key="save_script"):
                data["scenes"] = edited_scenes
                st.session_state["script_data"] = data
                if save_json(SCRIPT_FILE, data):
                    st.success("✅ Yadda saxlanıldı!")

            st.markdown("")
            if st.button("🎧 Səs Studiosu →", on_click=go_to, args=("🎙️ Ses",), key="go_voice"):
                pass

    elif mode == "🔗 YouTube Linkdən yarat":

        with st.container(border=True):
            st.markdown('<div class="section-title" style="margin-bottom:14px">🎯 YouTube Linki ilə Oxşar Video & Ssenari Hazırla</div>', unsafe_allow_html=True)
            st.markdown("""
            <p style="font-size:13px;color:#7b87aa;margin-bottom:14px">
            İstədiyiniz hər hansı YouTube videosunun (və ya Shorts-un) linkini daxil edin. AI videonun mövzusunu analiz edəcək və həmin məzmuna uyğun yeni, unikal ssenari və ya tam video layihəsi hazırlayacaq.
            </p>
            """, unsafe_allow_html=True)

            yt_url_input = st.text_input(
                "🔗 YouTube Video / Shorts Linki",
                placeholder="https://www.youtube.com/watch?v=... və ya https://youtu.be/... və ya https://www.youtube.com/shorts/...",
                key="yt_clone_link"
            )

            c_yt1, c_yt2 = st.columns(2)
            with c_yt1:
                yt_clone_lang = st.selectbox("🌐 Hədəf Dil", list(LANG_MAP.keys()), key="yt_clone_lang")
            with c_yt2:
                yt_clone_fmt = st.radio("📐 Format", ["Shorts (9:16)", "Uzun video (16:9)"], horizontal=True, key="yt_clone_fmt")

            yt_clone_niche = st.text_input(
                "🏷️ Əlavə Niş / Kateqoriya (ixtiyari)",
                placeholder="Məsələn: Texnologiya, Motivasiya, Psixologiya, Maliyyə",
                key="yt_clone_niche"
            )

            # Video preview if valid URL is entered
            if yt_url_input.strip():
                vid_info = get_youtube_video_info(yt_url_input.strip())
                if vid_info:
                    st.markdown("---")
                    prev_c1, prev_c2 = st.columns([1, 2])
                    with prev_c1:
                        if vid_info.get("thumbnail_url"):
                            st.image(vid_info["thumbnail_url"], use_container_width=True)
                    with prev_c2:
                        st.markdown(f"**Orijinal Başlıq:** {vid_info.get('title', 'YouTube Video')}")
                        st.markdown(f"**Kanal / Müəllif:** {vid_info.get('author_name', 'Məlum deyil')}")
                        st.markdown(f"[▶ YouTube-da aç]({vid_info.get('canonical_url', yt_url_input.strip())})")

            st.markdown("<br>", unsafe_allow_html=True)
            b_col1, b_col2 = st.columns(2)
            with b_col1:
                btn_yt_script = st.button("📝 Oxşar Ssenari Yarat", use_container_width=True, key="btn_yt_script")
            with b_col2:
                btn_yt_full_video = st.button("🚀 Birbaşa Tam Video Layihəsi Yarat", use_container_width=True, key="btn_yt_full")

        if btn_yt_script or btn_yt_full_video:
            if not yt_url_input.strip():
                st.warning("Zəhmət olmasa bir YouTube video linki daxil edin.")
            else:
                vid_info = get_youtube_video_info(yt_url_input.strip())
                if not vid_info:
                    st.error("❌ Etibarlı YouTube linki tapılmadı. Zəhmət olmasa linki düzgün daxil edin.")
                else:
                    extracted_title = vid_info.get("title", "")
                    niche_to_use = yt_clone_niche.strip() or "General"
                    topic_to_use = f"{extracted_title} (YouTube ilhamlı konsept)"

                    if btn_yt_script:
                        mod = try_import("write_bridge")
                        if mod is None:
                            st.error("❌ `write_bridge.py` tapılmadı. Zəhmət olmasa layihə fayllarını yoxlayın.")
                        else:
                            try:
                                with st.spinner(f"Orijinal video ('{extracted_title}') analiz edilir və oxşar yeni ssenari yazılır..."):
                                    data = mod.generate_script(
                                        extracted_title,
                                        niche_to_use,
                                        LANG_MAP[yt_clone_lang],
                                    )
                                st.session_state["script_data"] = data
                                save_json(SCRIPT_FILE, data)
                                topics = load_json(USED_FILE, [])
                                if extracted_title not in topics:
                                    topics.append(extracted_title)
                                    save_json(USED_FILE, topics)
                                st.success("✅ Orijinal videoya uyğun yeni ssenari uğurla hazırlandı!")
                            except Exception as e:
                                st.error(f"❌ Xəta: {e}")

                    elif btn_yt_full_video:
                        agent = try_import("agent")
                        if agent is None:
                            st.error("❌ `agent.py` tapılmadı. Tam video yaradılması üçün agent.py faylı tələb olunur.")
                        else:
                            try:
                                with st.spinner(f"'{extracted_title}' əsasında tam video hazırlanır... Bu bir neçə dəqiqə çəkə bilər."):
                                    res = agent.make_one(
                                        niche=niche_to_use,
                                        topic=extracted_title,
                                        language=LANG_MAP[yt_clone_lang],
                                        fmt="shorts" if yt_clone_fmt.startswith("Shorts") else "long",
                                    )
                                st.session_state["last_result"] = res
                                topics = load_json(USED_FILE, [])
                                if extracted_title not in topics:
                                    topics.append(extracted_title)
                                    save_json(USED_FILE, topics)
                                st.success("✅ Oxşar video layihəsi uğurla hazırlandı!")
                            except Exception as e:
                                st.error(f"❌ Video yaradılarkən xəta: {e}")

        # Show generated script if available
        data = st.session_state.get("script_data") or load_json(SCRIPT_FILE, None)
        if data and mode == "🔗 YouTube Linkdən yarat":
            st.markdown("---")
            st.markdown(f"### 🎬 Hazırlanmış Ssenari: {data.get('title', 'Başlıqsız')}")
            hook = data.get("hook", "")
            if hook:
                st.markdown(f"> 💡 **Hook:** {hook}")

            edited_scenes = []
            scenes = data.get("scenes", [])
            for i, scene in enumerate(scenes, start=1):
                with st.container(border=True):
                    sc1, sc2 = st.columns([1, 4])
                    with sc1:
                        st.markdown(f"""
                        <div style="display:flex;flex-direction:column;align-items:center;gap:6px;padding-top:4px">
                            <div class="step-badge">{i}</div>
                            <div style="font-size:11px;color:#7b87aa;text-align:center">{scene.get('visual','')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with sc2:
                        new_text = st.text_area(
                            f"Səhnə {i} — narrasyon",
                            value=scene.get("narration", ""),
                            key=f"yt_scene_{i}",
                            height=90,
                        )
                        edited_scenes.append({**scene, "narration": new_text})

            col_s1, col_s2 = st.columns(2)
            with col_s1:
                if st.button("💾 Dəyişiklikləri yadda saxla", use_container_width=True, key="save_yt_script"):
                    data["scenes"] = edited_scenes
                    st.session_state["script_data"] = data
                    if save_json(SCRIPT_FILE, data):
                        st.success("✅ Yadda saxlanıldı!")
            with col_s2:
                if st.button("🎧 Səs Studiosuna keç →", on_click=go_to, args=("🎙️ Ses",), use_container_width=True, key="go_voice_from_yt"):
                    pass

        # Show generated video result if available
        result = st.session_state.get("last_result")
        if result and mode == "🔗 YouTube Linkdən yarat":
            st.markdown("---")
            st.markdown("### 🎥 Hazırlanmış Video")
            st.write(f"**Mövzu:** {result.get('topic', '')}")
            st.write(f"**Başlıq:** {result.get('title', '')}")
            video_path = Path(result.get("video", ""))
            if video_path.exists():
                st.video(str(video_path))
                with open(video_path, "rb") as vf:
                    st.download_button("⬇️ Videonu yüklə", vf, file_name=video_path.name, mime="video/mp4", use_container_width=True, key="dl_yt_clone_vid")

    else:  # Manual
        with st.container(border=True):
            saved = MANUAL_SCRIPT_FILE.read_text(encoding="utf-8") if MANUAL_SCRIPT_FILE.exists() else ""
            script = st.text_area(
                "✍️ Senarinizi buraya yazın",
                value=saved,
                height=450,
                placeholder="Video üçün ssenarinizi əl ilə yazın…",
                key="manual_script_area",
            )
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("💾 Yadda saxla", use_container_width=True, key="save_manual"):
                    try:
                        with open(MANUAL_SCRIPT_FILE, "w", encoding="utf-8") as f:
                            f.write(script)
                        st.success("✅ Senaryo yadda saxlanıldı!")
                    except Exception as e:
                        st.error(f"❌ Xəta: {e}")
            with col_b:
                if script.strip():
                    st.download_button("⬇️ Yüklə (.txt)", script.encode("utf-8"),
                                       file_name="script.txt", mime="text/plain",
                                       use_container_width=True, key="dl_script")


# ══════════════════════════════════════════════
#  🎙️  SES
# ══════════════════════════════════════════════

elif page == "🎙️ Ses":

    st.markdown("""
    <div class="page-header">
        <h1>🎙️ Səs Studio</h1>
        <p>AI neural səslərlə peşəkar dublyaj yaradın.</p>
    </div>
    """, unsafe_allow_html=True)

    voice_keys   = list(VOICE_OPTIONS.keys())
    saved_voice  = get_setting("voice", "name", voice_keys[0])

    col_settings, col_preview = st.columns([3, 2], gap="large")

    with col_settings:
        with st.container(border=True):
            st.markdown('<div class="section-title" style="margin-bottom:14px">🎤 Səs Seçimi</div>', unsafe_allow_html=True)
            voice_name = st.selectbox("AI Səsi", voice_keys,
                                      index=pick_index(voice_keys, saved_voice),
                                      key="voice_select")
            c1, c2 = st.columns(2)
            with c1:
                speed = st.slider("Sürət", -50, 50,
                                  get_setting("voice", "speed", 0), 5, key="voice_speed",
                                  help="Mənfi = yavaş, Müsbət = sürətli")
            with c2:
                pitch = st.slider("Ton (pitch)", -20, 20,
                                  get_setting("voice", "pitch", 0), 1, key="voice_pitch",
                                  help="Mənfi = alçaq ton, Müsbət = yüksək ton")

        with st.container(border=True):
            st.markdown('<div class="section-title" style="margin-bottom:14px">📝 Mətn</div>', unsafe_allow_html=True)

            # Auto-fill from script
            script_data = st.session_state.get("script_data") or load_json(SCRIPT_FILE, None)
            auto_text = ""
            if script_data:
                auto_text = "\n\n".join(
                    s.get("narration", "") for s in script_data.get("scenes", [])
                )

            text = st.text_area(
                "Səsləndiriləcək mətn",
                value=auto_text,
                height=260,
                placeholder="Ssenaridən avtomatik dolduruldu. Dəyişdirə bilərsiniz…",
                key="voice_text",
            )
            if script_data and auto_text:
                st.caption("💡 Ssenariodan avtomatik yükləndi.")

            if st.button("🔊 SƏSİ YARAT", use_container_width=True, key="gen_voice"):
                if not text.strip():
                    st.warning("Əvvəlcə mətn daxil edin.")
                else:
                    mod = try_import("voice")
                    if mod is None:
                        st.error("❌ `voice.py` tapılmadı.")
                    else:
                        try:
                            save_setting("voice", {
                                "name": voice_name,
                                "speed": speed,
                                "pitch": pitch,
                            })
                            AUDIO_FILE.parent.mkdir(parents=True, exist_ok=True)
                            rate = f"{speed:+d}%"
                            with st.spinner("AI səsi hazırlanır…"):
                                mod.generate_voice(
                                    text.strip(), str(AUDIO_FILE),
                                    VOICE_OPTIONS[voice_name], rate,
                                )
                            st.success("✅ Səs uğurla yaradıldı!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Xəta: {e}")

    with col_preview:
        st.markdown(f"""
        <div class="voice-preview" style="margin-bottom:16px">
            <div class="voice-avatar">🎙</div>
            <div>
                <div class="voice-name">{voice_name}</div>
                <div class="voice-lang">{VOICE_OPTIONS.get(voice_name, '')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown('<div class="section-title" style="margin-bottom:12px">▶ Son Yaradılan Səs</div>', unsafe_allow_html=True)
            if AUDIO_FILE.exists():
                sz = format_size(AUDIO_FILE)
                mod_time = datetime.fromtimestamp(AUDIO_FILE.stat().st_mtime).strftime("%d.%m.%Y %H:%M")
                st.markdown(f"<span style='color:#7b87aa;font-size:12px'>{sz} · {mod_time}</span>",
                            unsafe_allow_html=True)
                st.audio(str(AUDIO_FILE), format="audio/mp3")
                with open(AUDIO_FILE, "rb") as af:
                    st.download_button("⬇️ MP3 yüklə", af,
                                       file_name="generated_voice.mp3",
                                       mime="audio/mpeg",
                                       use_container_width=True,
                                       key="dl_audio")
            else:
                st.markdown("""
                <div class="empty-state">
                    <div class="icon">🔇</div>
                    <div class="label">Hələ səs yaradılmayıb.</div>
                </div>""", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown('<div class="section-title" style="margin-bottom:10px">💡 İpucu</div>', unsafe_allow_html=True)
            st.markdown("""
            <ul style="color:#7b87aa;font-size:13px;line-height:1.8;margin:0;padding-left:18px">
                <li>Sürəti <strong style="color:#a78bfa">+5</strong> artırmaq Shorts üçün idealdır</li>
                <li>Ton <strong style="color:#a78bfa">-5</strong> ilə daha dərin səs əldə edin</li>
                <li>Azərbaycan dili üçün <strong style="color:#a78bfa">Babək</strong> tövsiyə olunur</li>
            </ul>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  🎵  MUSİQİ
# ══════════════════════════════════════════════

elif page == "🎵 Musiqi":

    st.markdown("""
    <div class="page-header">
        <h1>🎵 Musiqi Studio</h1>
        <p>Videonuz üçün fon musiqisi seçin.</p>
    </div>
    """, unsafe_allow_html=True)

    music_icons = {
        "Cinematic":     "🎬",
        "Documentary":   "📽",
        "Technology":    "💻",
        "Emotional":     "💜",
        "Suspense":      "😰",
        "Inspirational": "🌟",
        "No Music":      "🔇",
    }

    saved_music = st.session_state["selected_music"]

    with st.container(border=True):
        st.markdown('<div class="section-title" style="margin-bottom:16px">🎶 Musiqi Növü</div>', unsafe_allow_html=True)
        music_cols = st.columns(4)
        for i, opt in enumerate(MUSIC_OPTIONS):
            col = music_cols[i % 4]
            with col:
                is_active = saved_music == opt
                border_color = "#7c3aed" if is_active else "#1a2340"
                bg_color = "rgba(124,58,237,0.12)" if is_active else "var(--panel)"
                txt_color = "#a78bfa" if is_active else "#7b87aa"
                st.markdown(f"""
                <div onclick="" style="
                    background:{bg_color};border:1px solid {border_color};
                    border-radius:14px;padding:14px 10px;text-align:center;
                    cursor:pointer;transition:all 0.2s;margin-bottom:10px">
                    <div style="font-size:26px;margin-bottom:6px">{music_icons.get(opt,'🎵')}</div>
                    <div style="font-size:13px;font-weight:600;color:{txt_color}">{opt}</div>
                </div>""", unsafe_allow_html=True)
                if st.button(f"{'✓ ' if is_active else ''}{opt}", key=f"music_{opt}",
                             use_container_width=True):
                    st.session_state["selected_music"] = opt
                    st.rerun()

    with st.container(border=True):
        st.markdown('<div class="section-title" style="margin-bottom:14px">⚙️ Ayarlar</div>', unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        with m1:
            volume = st.slider("🔊 Musiqi səsi", 0, 100,
                               get_setting("music", "volume", 30), key="music_vol")
        with m2:
            fade_in  = st.slider("▶ Fade-in (saniyə)", 0, 10,
                                 get_setting("music", "fade_in", 2), key="music_fadein")
            fade_out = st.slider("⏹ Fade-out (saniyə)", 0, 10,
                                 get_setting("music", "fade_out", 3), key="music_fadeout")

        if st.button("💾 Musiqi seçimini yadda saxla", use_container_width=True, key="save_music"):
            save_setting("music", {
                "style":    st.session_state["selected_music"],
                "volume":   volume,
                "fade_in":  fade_in,
                "fade_out": fade_out,
            })
            st.success(f"✅ Yadda saxlanıldı: {st.session_state['selected_music']} · {volume}% səs")


# ══════════════════════════════════════════════
#  🔊  SES EFEKTLƏRİ
# ══════════════════════════════════════════════

elif page == "🔊 Ses Efektləri":

    st.markdown("""
    <div class="page-header">
        <h1>🔊 Ses Efektləri</h1>
        <p>Videona canlılıq qatmaq üçün səs effektləri seçin.</p>
    </div>
    """, unsafe_allow_html=True)

    effect_icons = {
        "Whoosh": "💨", "Impact": "💥", "Hit": "👊", "Door": "🚪",
        "Rain": "🌧", "Fire": "🔥", "Electricity": "⚡", "Wind": "🌬",
        "Footsteps": "👣", "Notification": "🔔",
    }

    selected = st.session_state["selected_effects"]

    with st.container(border=True):
        st.markdown('<div class="section-title" style="margin-bottom:14px">🎛 Effekt Seç (çoxlu seçim)</div>', unsafe_allow_html=True)

        eff_cols = st.columns(5)
        for i, eff in enumerate(EFFECT_OPTIONS):
            col = eff_cols[i % 5]
            with col:
                is_sel = eff in selected
                if st.checkbox(
                    f"{effect_icons.get(eff,'')} {eff}",
                    value=is_sel,
                    key=f"eff_{eff}",
                ):
                    if eff not in st.session_state["selected_effects"]:
                        st.session_state["selected_effects"].append(eff)
                else:
                    if eff in st.session_state["selected_effects"]:
                        st.session_state["selected_effects"].remove(eff)

    if selected:
        st.markdown(f"**Seçilmiş effektlər:** " + " · ".join(
            f"{effect_icons.get(e,'')} {e}" for e in selected
        ))

    with st.container(border=True):
        st.markdown('<div class="section-title" style="margin-bottom:14px">⚙️ Effekt Ayarları</div>', unsafe_allow_html=True)
        ea1, ea2 = st.columns(2)
        with ea1:
            eff_vol = st.slider("🔊 Effekt səsi", 0, 100,
                                get_setting("sound_effects", "volume", 70), key="eff_vol")
        with ea2:
            eff_dur = st.selectbox("⏱ Effekt uzunluğu", DURATION_OPTIONS,
                                   index=pick_index(DURATION_OPTIONS,
                                   get_setting("sound_effects", "duration", DURATION_OPTIONS[1])),
                                   key="eff_dur")

        if st.button("💾 Effekt seçimini yadda saxla", use_container_width=True, key="save_effects"):
            save_setting("sound_effects", {
                "effects":  st.session_state["selected_effects"],
                "volume":   eff_vol,
                "duration": eff_dur,
            })
            st.success(f"✅ {len(selected)} effekt yadda saxlanıldı!")


# ══════════════════════════════════════════════
#  🎥  GÖRSELLƏR
# ══════════════════════════════════════════════

elif page == "🎥 Görseller":

    st.markdown("""
    <div class="page-header">
        <h1>🎥 Görsel Studio</h1>
        <p>Video üçün kliplər və şəkillər seçin.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('<div class="section-title" style="margin-bottom:14px">📂 Mənbə & Üslub</div>', unsafe_allow_html=True)
        v1, v2 = st.columns(2)
        with v1:
            vis_src = st.selectbox("Görsel mənbə", VISUAL_SOURCES,
                                   index=pick_index(VISUAL_SOURCES,
                                   get_setting("visuals", "source", VISUAL_SOURCES[0])),
                                   key="vis_src")
        with v2:
            vis_sty = st.selectbox("Görsel üslub", VISUAL_STYLES,
                                   index=pick_index(VISUAL_STYLES,
                                   get_setting("visuals", "style", VISUAL_STYLES[0])),
                                   key="vis_sty")

        vs1, vs2 = st.columns(2)
        with vs1:
            vis_res = st.radio("📐 Həll", ["1080p", "4K", "720p"], horizontal=True, key="vis_res")
        with vs2:
            vis_fps = st.radio("🎞 FPS", ["24", "30", "60"], horizontal=True, key="vis_fps")

    # Source descriptions
    src_info = {
        "Stock Footage (Pixabay)": ("🌐 Pixabay", "Milyonlarla pulsuz lisenziyalı stock video.", "#3b82f6"),
        "AI Image Generator":     ("🤖 AI Şəkil",  "DALL-E / Stable Diffusion ilə şəkil yarat.",  "#7c3aed"),
        "AI Video Generator":     ("✨ AI Video",  "Suno / Pika kimi alətlər ilə video yarat.",    "#ec4899"),
    }
    info_icon, info_txt, info_color = src_info[vis_src]
    st.markdown(f"""
    <div style="background:rgba(59,130,246,0.06);border:1px solid {info_color}33;border-radius:12px;
                padding:14px 18px;display:flex;gap:12px;align-items:center;margin:12px 0">
        <span style="font-size:22px">{info_icon[0]}</span>
        <div>
            <div style="font-size:14px;font-weight:600;color:#e8eeff">{info_icon}</div>
            <div style="font-size:13px;color:#7b87aa">{info_txt}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('<div class="section-title" style="margin-bottom:14px">🔑 API Açarı (ixtiyari)</div>', unsafe_allow_html=True)
        api_key = st.text_input("API açarı", type="password",
                                value=get_setting("visuals", "api_key", ""),
                                placeholder="Pixabay / OpenAI API açarınız",
                                key="vis_api")

        if st.button("💾 Görsel seçimini yadda saxla", use_container_width=True, key="save_visuals"):
            save_setting("visuals", {
                "source":  vis_src,
                "style":   vis_sty,
                "res":     vis_res,
                "fps":     vis_fps,
                "api_key": api_key,
            })
            st.success(f"✅ Yadda saxlanıldı: {vis_src} · {vis_sty} · {vis_res} {vis_fps}fps")


# ══════════════════════════════════════════════
#  ✂️  DÜZƏNLƏMƏ
# ══════════════════════════════════════════════

elif page == "✂️ Düzenleme":

    st.markdown("""
    <div class="page-header">
        <h1>✂️ Düzənləmə</h1>
        <p>Montaj sistemi və avtomatik effekt seçimləri.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('<div class="section-title" style="margin-bottom:14px">🎬 Montaj Sistemi</div>', unsafe_allow_html=True)

        edit_sys = st.selectbox("Montaj üsulu", EDITING_OPTIONS,
                                index=pick_index(EDITING_OPTIONS,
                                get_setting("editing", "system", EDITING_OPTIONS[0])),
                                key="edit_sys")

        edit_desc = {
            "Automatic Editing":    "AI avtomatik kəsikləri və keçidləri seçir.",
            "Manual Editing":       "Hər kəsiyi özünüz idarə edirsiniz.",
            "Cinematic Editing":    "Yavaş keçidlər, dramatik kəsiklər, film effekti.",
            "Shorts Editing":       "Sürətli montaj, diqqəti cəlb edən açılış, vertical.",
            "Documentary Editing":  "Sakit, axıcı keçidlər, informativ üslub.",
        }
        st.caption(edit_desc.get(edit_sys, ""))

    with st.container(border=True):
        st.markdown('<div class="section-title" style="margin-bottom:14px">⚙️ Avtomatik Effektlər</div>', unsafe_allow_html=True)
        e1, e2 = st.columns(2)
        with e1:
            subtitles   = st.checkbox("📝 Avtomatik altyazı",
                                      value=get_setting("editing", "subtitles", True), key="ed_subs")
            transitions = st.checkbox("🔄 Avtomatik keçidlər",
                                      value=get_setting("editing", "transitions", True), key="ed_trans")
        with e2:
            zoom        = st.checkbox("🔍 Dinamik zoom",
                                      value=get_setting("editing", "zoom", True), key="ed_zoom")
            color_grade = st.checkbox("🎨 Rəng korreksiyası",
                                      value=get_setting("editing", "color_grade", False), key="ed_color")

    with st.container(border=True):
        st.markdown('<div class="section-title" style="margin-bottom:14px">⏱ Müddət Ayarları</div>', unsafe_allow_html=True)
        d1, d2 = st.columns(2)
        with d1:
            min_clip = st.slider("Min. klip müddəti (san)", 1, 10,
                                 get_setting("editing", "min_clip", 3), key="ed_min")
        with d2:
            max_clip = st.slider("Max. klip müddəti (san)", 5, 30,
                                 get_setting("editing", "max_clip", 10), key="ed_max")

    if st.button("💾 Montaj ayarlarını yadda saxla", use_container_width=True, key="save_editing"):
        save_setting("editing", {
            "system":      edit_sys,
            "subtitles":   subtitles,
            "transitions": transitions,
            "zoom":        zoom,
            "color_grade": color_grade,
            "min_clip":    min_clip,
            "max_clip":    max_clip,
        })
        st.success("✅ Montaj ayarları yadda saxlanıldı!")


# ══════════════════════════════════════════════
#  🖼️  KÜÇÜK ÇİZİM
# ══════════════════════════════════════════════

elif page == "🖼️ Küçük Çizim":

    st.markdown("""
    <div class="page-header">
        <h1>🖼️ Küçük Çizim (Thumbnail)</h1>
        <p>Videonuz üçün cəlbedici thumbnail yaradın.</p>
    </div>
    """, unsafe_allow_html=True)

    col_form, col_prev = st.columns([3, 2], gap="large")

    with col_form:
        with st.container(border=True):
            st.markdown('<div class="section-title" style="margin-bottom:14px">⚙️ Thumbnail Parametrləri</div>', unsafe_allow_html=True)

            thumb_title = st.text_input("📝 Başlıq mətni",
                                        value=last_title(),
                                        placeholder="Videonuzun cəlbedici başlığı",
                                        key="thumb_title")

            t1, t2 = st.columns(2)
            with t1:
                thumb_style = st.selectbox("🎨 Üslub",
                    ["Bold & Colorful", "Minimal", "Dark & Dramatic", "Neon", "Professional"],
                    key="thumb_style")
            with t2:
                thumb_emoji = st.text_input("😀 Emoji (ixtiyari)", value="🔥",
                                            key="thumb_emoji", max_chars=4)

            thumb_bg = st.color_picker("🎨 Fon rəngi", value="#1a0533", key="thumb_bg")

            make_thumb_btn = st.button("✨ Thumbnail Yarat", use_container_width=True, key="make_thumb")

        if make_thumb_btn:
            video = latest_video()
            if not video:
                st.warning("Əvvəlcə bir video yaradın.")
            elif not thumb_title.strip():
                st.warning("Başlıq daxil edin.")
            else:
                mod = try_import("thumbnail")
                if mod is None:
                    st.error("❌ `thumbnail.py` tapılmadı.")
                else:
                    try:
                        with st.spinner("Thumbnail hazırlanır…"):
                            mod.make_thumbnail(video, thumb_title.strip())
                        if THUMB_FILE.exists():
                            st.success("✅ Thumbnail hazırdır!")
                            st.rerun()
                        else:
                            st.warning("Thumbnail faylı tapılmadı.")
                    except Exception as e:
                        st.error(f"❌ Xəta: {e}")

    with col_prev:
        with st.container(border=True):
            st.markdown('<div class="section-title" style="margin-bottom:12px">👁 Önizləmə</div>', unsafe_allow_html=True)
            if THUMB_FILE.exists():
                sz  = format_size(THUMB_FILE)
                mod_time = datetime.fromtimestamp(THUMB_FILE.stat().st_mtime).strftime("%d.%m.%Y %H:%M")
                st.image(str(THUMB_FILE), caption=f"thumbnail.jpg · {sz} · {mod_time}",
                         use_container_width=True)
                with open(THUMB_FILE, "rb") as tf:
                    st.download_button("⬇️ Thumbnail yüklə (.jpg)", tf,
                                       file_name="thumbnail.jpg",
                                       mime="image/jpeg",
                                       use_container_width=True,
                                       key="dl_thumb")
            else:
                st.markdown("""
                <div class="empty-state">
                    <div class="icon">🖼️</div>
                    <div class="label">Hələ thumbnail yaradılmayıb.</div>
                </div>""", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown('<div class="section-title" style="margin-bottom:10px">📐 Ölçülər</div>', unsafe_allow_html=True)
            st.markdown("""
            <div style="color:#7b87aa;font-size:13px;line-height:1.9">
                📺 Standart: <strong style="color:#e8eeff">1280 × 720px</strong><br>
                📱 Shorts: <strong style="color:#e8eeff">1080 × 1920px</strong><br>
                🗜 Fayl ölçüsü: <strong style="color:#e8eeff">&lt; 2 MB</strong><br>
                🎨 Format: <strong style="color:#e8eeff">JPG / PNG</strong>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  📤  YOUTUBE
# ══════════════════════════════════════════════

elif page == "📤 YouTube":

    st.markdown("""
    <div class="page-header">
        <h1>📤 YouTube Yükləmə</h1>
        <p>Videonuzu YouTube-a yükləmək üçün məlumatları doldurun.</p>
    </div>
    """, unsafe_allow_html=True)

    saved_meta = load_json(YOUTUBE_META_FILE, {})

    col_form, col_info = st.columns([3, 2], gap="large")

    with col_form:
        # YT branding
        st.markdown("""
        <div class="yt-upload-card">
            <div class="yt-logo">
                <div class="yt-icon"></div>
                <div class="yt-brand">YouTube Upload</div>
            </div>
            <p style="font-size:13px;color:#7b87aa;margin:0">
            Aşağıdakı məlumatları doldurun. Yükləmə üçün YouTube Data API v3 tələb olunur.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown('<div class="section-title" style="margin-bottom:14px">📋 Video Məlumatları</div>', unsafe_allow_html=True)

            yt_title = st.text_input("🎯 YouTube Başlığı",
                                     value=saved_meta.get("title", last_title()),
                                     max_chars=100,
                                     key="yt_title",
                                     help="Maksimum 100 simvol")
            char_count = len(yt_title)
            color = "#22c55e" if char_count <= 60 else "#f97316" if char_count <= 100 else "#ef4444"
            st.markdown(f"<div style='font-size:11px;color:{color};text-align:right;margin-top:-10px'>{char_count}/100</div>",
                        unsafe_allow_html=True)

            yt_desc = st.text_area("📝 Təsvir (description)",
                                   value=saved_meta.get("description", ""),
                                   height=200,
                                   max_chars=5000,
                                   key="yt_desc",
                                   placeholder="Videonun təsvirini yazın. Açar sözlər, linklər əlavə edin…")

            yt_tags = st.text_input("🏷 Teqlər (vergüllə ayırın)",
                                    value=", ".join(saved_meta.get("tags", [])),
                                    key="yt_tags",
                                    placeholder="AI, texnologiya, gələcək, youtube")

        with st.container(border=True):
            st.markdown('<div class="section-title" style="margin-bottom:14px">⚙️ Yükləmə Ayarları</div>', unsafe_allow_html=True)
            ya1, ya2, ya3 = st.columns(3)
            with ya1:
                yt_privacy = st.selectbox("🔒 Görünüş", PRIVACY_OPTIONS,
                                          index=pick_index(PRIVACY_OPTIONS,
                                          saved_meta.get("privacy", PRIVACY_OPTIONS[0])),
                                          key="yt_privacy")
            with ya2:
                yt_category = st.selectbox("📂 Kateqoriya",
                                           ["Science & Technology", "Education", "Entertainment",
                                            "News & Politics", "Howto & Style", "Gaming"],
                                           key="yt_cat")
            with ya3:
                yt_lang = st.selectbox("🌐 Dil", list(LANG_MAP.keys()), key="yt_lang")

            yt_playlist = st.text_input("📋 Playlist adı (ixtiyari)",
                                        value=saved_meta.get("playlist", ""),
                                        key="yt_playlist",
                                        placeholder="Mövcud playlist adı")
            yt_notify = st.checkbox("🔔 Abunəçilərə bildiriş göndər",
                                    value=saved_meta.get("notify", True), key="yt_notify")

        # Buttons
        b1, b2 = st.columns(2)
        with b1:
            if st.button("💾 Məlumatları yadda saxla", use_container_width=True, key="save_yt"):
                tags_list = [t.strip() for t in yt_tags.split(",") if t.strip()]
                if save_json(YOUTUBE_META_FILE, {
                    "title":    yt_title,
                    "description": yt_desc,
                    "tags":     tags_list,
                    "privacy":  yt_privacy,
                    "category": yt_category,
                    "language": yt_lang,
                    "playlist": yt_playlist,
                    "notify":   yt_notify,
                }):
                    st.success("✅ Məlumatlar yadda saxlanıldı!")

        with b2:
            if st.button("🚀 YouTube-a Yüklə", use_container_width=True, key="upload_yt"):
                video = latest_video()
                if not video:
                    st.error("❌ Yüklənəcək video tapılmadı.")
                elif not yt_title.strip():
                    st.warning("Başlıq daxil edin.")
                else:
                    mod = try_import("uploader")
                    if mod is None:
                        st.error("❌ `uploader.py` tapılmadı. YouTube API inteqrasiyasını qurun.")
                    else:
                        try:
                            with st.spinner("YouTube-a yüklənir…"):
                                url = mod.upload(
                                    str(video),
                                    title=yt_title,
                                    description=yt_desc,
                                    tags=[t.strip() for t in yt_tags.split(",") if t.strip()],
                                    privacy=yt_privacy,
                                )
                            st.success(f"✅ Video yükləndi! 🎉")
                            st.markdown(f"[▶ YouTube-da aç]({url})")
                        except Exception as e:
                            st.error(f"❌ Yükləmə xətası: {e}")

    with col_info:
        # Preview card
        with st.container(border=True):
            st.markdown('<div class="section-title" style="margin-bottom:12px">👁 Önizləmə</div>', unsafe_allow_html=True)
            if THUMB_FILE.exists():
                st.image(str(THUMB_FILE), use_container_width=True)
            else:
                st.markdown("""<div style="background:#0c1222;border-radius:12px;aspect-ratio:16/9;
                    display:flex;align-items:center;justify-content:center;color:#7b87aa;font-size:13px">
                    Thumbnail yoxdur</div>""", unsafe_allow_html=True)

            if yt_title:
                st.markdown(f"**{yt_title[:60]}{'…' if len(yt_title) > 60 else ''}**")
            tags_list_prev = [t.strip() for t in yt_tags.split(",") if t.strip()]
            if tags_list_prev:
                tags_html = " ".join(
                    f'<span style="background:rgba(124,58,237,0.15);color:#a78bfa;'
                    f'border-radius:999px;padding:2px 10px;font-size:11px;margin:2px">{t}</span>'
                    for t in tags_list_prev[:6]
                )
                st.markdown(tags_html, unsafe_allow_html=True)

        # Checklist
        with st.container(border=True):
            st.markdown('<div class="section-title" style="margin-bottom:12px">✅ Yükləmə Checklist</div>', unsafe_allow_html=True)

            video   = latest_video()
            checks  = [
                ("🎬 Video fayl",    bool(video)),
                ("📝 Başlıq",        bool(yt_title.strip())),
                ("📝 Təsvir",        len(yt_desc.strip()) > 20),
                ("🏷 Teqlər",        bool(yt_tags.strip())),
                ("🖼️ Thumbnail",    THUMB_FILE.exists()),
            ]
            for label, ok in checks:
                icon  = "✅" if ok else "⬜"
                color = "#22c55e" if ok else "#6b7597"
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:8px;padding:5px 0;'
                    f'font-size:13px;color:{color}">{icon} {label}</div>',
                    unsafe_allow_html=True,
                )

            all_ok = all(ok for _, ok in checks)
            if all_ok:
                st.success("Hər şey hazırdır! Yükləyə bilərsiniz. 🚀")
            else:
                missing = sum(1 for _, ok in checks if not ok)
                st.warning(f"{missing} element çatışmır.")

        # API setup note
        with st.container(border=True):
            st.markdown('<div class="section-title" style="margin-bottom:8px">🔑 API Qurulumu</div>', unsafe_allow_html=True)
            st.markdown("""
            <div style="font-size:13px;color:#7b87aa;line-height:1.8">
                1. <a href="https://console.cloud.google.com" target="_blank" style="color:#7c3aed">Google Cloud Console</a>-a daxil olun<br>
                2. YouTube Data API v3-ü aktiv edin<br>
                3. OAuth 2.0 client yaradın<br>
                4. <code style="background:#0c1222;padding:2px 6px;border-radius:4px">client_secret.json</code> faylını layihəyə yerləşdirin
            </div>
            """, unsafe_allow_html=True)
