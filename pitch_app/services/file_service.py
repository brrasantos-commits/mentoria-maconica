import re
import shutil
import uuid
from dataclasses import dataclass
from pathlib import Path

from docx import Document
from fastapi import UploadFile
from pypdf import PdfReader

from pitch_app.services.config import ALLOWED_MATERIAL_EXTENSIONS, ALLOWED_VIDEO_EXTENSIONS, MAX_SELLER_NAME_LEN, UPLOAD_DIR
from pitch_app.services.exceptions import AppError

@dataclass
class SubmissionPaths:
    root: Path
    video_path: Path
    audio_path: Path
    transcript_path: Path
    feedback_path: Path

def sanitize_name(name: str) -> str:
    cleaned = re.sub(r"[^\w\s-]", "", (name or "").strip())
    cleaned = re.sub(r"\s+", "_", cleaned)
    return cleaned[:MAX_SELLER_NAME_LEN] or 'arquivo'

def sanitize_stem(name: str) -> str:
    return sanitize_name(Path(name).stem).lower()

def validate_upload_name(file: UploadFile, label: str) -> None:
    if not file.filename:
        raise AppError(f'Selecione um arquivo de {label}.')

def ensure_allowed_extension(filename: str, allowed_extensions: set[str], label: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in allowed_extensions:
        allowed = ', '.join(sorted(allowed_extensions))
        raise AppError(f'Formato de {label} não suportado. Use: {allowed}.')
    return ext

def validate_video(video: UploadFile) -> None:
    validate_upload_name(video, 'vídeo')
    ensure_allowed_extension(video.filename, ALLOWED_VIDEO_EXTENSIONS, 'vídeo')

def validate_material(material: UploadFile) -> str:
    validate_upload_name(material, 'material')
    return ensure_allowed_extension(material.filename, ALLOWED_MATERIAL_EXTENSIONS, 'material')

def create_submission_paths(seller_name: str, video_filename: str) -> SubmissionPaths:
    seller_folder = sanitize_name(seller_name)

    # 🔥 ID totalmente único por execução
    submission_id = uuid.uuid4().hex

    root = UPLOAD_DIR / seller_folder / submission_id
    root.mkdir(parents=True, exist_ok=True)

    return SubmissionPaths(
        root=root,
        video_path=root / "video.mp4",
        audio_path=root / "audio.wav",
        transcript_path=root / "transcript.txt",
        feedback_path=root / "feedback.txt",
    )

def save_upload(file: UploadFile, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('wb') as buffer:
        shutil.copyfileobj(file.file, buffer)
    return destination

def read_txt(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        return path.read_text(encoding='cp1252', errors='ignore')

def read_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    texts: list[str] = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            texts.append(text)
    return "\n".join(texts)

def read_docx(path: Path) -> str:
    doc = Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

def normalize_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned: list[str] = []
    for line in lines:
        low = line.lower()
        if low.startswith('página '):
            continue
        if low.startswith('page '):
            continue
        if low in {'confidencial', 'interno', 'uso interno'}:
            continue
        cleaned.append(line)
    return "\n".join(cleaned)

def extract_text(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == '.txt':
        return normalize_text(read_txt(path))
    if ext == '.pdf':
        return normalize_text(read_pdf(path))
    if ext == '.docx':
        return normalize_text(read_docx(path))
    raise AppError(f'Formato não suportado: {ext}')
