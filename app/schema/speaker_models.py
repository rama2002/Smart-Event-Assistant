from pydantic import BaseModel

class Speaker(BaseModel):
    speaker_id: int
    name: str
    
class SpeakerCreate(BaseModel):
    name: str
