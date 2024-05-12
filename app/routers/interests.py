from fastapi import APIRouter, HTTPException, Security
from app.common.auth import get_current_admin_user, get_current_user
from app.schema.interests_models import InterestCreate, InterestUpdate
from app.database.interest_db import add_interest, delete_interest, update_interest, get_all_interests
from app.schema.user_models import User

router = APIRouter()

@router.post("/interests/", response_model=int)
async def create_interest(interest: InterestCreate,current_user: User = Security(get_current_admin_user)):
    interest_id = add_interest(interest.name)
    if interest_id:
        return interest_id
    else:
        raise HTTPException(status_code=500, detail="Failed to create interest")

@router.delete("/interests/{interest_id}")
async def delete_interest_by_id(interest_id: int,current_user: User = Security(get_current_admin_user)):
    deleted_count = delete_interest(interest_id)
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Interest not found")
    return {"message": "Interest deleted successfully"}

@router.put("/interests/{interest_id}", response_model=dict)
async def update_interest_by_id(interest_id: int, interest_update: InterestUpdate,current_user: User = Security(get_current_admin_user)):
    updated_row = update_interest(interest_id, interest_update.name)
    if updated_row:
        return {"message": "Interest updated successfully", "interest": updated_row}
    else:
        raise HTTPException(status_code=404, detail="Interest not found")
    
@router.get("/interests/")
async def list_all_interests():
    interests = get_all_interests()
    if not interests:
        raise HTTPException(status_code=404, detail="No interests found")
    return interests

