"""
Material management service
"""
import logging
from pathlib import Path
from typing import Optional
from functools import lru_cache
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from pitch_app.services.config import MATERIALS_DIR

logger = logging.getLogger(__name__)

# Cache key for filter options - invalidate by changing this
_filter_cache_key = datetime.utcnow().isoformat()


def invalidate_filter_cache():
    """Invalidate the filter options cache"""
    global _filter_cache_key
    _filter_cache_key = datetime.utcnow().isoformat()
    _get_filter_options_cached.cache_clear()


@lru_cache(maxsize=1)
def _get_filter_options_cached(cache_key: str):
    """Internal cached function for filter options"""
    db = None
    try:
        from pitch_app.db import SessionLocal
        db = SessionLocal()
        
        rows = db.execute(text("""
            SELECT DISTINCT industry, solution
            FROM materials
            WHERE active = 1
        """)).fetchall()

        industry_options = sorted({r.industry for r in rows if r.industry})
        solution_options = sorted({r.solution for r in rows if r.solution})

        return industry_options, solution_options
    except Exception as e:
        logger.error(f"Error fetching filter options: {e}")
        return [], []
    finally:
        if db:
            db.close()


def get_filter_options():
    """Get cached filter options for materials"""
    return _get_filter_options_cached(_filter_cache_key)


def list_materials(
    db: Session,
    industry: str = "all",
    solution: str = "all",
    rito: str = "all",
    tema: str = "all",
    categoria: str = "all",
    user_grade_level: int | None = None,
) -> list[dict]:
    """
    List all active materials with optional filtering
    """
    try:
        rows = db.execute(text("""
            SELECT id, title, filename, file_type, industry, solution, 
                   description, rito, grau_minimo, tema, categoria, sort_order, active
            FROM materials
            WHERE active = 1
            ORDER BY sort_order ASC, id ASC
        """)).fetchall()

        materials = []
        for r in rows:
            item = {
                "id": r.id,
                "slug": f"{r.id}",
                "title": r.title,
                "filename": r.filename,
                "type": (r.file_type or Path(r.filename).suffix.lower().lstrip(".")),
                "industry": r.industry,
                "solution": r.solution,
                "description": r.description,
                "rito": r.rito,
                "grau_minimo": int(getattr(r, "grau_minimo", 1) or 1),
                "tema": r.tema,
                "categoria": r.categoria,
                "sort_order": r.sort_order,
                "active": bool(r.active),
                "path": f"/materials/{r.filename}",
            }

            # Apply grade-based access control
            if user_grade_level is not None and item["grau_minimo"] > user_grade_level:
                continue

            # Apply filters
            if industry != "all" and item["industry"] != industry:
                continue
            if solution != "all" and item["solution"] != solution:
                continue
            if rito != "all" and item["rito"] != rito:
                continue
            if tema != "all" and item["tema"] != tema:
                continue
            if categoria != "all" and item["categoria"] != categoria:
                continue

            materials.append(item)

        return materials
    except Exception as e:
        logger.error(f"Error listing materials: {e}")
        return []


def get_material_by_id(db: Session, material_id: int) -> Optional[dict]:
    """
    Get a single material by ID
    """
    try:
        row = db.execute(text("""
            SELECT id, title, filename, file_type, industry, solution, 
                   description, rito, grau_minimo, tema, categoria, sort_order, active
            FROM materials
            WHERE id = :id AND active = 1
        """), {"id": material_id}).fetchone()

        if not row:
            return None

        return {
            "id": row.id,
            "slug": f"{row.id}",
            "title": row.title,
            "filename": row.filename,
            "type": (row.file_type or Path(row.filename).suffix.lower().lstrip(".")),
            "industry": row.industry,
            "solution": row.solution,
            "description": row.description,
            "rito": row.rito,
            "grau_minimo": int(getattr(row, "grau_minimo", 1) or 1),
            "tema": row.tema,
            "categoria": row.categoria,
            "sort_order": row.sort_order,
            "active": bool(row.active),
            "path": f"/materials/{row.filename}",
        }
    except Exception as e:
        logger.error(f"Error getting material {material_id}: {e}")
        return None


def get_material_by_filename(db: Session, filename: str) -> Optional[dict]:
    """
    Get a single material by filename
    """
    try:
        row = db.execute(text("""
            SELECT id, title, filename, file_type, industry, solution,
                   description, rito, grau_minimo, tema, categoria, sort_order, active
            FROM materials
            WHERE filename = :filename AND active = 1
        """), {"filename": filename}).fetchone()

        if not row:
            return None

        return {
            "id": row.id,
            "slug": f"{row.id}",
            "title": row.title,
            "filename": row.filename,
            "type": (row.file_type or Path(row.filename).suffix.lower().lstrip(".")),
            "industry": row.industry,
            "solution": row.solution,
            "description": row.description,
            "rito": row.rito,
            "grau_minimo": int(getattr(row, "grau_minimo", 1) or 1),
            "tema": row.tema,
            "categoria": row.categoria,
            "sort_order": row.sort_order,
            "active": bool(row.active),
            "path": f"/materials/{row.filename}",
        }
    except Exception as e:
        logger.error(f"Error getting material by filename {filename}: {e}")
        return None


def create_material(db: Session, title: str, filename: str, file_type: str,
                   industry: str, solution: str, description: str = "",
                   rito: str = "", grau_minimo: int = 1,
                   tema: str = "", categoria: str = "",
                   sort_order: int = 0) -> Optional[int]:
    """
    Create a new material
    Returns the new material ID or None on error
    """
    try:
        result = db.execute(text("""
            INSERT INTO materials 
            (title, filename, file_type, industry, solution, description, rito, grau_minimo, tema, categoria, sort_order, active)
            VALUES (:title, :filename, :file_type, :industry, :solution, :description, :rito, :grau_minimo, :tema, :categoria, :sort_order, 1)
        """), {
            "title": title,
            "filename": filename,
            "file_type": file_type,
            "industry": industry,
            "solution": solution,
            "description": description,
            "rito": rito,
            "grau_minimo": grau_minimo,
            "tema": tema,
            "categoria": categoria,
            "sort_order": sort_order
        })
        db.commit()
        
        invalidate_filter_cache()
        logger.info(f"Created material: {title} (ID: {result.lastrowid})")
        return result.lastrowid
    except Exception as e:
        logger.error(f"Error creating material {title}: {e}")
        db.rollback()
        return None


def update_material(db: Session, material_id: int, **kwargs) -> bool:
    """
    Update a material with provided fields
    """
    try:
        # Build dynamic update query
        fields = []
        params = {"id": material_id}
        
        allowed_fields = ["title", "filename", "file_type", "industry", 
                         "solution", "description", "rito", "grau_minimo", "tema", "categoria", "sort_order", "active"]
        
        for field in allowed_fields:
            if field in kwargs:
                fields.append(f"{field} = :{field}")
                params[field] = kwargs[field]
        
        if not fields:
            return True  # Nothing to update
        
        query = f"UPDATE materials SET {', '.join(fields)} WHERE id = :id"
        db.execute(text(query), params)
        db.commit()
        
        invalidate_filter_cache()
        logger.info(f"Updated material ID: {material_id}")
        return True
    except Exception as e:
        logger.error(f"Error updating material {material_id}: {e}")
        db.rollback()
        return False


def delete_material(db: Session, material_id: int, soft_delete: bool = True) -> bool:
    """
    Delete a material (soft delete by default)
    """
    try:
        if soft_delete:
            db.execute(text("""
                UPDATE materials SET active = 0 WHERE id = :id
            """), {"id": material_id})
        else:
            db.execute(text("""
                DELETE FROM materials WHERE id = :id
            """), {"id": material_id})
        
        db.commit()
        invalidate_filter_cache()
        logger.info(f"Deleted material ID: {material_id} (soft={soft_delete})")
        return True
    except Exception as e:
        logger.error(f"Error deleting material {material_id}: {e}")
        db.rollback()
        return False

# Made with Bob
