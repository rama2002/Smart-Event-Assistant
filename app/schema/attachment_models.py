from pydantic import BaseModel
from datetime import datetime

class AttachmentBase(BaseModel):
    event_id: int
    file_name: str
    mime_type: str
    file_size: int

class AttachmentCreate(AttachmentBase):
    pass

class AttachmentInDB(AttachmentBase):
    attachment_id: int
    uploaded_on: datetime

    class Config:
        orm_mode = True
