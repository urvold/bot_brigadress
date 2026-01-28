from fastapi import FastAPI, Depends, Header, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import csv
import io

from .db import engine, Base, get_session
from .config import settings
from .telegram_auth import get_user_from_init_data, TelegramAuthError
from . import crud
from .schemas import FAQOut, DocumentOut, ProjectOut, LeadCreate, LeadOut, LeadStatusUpdate
from .models import Lead
from .seed import seed_from_file

app = FastAPI(title="BrigAdress Showcase API", version="1.0.0")

# CORS (для локальной разработки)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # seed content from file
    async with get_session().__anext__() as session:
        await seed_from_file(session, "seed_content.json")

# Serve static site and webapp
app.mount("/site", StaticFiles(directory="static/site", html=True), name="site")
app.mount("/webapp", StaticFiles(directory="static/webapp", html=True), name="webapp")

@app.get("/api/health")
async def health():
    return {"ok": True}

def _require_init_data(init_data: Optional[str]) -> dict:
    if not init_data:
        raise HTTPException(status_code=401, detail="Missing Telegram initData")
    try:
        user = get_user_from_init_data(init_data)
    except TelegramAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    if not user:
        raise HTTPException(status_code=401, detail="No user in initData")
    return user

def _is_admin(tg_id: int) -> bool:
    return tg_id in settings.admin_ids

@app.get("/api/content/faq", response_model=list[FAQOut])
async def api_faq(session: AsyncSession = Depends(get_session)):
    items = await crud.get_faq(session)
    return [{"id": i.id, "question": i.question, "answer": i.answer} for i in items]

@app.get("/api/content/documents", response_model=list[DocumentOut])
async def api_docs(session: AsyncSession = Depends(get_session)):
    items = await crud.get_documents(session)
    return [{"id": i.id, "title": i.title, "url": f"/site/{i.path}"} for i in items]

@app.get("/api/content/projects", response_model=list[ProjectOut])
async def api_projects(session: AsyncSession = Depends(get_session)):
    items = await crud.get_projects(session)
    return [{"id": i.id, "title": i.title, "description": i.description, "image": i.image} for i in items]

@app.post("/api/leads", response_model=LeadOut)
async def create_lead(
    payload: LeadCreate,
    session: AsyncSession = Depends(get_session),
    x_telegram_init_data: Optional[str] = Header(default=None, alias="X-Telegram-Init-Data"),
):
    tg_user = _require_init_data(x_telegram_init_data)
    user = await crud.upsert_user(session, tg_user)
    lead = await crud.create_lead(session, payload.model_dump(), user=user)
    return {
        "id": lead.id,
        "lead_type": lead.lead_type,
        "name": lead.name,
        "phone": lead.phone,
        "city": lead.city,
        "work_type": lead.work_type,
        "budget": lead.budget,
        "description": lead.description,
        "status": lead.status,
        "created_at": lead.created_at.isoformat(),
        "attachment_count": len(lead.attachments),

    }
@app.post("/api/bot/leads", response_model=LeadOut)
async def create_lead_from_bot(
    payload: LeadCreate,
    session: AsyncSession = Depends(get_session),
    x_bot_token: Optional[str] = Header(default=None, alias="X-Bot-Token"),
):
    # For internal bot service: authenticate by BOT_TOKEN (same token).
    if not x_bot_token or x_bot_token != settings.bot_token:
        raise HTTPException(status_code=401, detail="Bad bot token")
    # no tg initData here; create/update user by telegram_id if provided via payload.description? not.
    # Bot will include telegram user fields inside description; still store lead without user link.
    lead = await crud.create_lead(session, payload.model_dump(), user=None)
    return {
        "id": lead.id,
        "lead_type": lead.lead_type,
        "name": lead.name,
        "phone": lead.phone,
        "city": lead.city,
        "work_type": lead.work_type,
        "budget": lead.budget,
        "description": lead.description,
        "status": lead.status,
        "created_at": lead.created_at.isoformat(),
        "attachment_count": len(lead.attachments),
    }

@app.get("/api/admin/leads", response_model=list[LeadOut])
async def admin_list_leads(
    session: AsyncSession = Depends(get_session),
    x_telegram_init_data: Optional[str] = Header(default=None, alias="X-Telegram-Init-Data"),
    limit: int = 200,
):
    tg_user = _require_init_data(x_telegram_init_data)
    if not _is_admin(int(tg_user["id"])):
        raise HTTPException(status_code=403, detail="Admin only")
    leads = await crud.list_leads(session, limit=limit)
    return [{
        "id": l.id,
        "lead_type": l.lead_type,
        "name": l.name,
        "phone": l.phone,
        "city": l.city,
        "work_type": l.work_type,
        "budget": l.budget,
        "description": l.description,
        "status": l.status,
        "created_at": l.created_at.isoformat(),
        "attachment_count": len(l.attachments),
    } for l in leads]

@app.patch("/api/admin/leads/{lead_id}", response_model=LeadOut)
async def admin_update_lead_status(
    lead_id: int,
    payload: LeadStatusUpdate,
    session: AsyncSession = Depends(get_session),
    x_telegram_init_data: Optional[str] = Header(default=None, alias="X-Telegram-Init-Data"),
):
    tg_user = _require_init_data(x_telegram_init_data)
    if not _is_admin(int(tg_user["id"])):
        raise HTTPException(status_code=403, detail="Admin only")

    res = await session.execute(select(Lead).where(Lead.id == lead_id))
    lead = res.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    lead.status = payload.status
    await session.commit()
    await session.refresh(lead)

    return {
        "id": lead.id,
        "lead_type": lead.lead_type,
        "name": lead.name,
        "phone": lead.phone,
        "city": lead.city,
        "work_type": lead.work_type,
        "budget": lead.budget,
        "description": lead.description,
        "status": lead.status,
        "created_at": lead.created_at.isoformat(),
        "attachment_count": len(lead.attachments),
    }

@app.get("/api/admin/export/leads.csv")
async def admin_export_leads_csv(
    session: AsyncSession = Depends(get_session),
    x_telegram_init_data: Optional[str] = Header(default=None, alias="X-Telegram-Init-Data"),
):
    tg_user = _require_init_data(x_telegram_init_data)
    if not _is_admin(int(tg_user["id"])):
        raise HTTPException(status_code=403, detail="Admin only")

    leads = await crud.list_leads(session, limit=5000)
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["id","lead_type","name","phone","city","work_type","budget","status","created_at","description"])
    for l in leads:
        writer.writerow([l.id,l.lead_type,l.name,l.phone,l.city,l.work_type,l.budget,l.status,l.created_at.isoformat(), (l.description or "").replace("\n"," ")])
    return Response(content=out.getvalue(), media_type="text/csv; charset=utf-8")
