import io
from fastapi import APIRouter, File, HTTPException, Query, Security, UploadFile
from fastapi.responses import StreamingResponse
from app.common.auth import get_current_admin_user, get_current_adminspeaker_user, get_current_attendee_user, get_current_speaker_user, get_current_user
from app.database.attachment_db import add_attachment, delete_attachment, fetch_attachments_for_event, get_attachment
from app.database.event_db import add_event, fetch_filtered_events, update_event, delete_event, enroll_in_event, unenroll_in_event
from app.schema.attachment_models import AttachmentInDB
from app.schema.event_models import Event, EventCreate, EventUpdate  
import logging
from datetime import date
from typing import Optional, List
from app.schema.user_models import User

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/events/", response_model=Event)
async def create_event_endpoint(event: EventCreate,current_user: User = Security(get_current_admin_user)):
    new_event = add_event(
        title=event.title,
        description=event.description,
        start_date=event.start_date,
        end_date=event.end_date,
        location=event.location,
        created_by=None 
    )
    if not new_event:
        raise HTTPException(status_code=400, detail="Could not create event.")
    
    logger.debug(f"New event data: {new_event}")
    
    event_id = new_event.get('event_id')
    logger.debug(f"Extracted event_id: {event_id}")
    if not isinstance(event_id, int):
        logger.error(f"Invalid event_id type: {type(event_id)}")
        raise HTTPException(status_code=500, detail="Invalid event ID.")
    
    new_event_response = Event(
        event_id=event_id,
        title=event.title,
        description=event.description,
        start_date=event.start_date,
        end_date=event.end_date,
        location=event.location
    )
    return new_event_response

@router.put("/events/{event_id}", response_model=Event)
async def update_event_endpoint(event_id: int, event: EventUpdate,current_user: User = Security(get_current_adminspeaker_user)):
    updated_event = update_event(
        event_id=event_id,
        title=event.title,
        description=event.description,
        start_date=event.start_date,
        end_date=event.end_date,
        location=event.location
    )
    if not updated_event:
        raise HTTPException(status_code=404, detail="Event not found.")
    
    if isinstance(updated_event, dict):
        return Event(**updated_event)
    else:
        raise HTTPException(status_code=500, detail="Failed to update event.")

@router.delete("/events/{event_id}", response_model=dict)
async def delete_event_endpoint(event_id: int,current_user: User = Security(get_current_admin_user)):
    deleted_event = delete_event(event_id)
    if not deleted_event:
        raise HTTPException(status_code=404, detail="Event not found.")
    return {"message": "Event deleted successfully"}


@router.post("/events/{event_id}/enroll", response_model=dict)
async def enroll_in_event_endpoint(event_id: int, current_user: User = Security(get_current_attendee_user)):
    enrollment = enroll_in_event(user_id=current_user.user_id, event_id=event_id)
    if not enrollment:
        raise HTTPException(status_code=400, detail="Could not enroll in event.")
    return {"message": "Enrollment successful"}

@router.delete("/events/{event_id}/unenroll", response_model=dict)
async def unenroll_in_event_endpoint(event_id: int, current_user: User = Security(get_current_attendee_user)):
    unenrollment = unenroll_in_event(user_id=current_user['user_id'], event_id=event_id)
    if not unenrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found or user is not enrolled in event.")
    return {"message": "Unenrollment successful"}


@router.get("/events/", response_model=List[Event])
async def get_events(
    interest_id: Optional[int] = Query(None, description="Filter by interest ID"),
    title: Optional[str] = Query(None, description="Filter by title"),
    location: Optional[str] = Query(None, description="Filter by location"),
    event_date: Optional[date] = Query(None, description="Filter by event date"),
    page_number: int = Query(1, description="Page number for pagination"),
    page_size: int = Query(10, description="Number of items per page"),
    current_user: User = Security(get_current_user)
):
    events = fetch_filtered_events(interest_id, title, location, event_date, page_number, page_size)
    if events:
        return events
    else:
        raise HTTPException(status_code=404, detail="No events found")
    
@router.post("/events/{event_id}/attachments")
async def upload_attachment(event_id: int, file: UploadFile = File(...), current_user: User = Security(get_current_adminspeaker_user)):
    file_content = await file.read()
    attachment = add_attachment(
        event_id=event_id,
        file_name=file.filename,
        mime_type=file.content_type,
        file_size=len(file_content),
        file_content=file_content
    )
    if attachment:
        return {"message": "File uploaded successfully", "attachment_id": attachment['attachment_id']}
    else:
        raise HTTPException(status_code=500, detail="File upload failed")
    
@router.get("/events/attachments/{attachment_id}")
async def view_attachment(attachment_id: int, current_user: User = Security(get_current_user)):
    attachment = get_attachment(attachment_id)
    if attachment:
        return StreamingResponse(io.BytesIO(attachment['file_content']), media_type=attachment['mime_type'])
    else:
        raise HTTPException(status_code=404, detail="Attachment not found")
    
    
@router.delete("/events/attachments/{attachment_id}")
async def remove_attachment(attachment_id: int, current_user: User = Security(get_current_adminspeaker_user)):
    result = delete_attachment(attachment_id)
    if result:
        return {"message": "Attachment deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Attachment not found")
    
    
@router.get("/events/{event_id}/attachments", response_model=List[AttachmentInDB])
async def list_event_attachments(event_id: int, current_user: User = Security(get_current_user)):
    attachments = fetch_attachments_for_event(event_id)
    if attachments:
        return attachments
    else:
        raise HTTPException(status_code=404, detail="No attachments found for this event")