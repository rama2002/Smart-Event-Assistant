
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class EventAttendance(BaseModel):
    title: str
    attendee_count: int

class MonthlySignups(BaseModel):
    month: datetime
    signups: int

