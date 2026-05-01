"""
Bulk Import Service - Import multiple materials from directory
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session

from pitch_app.services.config import MATERIALS_DIR


def scan_materials_directory() -> List[Dict]:
    """
    Scan materials directory and return list of files not yet in database
    
    Returns:
        List of dictionaries with file information
    """
    if not MATERIALS_DIR.exists():
        return []
    
    files = []
    for file_path in MATERIALS_DIR.iterdir():
        if file_path.is_file() and not file_path.name.startswith('.'):
            # Get file extension
            ext = file_path.suffix.lower().lstrip('.')
            
            # Skip non-media files
            if ext not in ['pdf', 'mp4', 'webm', 'mov', 'avi', 'mkv']:
                continue
            
            # Generate suggested title from filename
            title = generate_title_from_filename(file_path.stem)
            
            # Try to extract industry and solution from filename
            industry, solution = extract_metadata_from_filename(file_path.stem)
            
            files.append({
                'filename': file_path.name,
                'file_type': ext,
                'suggested_title': title,
                'suggested_industry': industry,
                'suggested_solution': solution,
                'file_size': file_path.stat().st_size,
                'file_size_mb': round(file_path.stat().st_size / (1024 * 1024), 2)
            })
    
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
    """
    Get set of filenames already in database
    
    Args:
        db: Database session
        
    Returns:
        Set of existing filenames
    """
    result = db.execute(text("SELECT filename FROM materials")).fetchall()
    return {row.filename for row in result}


def get_new_materials(db: Session) -> List[Dict]:
    """
    Get list of materials in directory that are not yet in database
    
    Args:
        db: Database session
        
    Returns:
        List of new materials with metadata
    """
    all_files = scan_materials_directory()
    existing = get_existing_filenames(db)
    
    new_files = [f for f in all_files if f['filename'] not in existing]
    
    return new_files


def bulk_import_materials(db: Session, materials: List[Dict]) -> Dict:
    """
    Import multiple materials into database
    
    Args:
        db: Database session
        materials: List of material dictionaries with keys:
            - filename (required)
            - title (required)
            - file_type (required)
            - industry (optional)
            - solution (optional)
            - description (optional)
            
    Returns:
        Dictionary with import results
    """
    imported = 0
    skipped = 0
    errors = []
    
    existing = get_existing_filenames(db)
    
    for material in materials:
        try:
            filename = material.get('filename')
            
            # Skip if already exists
            if filename in existing:
                skipped += 1
                continue
            
            # Validate required fields
            if not filename or not material.get('title'):
                errors.append(f"Missing required fields for {filename}")
                continue
            
            # Get next sort order
            result = db.execute(text("SELECT COALESCE(MAX(sort_order), 0) + 1 as next_order FROM materials")).fetchone()
            next_order = result.next_order if result else 1
            
            # Insert material
            db.execute(text("""
                INSERT INTO materials (
                    title, filename, file_type, industry, solution, 
                    description, sort_order, active
                ) VALUES (
                    :title, :filename, :file_type, :industry, :solution,
                    :description, :sort_order, 1
                )
            """), {
                'title': material.get('title'),
                'filename': filename,
                'file_type': material.get('file_type'),
                'industry': material.get('industry'),
                'solution': material.get('solution'),
                'description': material.get('description', ''),
                'sort_order': next_order
            })
            
            imported += 1
            
        except Exception as e:
            errors.append(f"Error importing {material.get('filename', 'unknown')}: {str(e)}")
    
    db.commit()
    
    return {
        'imported': imported,
        'skipped': skipped,
        'errors': errors,
        'total': len(materials)
    }

# Made with Bob
