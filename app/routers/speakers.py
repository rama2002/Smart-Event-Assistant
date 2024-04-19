from typing import List
from fastapi import APIRouter, HTTPException
from app.schema.speaker_models import Speaker, SpeakerCreate
from app.database.speaker_db import add_speaker, delete_speaker, get_all_speakers

router = APIRouter()

@router.post("/speakers/", response_model=Speaker)
async def create_speaker(speaker: SpeakerCreate):
    new_speaker_id = add_speaker(speaker.name)
    if new_speaker_id is None:
        raise HTTPException(status_code=400, detail="Failed to create speaker.")
    return {"speaker_id": new_speaker_id, "name": speaker.name}


@router.delete("/speakers/{speaker_id}")
async def remove_speaker(speaker_id: int):
    deleted_speaker_id = delete_speaker(speaker_id)
    if not deleted_speaker_id:
        raise HTTPException(status_code=404, detail="Speaker not found.")
    return {"message": f"Speaker with id {speaker_id} deleted successfully."}

@router.get("/speakers/", response_model=List[Speaker])
async def get_speakers():
    speakers = get_all_speakers()  
    if speakers:
        return speakers
    else:
        raise HTTPException(status_code=404, detail="No speakers found")

