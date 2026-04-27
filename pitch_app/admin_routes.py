from pathlib import Path
import shutil
import os

from fastapi import APIRouter, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import text
from openai import OpenAI

from pitch_app.db import SessionLocal
from pitch_app.services.material_processing_service import process_material_on_upload

router = APIRouter(prefix="/admin", tags=["admin"])

from pitch_app.services.config import MATERIALS_DIR

INDUSTRY_OPTIONS = ["Varejo", "Saúde", "Finanças", "Tecnologia", "Educação", "Indústria"]
SOLUTION_OPTIONS = ["Software", "Serviços", "Consultoria", "Hardware", "Plataforma"]


def _is_admin(request: Request):
    return bool(request.session.get("admin_logged_in"))


def _admin_only(request: Request):
    if not _is_admin(request):
        raise HTTPException(status_code=303, headers={"Location": "/admin/login"})


def _guess_type(filename: str) -> str:
    return Path(filename).suffix.lower().lstrip(".")


def _list_materials():
    db = SessionLocal()
    try:
        rows = db.execute(text("""
            SELECT id, title, filename, file_type, industry, solution, description,
                   sort_order, active, transcript_path, has_transcript, summary_path, has_ai_summary
            FROM materials
            ORDER BY sort_order ASC, id ASC
        """)).fetchall()

        return [
            {
                "id": r.id,
                "title": r.title,
                "filename": r.filename,
                "file_type": r.file_type,
                "industry": r.industry,
                "solution": r.solution,
                "description": r.description,
                "sort_order": r.sort_order,
                "active": bool(r.active),
                "transcript_path": getattr(r, "transcript_path", None),
                "has_transcript": bool(getattr(r, "has_transcript", 0)),
                "summary_path": getattr(r, "summary_path", None),
                "has_ai_summary": bool(getattr(r, "has_ai_summary", 0)),
            }
            for r in rows
        ]
    finally:
        db.close()


@router.get("/login", response_class=HTMLResponse)
def admin_login_form(request: Request):
    return request.app.state.templates.TemplateResponse(
        "admin_login.html",
        {"request": request, "error": None},
    )


@router.post("/login", response_class=HTMLResponse)
def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    import os

ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

if username == ADMIN_USER and password == ADMIN_PASSWORD:
        request.session["admin_logged_in"] = True
        return RedirectResponse(url="/admin/materials", status_code=303)

    return request.app.state.templates.TemplateResponse(
        "admin_login.html",
        {"request": request, "error": "Usuário ou senha inválidos"},
        status_code=401,
    )


@router.get("/logout")
def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/admin/login", status_code=303)


@router.get("/materials", response_class=HTMLResponse)
def admin_materials(request: Request):
    _admin_only(request)
    materials = _list_materials()

    return request.app.state.templates.TemplateResponse(
        "admin_materials.html",
        {"request": request, "materials": materials},
    )


@router.get("/materials/new", response_class=HTMLResponse)
def new_material_form(request: Request):
    _admin_only(request)
    return request.app.state.templates.TemplateResponse(
        "admin_material_form.html",
        {
            "request": request,
            "material": None,
            "industry_options": INDUSTRY_OPTIONS,
            "solution_options": SOLUTION_OPTIONS,
            "form_action": "/admin/materials/new",
        },
    )


@router.post("/materials/new")
async def create_material(
    request: Request,
    title: str = Form(...),
    industry: str = Form(...),
    solution: str = Form(...),
    description: str = Form(""),
    sort_order: int = Form(0),
    active: bool = Form(False),
    file: UploadFile = File(...),
):
    _admin_only(request)
    MATERIALS_DIR.mkdir(parents=True, exist_ok=True)

    filename = file.filename or ""
    if not filename:
        raise HTTPException(status_code=400, detail="Arquivo inválido")

    dest = MATERIALS_DIR / filename
    with dest.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    transcript_path = None
    has_transcript = 0
    summary_path = None
    has_ai_summary = 0

    try:
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if api_key:
            client = OpenAI(api_key=api_key)
            processing_result = process_material_on_upload(client, dest)

            transcript_path = processing_result.get("transcript_path")
            has_transcript = 1 if processing_result.get("has_transcript") else 0
            summary_path = processing_result.get("summary_path")
            has_ai_summary = 1 if processing_result.get("has_ai_summary") else 0
    except Exception as exc:
        print("⚠️ erro no processamento do material:", exc)

    db = SessionLocal()
    try:
        db.execute(text("""
            INSERT INTO materials
            (title, filename, file_type, industry, solution, description, sort_order, active,
             transcript_path, has_transcript, summary_path, has_ai_summary)
            VALUES (:title, :filename, :file_type, :industry, :solution, :description, :sort_order, :active,
                    :transcript_path, :has_transcript, :summary_path, :has_ai_summary)
        """), {
            "title": title.strip(),
            "filename": filename,
            "file_type": _guess_type(filename),
            "industry": industry.strip(),
            "solution": solution.strip(),
            "description": description.strip(),
            "sort_order": sort_order,
            "active": 1 if active else 0,
            "transcript_path": transcript_path,
            "has_transcript": has_transcript,
            "summary_path": summary_path,
            "has_ai_summary": has_ai_summary,
        })
        db.commit()
    finally:
        db.close()

    return RedirectResponse(url="/admin/materials", status_code=303)


@router.get("/materials/{material_id}/edit", response_class=HTMLResponse)
def edit_material_form(request: Request, material_id: int):
    _admin_only(request)
    db = SessionLocal()
    try:
        row = db.execute(text("""
            SELECT id, title, filename, file_type, industry, solution, description,
                   sort_order, active, transcript_path, has_transcript, summary_path, has_ai_summary
            FROM materials
            WHERE id = :id
        """), {"id": material_id}).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Material não encontrado")

        material = {
            "id": row.id,
            "title": row.title,
            "filename": row.filename,
            "file_type": row.file_type,
            "industry": row.industry,
            "solution": row.solution,
            "description": row.description,
            "sort_order": row.sort_order,
            "active": bool(row.active),
            "transcript_path": getattr(row, "transcript_path", None),
            "has_transcript": bool(getattr(row, "has_transcript", 0)),
            "summary_path": getattr(row, "summary_path", None),
            "has_ai_summary": bool(getattr(row, "has_ai_summary", 0)),
        }
    finally:
        db.close()

    return request.app.state.templates.TemplateResponse(
        "admin_material_form.html",
        {
            "request": request,
            "material": material,
            "industry_options": INDUSTRY_OPTIONS,
            "solution_options": SOLUTION_OPTIONS,
            "form_action": f"/admin/materials/{material_id}/edit",
        },
    )


@router.post("/materials/{material_id}/edit")
async def update_material(
    request: Request,
    material_id: int,
    title: str = Form(...),
    industry: str = Form(...),
    solution: str = Form(...),
    description: str = Form(""),
    sort_order: int = Form(0),
    active: bool = Form(False),
):
    _admin_only(request)
    db = SessionLocal()
    try:
        db.execute(text("""
            UPDATE materials
            SET title = :title,
                industry = :industry,
                solution = :solution,
                description = :description,
                sort_order = :sort_order,
                active = :active
            WHERE id = :id
        """), {
            "title": title.strip(),
            "industry": industry.strip(),
            "solution": solution.strip(),
            "description": description.strip(),
            "sort_order": sort_order,
            "active": 1 if active else 0,
            "id": material_id,
        })
        db.commit()
    finally:
        db.close()

    return RedirectResponse(url="/admin/materials", status_code=303)


@router.post("/materials/{material_id}/reprocess")
def reprocess_material(request: Request, material_id: int):
    _admin_only(request)

    db = SessionLocal()
    try:
        row = db.execute(text("""
            SELECT id, filename, file_type
            FROM materials
            WHERE id = :id
        """), {"id": material_id}).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Material não encontrado")

        file_path = MATERIALS_DIR / row.filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Arquivo físico do material não encontrado")

        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY não configurada")

        transcript_path = None
        has_transcript = 0
        summary_path = None
        has_ai_summary = 0

        try:
            client = OpenAI(api_key=api_key)
            processing_result = process_material_on_upload(client, file_path)

            transcript_path = processing_result.get("transcript_path")
            has_transcript = 1 if processing_result.get("has_transcript") else 0
            summary_path = processing_result.get("summary_path")
            has_ai_summary = 1 if processing_result.get("has_ai_summary") else 0
        except Exception as exc:
            print("⚠️ erro no reprocessamento do material:", exc)
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao reprocessar material: {exc}"
            ) from exc

        db.execute(text("""
            UPDATE materials
            SET transcript_path = :transcript_path,
                has_transcript = :has_transcript,
                summary_path = :summary_path,
                has_ai_summary = :has_ai_summary
            WHERE id = :id
        """), {
            "id": material_id,
            "transcript_path": transcript_path,
            "has_transcript": has_transcript,
            "summary_path": summary_path,
            "has_ai_summary": has_ai_summary,
        })
        db.commit()
    finally:
        db.close()

    return RedirectResponse(url="/admin/materials", status_code=303)


@router.post("/materials/{material_id}/delete")
def delete_material(request: Request, material_id: int):
    _admin_only(request)
    db = SessionLocal()
    try:
        row = db.execute(text("""
            SELECT filename, transcript_path, summary_path
            FROM materials
            WHERE id = :id
        """), {"id": material_id}).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Material não encontrado")

        path = MATERIALS_DIR / row.filename
        if path.exists():
            path.unlink()

        transcript_path = getattr(row, "transcript_path", None)
        if transcript_path:
            transcript_file = Path(transcript_path)
            if transcript_file.exists():
                transcript_file.unlink()

        summary_path = getattr(row, "summary_path", None)
        if summary_path:
            summary_file = Path(summary_path)
            if summary_file.exists():
                summary_file.unlink()

        db.execute(text("DELETE FROM materials WHERE id = :id"), {"id": material_id})
        db.commit()
    finally:
        db.close()

    return RedirectResponse(url="/admin/materials", status_code=303)