from pathlib import Path
import json
import time
import threading

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

BASE_DIR = Path(__file__).resolve().parent
MATERIALS_DIR = BASE_DIR / "materials"
OUTPUT_FILE = BASE_DIR / "materials.json"

INDUSTRY_BY_KEYWORD = [
    ("saude", "Saúde"),
    ("clinic", "Saúde"),
    ("hospital", "Saúde"),
    ("bank", "Finanças"),
    ("finance", "Finanças"),
    ("payment", "Finanças"),
    ("tech", "Tecnologia"),
    ("ai", "Tecnologia"),
    ("software", "Tecnologia"),
    ("app", "Tecnologia"),
    ("school", "Educação"),
    ("edu", "Educação"),
    ("training", "Educação"),
    ("industrial", "Indústria"),
    ("factory", "Indústria"),
    ("manufact", "Indústria"),
]

SOLUTION_BY_KEYWORD = [
    ("consult", "Consultoria"),
    ("strategy", "Consultoria"),
    ("service", "Serviços"),
    ("support", "Serviços"),
    ("hardware", "Hardware"),
    ("sensor", "Hardware"),
    ("device", "Hardware"),
    ("platform", "Plataforma"),
    ("portal", "Plataforma"),
    ("marketplace", "Plataforma"),
]

_lock = threading.Lock()
_last_run = 0.0


def detect_industry(text: str) -> str:
    t = text.lower()
    for key, value in INDUSTRY_BY_KEYWORD:
        if key in t:
            return value
    return "Não informado"


def detect_solution(text: str) -> str:
    t = text.lower()
    for key, value in SOLUTION_BY_KEYWORD:
        if key in t:
            return value
    return "Não informado"


def detect_kind(filename: str) -> str:
    ext = Path(filename).suffix.lower().lstrip(".")
    if ext == "pdf":
        return "pdf"
    if ext in {"mp4", "m4v", "webm", "mov", "avi", "mkv"}:
        return "video"
    return "file"


def human_title(filename: str) -> str:
    return Path(filename).stem.replace("_", " ").replace("-", " ").title()


def generate_json():
    global _last_run
    with _lock:
        now = time.time()
        if now - _last_run < 0.5:
            return
        _last_run = now

        MATERIALS_DIR.mkdir(parents=True, exist_ok=True)

        items = []
        for i, path in enumerate(sorted(MATERIALS_DIR.iterdir()), start=1):
            if not path.is_file() or path.name.startswith("."):
                continue

            title = human_title(path.name)
            items.append({
                "filename": path.name,
                "title": title,
                "industry": detect_industry(title),
                "solution": detect_solution(title),
                "kind": detect_kind(path.name),
                "type": path.suffix.lower().lstrip("."),
                "sort": i,
            })

        OUTPUT_FILE.write_text(
            json.dumps(items, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print(f"[OK] materials.json atualizado com {len(items)} arquivos.")


class MaterialsHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.is_directory:
            return
        generate_json()


def main():
    MATERIALS_DIR.mkdir(parents=True, exist_ok=True)
    generate_json()

    event_handler = MaterialsHandler()
    observer = Observer()
    observer.schedule(event_handler, str(MATERIALS_DIR), recursive=False)
    observer.start()

    print(f"[WATCHING] Monitorando: {MATERIALS_DIR}")
    print("[INFO] Pressione Ctrl+C para parar.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()