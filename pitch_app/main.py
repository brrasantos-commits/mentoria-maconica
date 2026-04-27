import os
from pathlib import Path

from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import text

from pitch_app.admin_routes import router as admin_router
from pitch_app.db import init_db, SessionLocal, migrate_db
from pitch_app.services.evaluation_service import evaluate_submission
from pitch_app.services.exceptions import AppError
from pitch_app.services.job_store import create_job, get_job, update_job

from pitch_app.services.config import (
    TEMPLATES_DIR,
    STATIC_DIR,
    MATERIALS_DIR,
    MAX_VIDEO_SIZE_MB,
)

STATIC_DIR.mkdir(parents=True, exist_ok=True)
MATERIALS_DIR.mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "css").mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Sales Pitch AI V4")

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", "fallback-secret"),
)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.state.templates = templates

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/materials", StaticFiles(directory=str(MATERIALS_DIR)), name="materials")

app.include_router(admin_router)

SESSION_MATERIALS_KEY = "selected_materials"
SESSION_USER_KEY = "user_logged"


@app.on_event("startup")
def on_startup():
    init_db()
    migrate_db()


def _is_user_logged(request: Request) -> bool:
    return bool(request.session.get(SESSION_USER_KEY))


def _login_redirect():
    return RedirectResponse(url="/login", status_code=303)


def _get_selected_materials(request: Request) -> list[str]:
    items = request.session.get(SESSION_MATERIALS_KEY, [])
    if not isinstance(items, list):
        return []

    cleaned = []
    seen = set()

    for item in items:
        if isinstance(item, str):
            value = item.strip()
            if value and value not in seen:
                seen.add(value)
                cleaned.append(value)

    return cleaned


def _set_selected_materials(request: Request, items: list[str]) -> list[str]:
    cleaned = []
    seen = set()

    for item in items:
        if isinstance(item, str):
            value = item.strip()
            if value and value not in seen:
                seen.add(value)
                cleaned.append(value)

    request.session[SESSION_MATERIALS_KEY] = cleaned
    return cleaned


def _add_selected_material(request: Request, filename: str) -> list[str]:
    current = _get_selected_materials(request)
    value = (filename or "").strip()

    if value and value not in current:
        current.append(value)

    return _set_selected_materials(request, current)


def _remove_selected_material(request: Request, filename: str) -> list[str]:
    value = (filename or "").strip()
    current = [item for item in _get_selected_materials(request) if item != value]
    return _set_selected_materials(request, current)


def _list_materials(industry: str = "all", solution: str = "all"):
    db = SessionLocal()
    try:
        rows = db.execute(text("""
            SELECT id, title, filename, file_type, industry, solution, description, sort_order, active
            FROM materials
            ORDER BY sort_order ASC, id ASC
        """)).fetchall()

        materials = []

        for r in rows:
            if not bool(r.active):
                continue

            item = {
                "id": r.id,
                "slug": f"{r.id}",
                "title": r.title,
                "filename": r.filename,
                "type": (r.file_type or Path(r.filename).suffix.lower().lstrip(".")),
                "industry": r.industry,
                "solution": r.solution,
                "description": r.description,
                "sort_order": r.sort_order,
                "active": bool(r.active),
                "path": f"/materials/{r.filename}",
            }

            if industry != "all" and item["industry"] != industry:
                continue

            if solution != "all" and item["solution"] != solution:
                continue

            materials.append(item)

        return materials
    finally:
        db.close()


def _filter_options():
    db = SessionLocal()
    try:
        rows = db.execute(text("""
            SELECT DISTINCT industry, solution
            FROM materials
            WHERE active = 1
        """)).fetchall()

        industry_options = sorted({r.industry for r in rows if r.industry})
        solution_options = sorted({r.solution for r in rows if r.solution})

        return industry_options, solution_options
    finally:
        db.close()


def _validate_video_upload(video: UploadFile):
    if not video or not video.filename:
        raise HTTPException(
            status_code=400,
            detail="Vídeo do pitch é obrigatório."
        )

    allowed_extensions = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
    ext = Path(video.filename).suffix.lower()

    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Formato de vídeo não suportado. Use MP4, MOV, AVI, MKV ou WEBM."
        )

    max_size_bytes = MAX_VIDEO_SIZE_MB * 1024 * 1024

    video.file.seek(0, 2)
    file_size = video.file.tell()
    video.file.seek(0)

    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"Arquivo muito grande. Máximo permitido: {MAX_VIDEO_SIZE_MB}MB."
        )


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    if _is_user_logged(request):
        return RedirectResponse(url="/estudo", status_code=303)
    return RedirectResponse(url="/login", status_code=303)


@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": None},
    )


@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    app_user = os.getenv("APP_USER", "user")
    app_password = os.getenv("APP_PASSWORD", "123456")

    if username == app_user and password == app_password:
        request.session[SESSION_USER_KEY] = True
        return RedirectResponse(url="/estudo", status_code=303)

    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Usuário ou senha inválidos"},
        status_code=401,
    )


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


@app.get("/estudo", response_class=HTMLResponse)
async def study_index(request: Request, industry: str = "all", solution: str = "all"):
    if not _is_user_logged(request):
        return _login_redirect()

    materials = _list_materials(industry=industry, solution=solution)
    industry_options, solution_options = _filter_options()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "materials": materials,
            "industry_options": industry_options,
            "solution_options": solution_options,
            "current_industry": industry,
            "current_solution": solution,
            "selected_materials": _get_selected_materials(request),
        },
    )


@app.get("/estudo/{material_id}", response_class=HTMLResponse)
async def study_material(request: Request, material_id: int):
    if not _is_user_logged(request):
        return _login_redirect()

    db = SessionLocal()

    try:
        row = db.execute(text("""
            SELECT id, title, filename, file_type, industry, solution, description, sort_order, active
            FROM materials
            WHERE id = :id AND active = 1
        """), {"id": material_id}).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Material não encontrado")

        material = {
            "id": row.id,
            "slug": f"{row.id}",
            "title": row.title,
            "filename": row.filename,
            "type": (row.file_type or Path(row.filename).suffix.lower().lstrip(".")),
            "industry": row.industry,
            "solution": row.solution,
            "description": row.description,
            "sort_order": row.sort_order,
            "active": bool(row.active),
            "path": f"/materials/{row.filename}",
        }
    finally:
        db.close()

    _add_selected_material(request, material["filename"])

    return templates.TemplateResponse(
        "study_material.html",
        {
            "request": request,
            "material": material,
            "selected_materials": _get_selected_materials(request),
        },
    )


@app.post("/estudo/concluir")
async def study_complete(request: Request):
    if not _is_user_logged(request):
        return _login_redirect()

    return RedirectResponse(url="/pitch", status_code=303)


@app.get("/pitch", response_class=HTMLResponse)
async def pitch_form(request: Request):
    if not _is_user_logged(request):
        return _login_redirect()

    materials = _list_materials()
    industry_options, solution_options = _filter_options()

    return templates.TemplateResponse(
        "pitch_form.html",
        {
            "request": request,
            "materials": materials,
            "industry_options": industry_options,
            "solution_options": solution_options,
            "selected_materials": _get_selected_materials(request),
        },
    )


@app.get("/api/session/materials")
async def session_materials(request: Request):
    if not _is_user_logged(request):
        return JSONResponse(status_code=401, content={"detail": "Usuário não autenticado"})

    return JSONResponse({"materials": _get_selected_materials(request)})


@app.post("/api/session/materials/add")
async def session_material_add(request: Request):
    if not _is_user_logged(request):
        return JSONResponse(status_code=401, content={"detail": "Usuário não autenticado"})

    data = await request.json()
    filename = (data.get("filename") or "").strip()

    if not filename:
        return JSONResponse(status_code=400, content={"detail": "filename obrigatório"})

    materials = _add_selected_material(request, filename)
    return JSONResponse({"materials": materials})


@app.post("/api/session/materials/remove")
async def session_material_remove(request: Request):
    if not _is_user_logged(request):
        return JSONResponse(status_code=401, content={"detail": "Usuário não autenticado"})

    data = await request.json()
    filename = (data.get("filename") or "").strip()

    if not filename:
        return JSONResponse(status_code=400, content={"detail": "filename obrigatório"})

    materials = _remove_selected_material(request, filename)
    return JSONResponse({"materials": materials})


@app.post("/api/session/materials/set")
async def session_material_set(request: Request):
    if not _is_user_logged(request):
        return JSONResponse(status_code=401, content={"detail": "Usuário não autenticado"})

    data = await request.json()
    items = data.get("materials", [])

    if not isinstance(items, list):
        return JSONResponse(status_code=400, content={"detail": "materials deve ser lista"})

    materials = _set_selected_materials(request, items)
    return JSONResponse({"materials": materials})


@app.post("/api/session/materials/clear")
async def session_material_clear(request: Request):
    if not _is_user_logged(request):
        return JSONResponse(status_code=401, content={"detail": "Usuário não autenticado"})

    request.session[SESSION_MATERIALS_KEY] = []
    return JSONResponse({"materials": []})


@app.get("/api/jobs/{job_id}")
async def job_status(job_id: str):
    job = get_job(job_id)

    if not job:
        return JSONResponse(status_code=404, content={"detail": "Job não encontrado"})

    return JSONResponse(content=job)


@app.post("/analyze", response_class=HTMLResponse)
async def analyze(
    request: Request,
    seller_name: str = Form(...),
    video: UploadFile = File(...),
    materials: list[str] = Form(...),
):
    if not _is_user_logged(request):
        return _login_redirect()

    _validate_video_upload(video)

    job_id = create_job(
        seller_name=(seller_name or "").strip(),
        video_name=video.filename or "",
    )

    try:
        result = evaluate_submission(
            job_id=job_id,
            seller_name=seller_name,
            video=video,
            materials=materials,
        )

        return templates.TemplateResponse(
            "result.html",
            {"request": request, **result}
        )

    except AppError as exc:
        update_job(
            job_id,
            stage="error",
            progress=100,
            message=exc.message,
            status="error",
        )
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    except Exception:
        update_job(
            job_id,
            stage="error",
            progress=100,
            message="Erro interno ao analisar o pitch.",
            status="error",
        )
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao analisar o pitch. Tente novamente."
        )