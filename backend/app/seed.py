import json
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from .models import FAQ, Document, Project

async def seed_from_file(session: AsyncSession, seed_file: str = "seed_content.json") -> None:
    with open(seed_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Only seed if empty
    faq_count = await session.scalar(select(func.count()).select_from(FAQ))
    if faq_count and faq_count > 0:
        return

    for item in data.get("faq", []):
        session.add(FAQ(question=item["question"], answer=item["answer"]))

    for item in data.get("documents", []):
        session.add(Document(title=item["title"], path=item["path"]))

    for item in data.get("projects", []):
        session.add(Project(title=item["title"], description=item.get("description",""), image=item.get("image")))

    await session.commit()
