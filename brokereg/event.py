from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class Event(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    event_version: int = 1
    event_domain: str
    event_name: str
    event_producer: str
    event_time: datetime = Field(default_factory=datetime.utcnow)
    content: BaseModel

