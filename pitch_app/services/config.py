import os
from pathlib import Path

# pitch_app/services/config.py
APP_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = APP_DIR

TEMPLATES_DIR = APP_DIR / "templates"
STATIC_DIR = APP_DIR / "static"

# ==============================
# PERSISTÊNCIA (Railway Volume)
# ==============================

DATA_DIR = Path(os.getenv("APP_DATA_DIR", APP_DIR / "data"))

MATERIALS_DIR = DATA_DIR / "materials"
UPLOAD_DIR = DATA_DIR / "uploads"

# Sidecars para materiais processados
PROCESSED_DIR = MATERIALS_DIR / "_processed"
MATERIAL_TRANSCRIPTS_DIR = PROCESSED_DIR / "transcripts"
MATERIAL_SUMMARIES_DIR = PROCESSED_DIR / "summaries"
MATERIAL_AUDIO_CACHE_DIR = PROCESSED_DIR / "audio"

# Criar diretórios
STATIC_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
MATERIALS_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MATERIAL_TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
MATERIAL_SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)
MATERIAL_AUDIO_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
OPENAI_TRANSCRIPTION_MODEL = os.getenv(
    "OPENAI_TRANSCRIPTION_MODEL",
    "gpt-4o-mini-transcribe",
)

MAX_TEXT_CHARS_PER_MATERIAL = int(
    os.getenv("MAX_TEXT_CHARS_PER_MATERIAL", "4000")
)
MAX_SELLER_NAME_LEN = 120

ALLOWED_MATERIAL_EXTENSIONS = {
    ".txt", ".pdf", ".docx", ".mp4", ".mov", ".avi", ".mkv", ".webm"
}
ALLOWED_VIDEO_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".avi",
    ".mkv",
    ".webm",
    ".mpeg",
    ".mpg",
    ".m4v",
}

TEXT_MATERIAL_EXTENSIONS = {".txt", ".pdf", ".docx"}
VIDEO_MATERIAL_EXTENSIONS = {
    ".mp4", ".mov", ".avi", ".mkv", ".webm", ".mpeg", ".mpg", ".m4v"
}

AUDIO_SAMPLE_RATE = os.getenv("AUDIO_SAMPLE_RATE", "16000")
AUDIO_CHANNELS = os.getenv("AUDIO_CHANNELS", "1")
MAX_VIDEO_SIZE_MB = int(os.getenv("MAX_VIDEO_SIZE_MB", "100"))