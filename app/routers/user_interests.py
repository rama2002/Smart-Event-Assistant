from fastapi import APIRouter, HTTPException, Path, Query, Security
from typing import List

from app.common.auth import get_current_attendee_user
from app.schema import user_interest_models
from app.database.interest_db import add_user_interest, delete_user_interest, get_user_interests
from app.schema.user_models import User

router = APIRouter()

@router.post("/users/{user_id}/interests/{interest_id}", response_model=dict)
async def add_interest_for_user(
    user_id: int = Path(..., description="The ID of the user"),
    interest_id: int = Path(..., description="The ID of the interest"),
    current_user: User = Security(get_current_attendee_user)
):
    success = add_user_interest(user_id, interest_id)
    if success:
        return {"message": "Interest added successfully for user."}
    else:
        raise HTTPException(status_code=400, detail="Failed to add interest for user.")
    
@router.delete("/users/{user_id}/interests/{interest_id}", response_model=dict)
async def remove_interest_for_user(
    user_id: int = Path(..., description="The ID of the user"),
    interest_id: int = Path(..., description="The ID of the interest"),
    current_user: User = Security(get_current_attendee_user)
):
    success = delete_user_interest(user_id, interest_id)
    if success:
        return {"message": f"Interest with id {interest_id} removed for user with id {user_id}."}
    else:
        raise HTTPException(status_code=404, detail="Interest not found or could not be removed.")

@router.get("/users/{user_id}/interests/", response_model=List[int])
async def list_interests_for_user(
    user_id: int = Path(..., description="The ID of the user"),
    current_user: User = Security(get_current_attendee_user)
):
    interests = get_user_interests(user_id)
    return interests
