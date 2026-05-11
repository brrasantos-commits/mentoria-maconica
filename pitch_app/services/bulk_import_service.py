"""
Bulk Import Service - Import multiple materials from directory
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from pitch_app.services.material_service import invalidate_filter_cache

from pitch_app.services.config import MATERIALS_DIR


def scan_materials_directory() -> List[Dict]:
    """Scan materials directory and return list of files not yet in database."""

    if not MATERIALS_DIR.exists():
        return []

    files: List[Dict] = []

    for file_path in sorted(MATERIALS_DIR.iterdir()):
        if not file_path.is_file() or file_path.name.startswith("."):
            continue

        # Get file extension
        ext = file_path.suffix.lower().lstrip(".")

        # Skip non-media files
        if ext not in ["pdf", "mp4", "webm", "mov", "avi", "mkv"]:
            continue

        # Generate suggested title from filename
        title = generate_title_from_filename(file_path.stem)

        # Try to extract industry and solution from filename
        industry, solution = extract_metadata_from_filename(file_path.stem)

        files.append(
            {
                "filename": file_path.name,
                "file_type": ext,
                "suggested_title": title,
                "suggested_industry": industry,
                "suggested_solution": solution,
                "file_size": file_path.stat().st_size,
                "file_size_mb": round(file_path.stat().st_size / (1024 * 1024), 2),
            }
        )

    return files



def generate_title_from_filename(filename: str) -> str:
    """
    Generate a human-readable title from filename
    
    Args:
        filename: The filename without extension
        
    Returns:
        Suggested title
    """
    # Remove common prefixes/suffixes
    title = filename
    
    # Remove underscores and hyphens, replace with spaces
    title = title.replace('_', ' ').replace('-', ' ')
    
    # Remove multiple spaces
    title = re.sub(r'\s+', ' ', title)
    
    # Capitalize words
    title = title.title()
    
    # Remove common patterns like dates, versions
    title = re.sub(r'\d{4}[-_]\d{2}[-_]\d{2}', '', title)
    title = re.sub(r'v\d+(\.\d+)*', '', title, flags=re.IGNORECASE)
    
    # Clean up
    title = title.strip()
    
    return title if title else filename


def extract_metadata_from_filename(filename: str) -> tuple[Optional[str], Optional[str]]:
    """
    Try to extract industry and solution from filename
    
    Args:
        filename: The filename without extension
        
    Returns:
        Tuple of (industry, solution) or (None, None)
    """
    filename_lower = filename.lower()
    
    # Industry keywords
    industries = {
        'varejo': 'Varejo',
        'retail': 'Varejo',
        'saude': 'Saúde',
        'saúde': 'Saúde',
        'health': 'Saúde',
        'financas': 'Finanças',
        'finanças': 'Finanças',
        'finance': 'Finanças',
        'tecnologia': 'Tecnologia',
        'tech': 'Tecnologia',
        'educacao': 'Educação',
        'educação': 'Educação',
        'education': 'Educação',
        'industria': 'Indústria',
        'indústria': 'Indústria',
        'industrial': 'Indústria',
        'industry': 'Indústria'
    }
    
    # Solution keywords
    solutions = {
        'software': 'Software',
        'servicos': 'Serviços',
        'serviços': 'Serviços',
        'services': 'Serviços',
        'consultoria': 'Consultoria',
        'consulting': 'Consultoria',
        'hardware': 'Hardware',
        'plataforma': 'Plataforma',
        'platform': 'Plataforma'
    }
    
    industry = None
    solution = None
    
    # Check for industry
    for keyword, value in industries.items():
        if keyword in filename_lower:
            industry = value
            break
    
    # Check for solution
    for keyword, value in solutions.items():
        if keyword in filename_lower:
            solution = value
            break
    
    return industry, solution


def get_existing_filenames(db: Session) -> set:
    """Get set of filenames already in database."""

    result = db.execute(text("SELECT filename FROM materials")).fetchall()

    filenames = set()
    for row in result:
        value = getattr(row, "filename", None)
        if value is None:
            try:
                value = row[0]
            except Exception:
                value = None
        if value:
            filenames.add(value)

    return filenames



def get_new_materials(db: Session) -> List[Dict]:
    """Get list of materials in directory that are not yet in database.

    Also precomputes a suggested sort order sequence starting at the current
    max(sort_order) + 1, so the UI can show "Ordem de exibição" already filled.
    """

    all_files = scan_materials_directory()
    existing = get_existing_filenames(db)

    new_files = [f for f in all_files if f["filename"] not in existing]

    # Suggested display order starts after last existing material
    next_order_row = db.execute(
        text("SELECT COALESCE(MAX(sort_order), 0) + 1 AS next_order FROM materials")
    ).fetchone()
    next_order = int(getattr(next_order_row, "next_order", 1) or 1)

    for idx, item in enumerate(new_files):
        item["suggested_sort_order"] = next_order + idx

    return new_files



def bulk_import_materials(db: Session, materials: List[Dict]) -> Dict:
    """Import multiple materials into database.

    Supports an optional `sort_order` field (user can edit it in the UI).

    Validation rules:
    - `sort_order` must be an integer >= 0
    - `sort_order` must be unique (no conflicts with existing materials and no duplicates within this batch)

    If `sort_order` is not provided, it assigns the next available sequence
    starting at max(sort_order)+1, skipping any occupied values.
    """

    imported = 0
    skipped = 0
    errors: list[str] = []

    existing = get_existing_filenames(db)

        # Existing orders (for uniqueness validation)
    existing_orders_rows = db.execute(text("SELECT sort_order FROM materials")).fetchall()

    used_orders: set[int] = set()
    for r in existing_orders_rows:
        if r is None:
            continue

        value = getattr(r, "sort_order", None)
        if value is None:
            try:
                value = r[0]
            except Exception:
                value = None

        if value is None:
            continue

        try:
            used_orders.add(int(value))
        except Exception:
            continue


    # Cursor for auto sort_order
    next_order_row = db.execute(
        text("SELECT COALESCE(MAX(sort_order), 0) + 1 AS next_order FROM materials")
    ).fetchone()
    next_order_cursor = int(getattr(next_order_row, "next_order", 1) or 1)

    def _next_free_order() -> int:
        nonlocal next_order_cursor
        while next_order_cursor in used_orders:
            next_order_cursor += 1
        value = next_order_cursor
        next_order_cursor += 1
        return value

    for material in materials:
        filename = material.get("filename")

        # Skip if already exists
        if filename in existing:
            skipped += 1
            continue

        # Validate required fields
        if not filename or not material.get("title"):
            errors.append(f"Missing required fields for {filename}")
            continue

        # Prefer user-provided sort_order
        sort_order_value = material.get("sort_order")

        if sort_order_value is None or sort_order_value == "":
            sort_order = _next_free_order()
        else:
            try:
                sort_order = int(sort_order_value)
            except Exception:
                errors.append(f"Ordem de exibição inválida para {filename}. Use um número inteiro.")
                continue

            if sort_order < 0:
                errors.append(f"Ordem de exibição inválida para {filename}. Use um número >= 0.")
                continue

            if sort_order in used_orders:
                errors.append(
                    f"Ordem de exibição {sort_order} já está em uso. Ajuste antes de importar: {filename}"
                )
                continue

        # Reserve the order in this batch to prevent duplicates
        used_orders.add(sort_order)

        try:
            db.execute(
                text(
                    """
                    INSERT INTO materials (
                        title, filename, file_type, industry, solution,
                        description, sort_order, active
                    ) VALUES (
                        :title, :filename, :file_type, :industry, :solution,
                        :description, :sort_order, 1
                    )
                    """
                ),
                {
                    "title": material.get("title"),
                    "filename": filename,
                    "file_type": material.get("file_type"),
                    "industry": (material.get("industry") or "").strip() or "Outros",
                    "solution": (material.get("solution") or "").strip() or "Geral",
                    "description": material.get("description", ""),
                    "sort_order": sort_order,
                },
            )
            imported += 1

        except Exception as e:
            errors.append(f"Error importing {filename}: {str(e)}")

    db.commit()
    invalidate_filter_cache()

    return {
        "imported": imported,
        "skipped": skipped,
        "errors": errors,
        "total": len(materials),
    }



# Made with Bob
