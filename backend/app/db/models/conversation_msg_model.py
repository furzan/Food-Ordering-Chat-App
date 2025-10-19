from typing import Dict, Any
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime
import uuid

class ConversationMessage(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    role: str
    content: Dict[str, Any] = Field(sa_column=Column(JSON))  # ✅ Correct way to use JSON
    conversation_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
