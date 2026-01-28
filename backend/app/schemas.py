from pydantic import BaseModel
from typing import Optional, List

class TGUser(BaseModel):
    id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class FAQOut(BaseModel):
    id: int
    question: str
    answer: str

class DocumentOut(BaseModel):
    id: int
    title: str
    url: str

class ProjectOut(BaseModel):
    id: int
    title: str
    description: str
    image: Optional[str] = None

class LeadCreate(BaseModel):
    lead_type: str
    name: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    work_type: Optional[str] = None
    budget: Optional[str] = None
    description: Optional[str] = None
    attachments: Optional[List[str]] = None  # Telegram file_id list

class LeadOut(BaseModel):
    id: int
    lead_type: str
    name: Optional[str]
    phone: Optional[str]
    city: Optional[str]
    work_type: Optional[str]
    budget: Optional[str]
    description: Optional[str]
    status: str
    created_at: str
    attachment_count: int

class LeadStatusUpdate(BaseModel):
    status: str
