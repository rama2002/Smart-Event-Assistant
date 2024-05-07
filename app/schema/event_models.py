from datetime import datetime
from pydantic import BaseModel, validator
from typing import Optional

class EventCreate(BaseModel):
    title: str
    description: str
    start_date: datetime
    end_date: datetime
    location: str

    @validator('end_date')
    def check_dates(cls, v, values, **kwargs):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


class EventUpdate(BaseModel):
    title: str = None
    description: str = None
    start_date: datetime = None
    end_date: datetime = None
    location: str = None

class Event(BaseModel):
    event_id: int
    title: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    location: str
    created_by: Optional[int] = None
    cover_attachment_id: Optional[int] = None

    class Config:
        orm_mode = True