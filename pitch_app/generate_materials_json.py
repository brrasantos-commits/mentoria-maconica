from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent
MATERIALS_DIR = BASE_DIR / "materials"
OUTPUT_FILE = BASE_DIR / "materials.json"

INDUSTRY_BY_KEYWORD = [
    ("SAÚDE", "Saúde"),
    ("clinic", "Saúde"),
    ("hospital", "Saúde"),
    ("bank", "Finanças"),
    ("finance", "Finanças"),
    ("payment", "Finanças"),
    ("VAREJO", "Varejo"),
    ("EDUCAÇÃO", "Educação"),
    ("AGRO", "Agro"),
    ("LOGISTICA", "Logistica"),
    ("school", "Educação"),
    ("edu", "Educação"),
    ("training", "Educação"),
    ("INDUSTRIAL", "Industrial"),
    ("factory", "Industrial"),
    ("manufact", "Industrial"),
]

SOLUTION_BY_KEYWORD = [
    ("consult", "Consultoria"),
    ("strategy", "Consultoria"),
    ("service", "Serviços"),
    ("support", "Serviços"),
    ("hardware", "Hardware"),
    ("FusionCube", "FusionCube"),
    ("device", "Hardware"),
    ("platform", "Plataforma"),
    ("portal", "Plataforma"),
    ("marketplace", "Plataforma"),
]


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


def main():
    items = []
    if not MATERIALS_DIR.exists():
        raise SystemExit(f"Pasta não encontrada: {MATERIALS_DIR}")

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

    OUTPUT_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Gerado: {OUTPUT_FILE} com {len(items)} materiais")


if __name__ == "__main__":
    main()