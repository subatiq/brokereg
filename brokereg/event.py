from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class EventData(BaseModel):
    pass


class Event(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    version: int = 1
    domain: str
    name: str
    producer: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    body: EventData

