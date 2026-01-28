from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User, Lead, LeadAttachment, FAQ, Document, Project

async def upsert_user(session: AsyncSession, tg_user: dict) -> User:
    telegram_id = int(tg_user["id"])
    res = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = res.scalar_one_or_none()
    if user:
        user.username = tg_user.get("username")
        user.first_name = tg_user.get("first_name")
        user.last_name = tg_user.get("last_name")
    else:
        user = User(
            telegram_id=telegram_id,
            username=tg_user.get("username"),
            first_name=tg_user.get("first_name"),
            last_name=tg_user.get("last_name"),
        )
        session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

async def create_lead(session: AsyncSession, lead_data: dict, user: User | None = None) -> Lead:
    lead = Lead(
        user_id=user.id if user else None,
        lead_type=lead_data["lead_type"],
        name=lead_data.get("name"),
        phone=lead_data.get("phone"),
        city=lead_data.get("city"),
        work_type=lead_data.get("work_type"),
        budget=lead_data.get("budget"),
        description=lead_data.get("description"),
        status="new",
    )
    session.add(lead)
    await session.flush()

    for file_id in (lead_data.get("attachments") or []):
        session.add(LeadAttachment(lead_id=lead.id, file_id=file_id, file_type="photo"))

    await session.commit()
    await session.refresh(lead)
    return lead

async def list_leads(session: AsyncSession, limit: int = 200) -> list[Lead]:
    res = await session.execute(select(Lead).order_by(desc(Lead.created_at)).limit(limit))
    return list(res.scalars().all())

async def get_faq(session: AsyncSession) -> list[FAQ]:
    res = await session.execute(select(FAQ).order_by(FAQ.id.asc()))
    return list(res.scalars().all())

async def get_documents(session: AsyncSession) -> list[Document]:
    res = await session.execute(select(Document).order_by(Document.id.asc()))
    return list(res.scalars().all())

async def get_projects(session: AsyncSession) -> list[Project]:
    res = await session.execute(select(Project).order_by(Project.id.asc()))
    return list(res.scalars().all())
