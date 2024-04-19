from fastapi import APIRouter, HTTPException
from app.schema.interests_models import InterestCreate, InterestUpdate
from app.database.interest_db import add_interest, delete_interest, update_interest

router = APIRouter()

@router.post("/interests/", response_model=int)
async def create_interest(interest: InterestCreate):
    interest_id = add_interest(interest.name)
    if interest_id:
        return interest_id
    else:
        raise HTTPException(status_code=500, detail="Failed to create interest")

@router.delete("/interests/{interest_id}")
async def delete_interest_by_id(interest_id: int):
    deleted_count = delete_interest(interest_id)
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Interest not found")
    return {"message": "Interest deleted successfully"}

@router.put("/interests/{interest_id}", response_model=dict)
async def update_interest_by_id(interest_id: int, interest_update: InterestUpdate):
    updated_row = update_interest(interest_id, interest_update.name)
    if updated_row:
        return {"message": "Interest updated successfully", "interest": updated_row}
    else:
        raise HTTPException(status_code=404, detail="Interest not found")

